import os
import json
import re
import logging
from z3 import *
from pathlib import Path
from tqdm import tqdm
import sys
sys.path.append(str(Path(__file__).parent.parent))

os.environ['GRPC_VERBOSITY'] = 'ERROR'
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

from engine import ApiKeyManager, make_api_call

PROJECT_ROOT = Path(__file__).parent.parent.parent

# --- CONFIGURAÇÃO DA ETAPA 5 ---
MODEL_NAME = 'gemini-2.5-pro'
INPUT_FILE = PROJECT_ROOT / 'artifacts' / 'stage_2b_naturalized_contexts.jsonl'
OUTPUT_BASE = PROJECT_ROOT / 'output' / 'z3_evaluation'
# ------------------------------------

def load_jsonl(file_path):
    if not file_path.exists():
        raise FileNotFoundError(f"Arquivo '{file_path}' não encontrado")

    with open(file_path, 'r', encoding='utf-8') as f:
        return [json.loads(line) for line in f]

def parse_expr(expr_str, vars_map):
    # Analisa uma pequena linguagem de expressões produzida pela LLM e converte em expressões Z3.

    expr_str = expr_str.strip()

    # Tenta identificar uma variável simples (Atômica)
    if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", expr_str):
        name = expr_str
        if name not in vars_map:
            vars_map[name] = Bool(name)
        return vars_map[name]

    # Tenta identificar uma função com argumentos (Ex: Not, Implies, Or e And)
    m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\((.*)\)$", expr_str)
    if not m:
        raise ValueError(f"Erro ao analisar expressão: {expr_str}")
    func = m.group(1)
    args_text = m.group(2).strip()

    # Processa argumentos respeitando parênteses aninhados [Ex: Not(Implies(p,r))]
    args = []
    depth = 0
    current = ''
    for ch in args_text:
        if ch == ',' and depth == 0:
            args.append(current.strip())
            current = ''
            continue
        current += ch
        if ch == '(':
            depth += 1
        elif ch == ')':
            depth -= 1
    if current.strip():
        args.append(current.strip())

    parsed_args = [parse_expr(a, vars_map) for a in args if a != '']

    # Converte para operadores Z3
    if func == 'Not':
        return Not(parsed_args[0])
    if func == 'Implies':
        return Implies(parsed_args[0], parsed_args[1])
    if func == 'Or':
        return Or(*parsed_args)
    if func == 'And':
        return And(*parsed_args)

def create_z3_solver_from_llm(context, key_manager, model_name=None):
    # Pede pra llm restrições Z3 da situação-problema.

    rule = context['rule']
    sentence_bank = context.get('sentence_bank', {})

    prompt = (
        "Converta o exemplo lógico abaixo em uma lista de restrições. "
        "Retorne SOMENTE um objeto JSON sem nenhum texto adicional antes ou depois, usando exatamente este formato: "
        "{\"variables\": [\"p\", \"q\"], \"constraints\": [\"Implies(p,q)\", \"Not(q)\"]}. "
        "As restrições devem usar apenas estas funções: Implies, Not, Or, And. "
        "Os nomes de variáveis devem ser simples (uma letra ou palavra). "
        f"Regra: {rule}. "
        f"Banco de sentenças: {json.dumps(sentence_bank, ensure_ascii=False)}. "
        "IMPORTANTE: 1. Não adicione explicações ou texto extra; 2. Não use formatação markdown; 3. A resposta deve começar com { e terminar com }; 4. Não quebre as linhas do JSON"
    )

    if key_manager is None:
        raise Exception("Key manager é necessário")

    if model_name is None:
        model_name = MODEL_NAME

    try:
        response_text = make_api_call(key_manager, model_name, prompt, call_purpose=f"ToZ3 ({rule})")
    except Exception as e:
        raise Exception(f"Erro na chamada da LLM: {e}")

    if not response_text:
        raise Exception("LLM retornou resposta vazia")

    try:
        # Retira { } se precisar
        try:
            data = json.loads(response_text)
        except Exception:
            first_brace = response_text.find('{')
            last_brace = response_text.rfind('}')
            if first_brace == -1 or last_brace == -1 or last_brace <= first_brace:
                raise
            json_text = response_text[first_brace:last_brace+1]
            data = json.loads(json_text)

        variables = data.get('variables', [])
        constraints = data.get('constraints', [])

        # resolvendo com o Z3
        vars_map = {}
        solver = Solver()
        for c in constraints:
            expr = parse_expr(str(c).strip(), vars_map)
            solver.add(expr)
        return solver, 'llm_success'
    except Exception as e:
        raise Exception(f"Erro ao analisar resposta da LLM: {e}")

def evaluate_context(context, key_manager):

    # Retorna o resultado da avaliação Z3

    solver, status = create_z3_solver_from_llm(context, key_manager)

    if solver is None:
        raise Exception(f"Falha ao criar solver usando LLM: {status}")

    result = solver.check()
    model = None
    
    if result == sat:
        model = solver.model()
        model_str = {str(d): str(model[d]) for d in model.decls()}
    else:
        model_str = None
    
    evaluation = {
        'rule': context['rule'],
        'natural_context': context['natural_context'],
        'sentence_bank': context['sentence_bank'],
        'solver_result': str(result),
        'model': model_str
    }
    
    return evaluation

def main():
    try:
        key_manager = ApiKeyManager()
    except Exception as e:
        print(f"CRÍTICO: Falha ao iniciar o gerenciador de chaves. Erro: {e}")
        return
    
    input_file = INPUT_FILE
    output_dir = OUTPUT_BASE

    os.makedirs(output_dir, exist_ok=True)
    
    try:
        contexts = load_jsonl(input_file)
    except Exception as e:
        print(f"Erro ao carregar arquivo de entrada: {e}")
        return
    
    # Organiza contextos por regra
    contexts_by_rule = {}
    for context in contexts:
        rule = context['rule']
        if rule not in contexts_by_rule:
            contexts_by_rule[rule] = []
        contexts_by_rule[rule].append(context)

    # Processa cada regra
    for rule, context_list in contexts_by_rule.items():
        rule_name = rule.split('/')[1]  # Extrai nome da regra
        rule_dir = output_dir / rule_name
        os.makedirs(rule_dir, exist_ok=True)
        
        evaluation_results = []
        
        try:
            for context in tqdm(context_list, desc=f"Avaliando {rule_name}"):
                try:
                    result = evaluate_context(context, key_manager)
                    evaluation_results.append(result)
                except Exception as e:
                    print(f"Erro ao avaliar contexto para {rule_name}: {e}")
                    continue
            
            results_file = rule_dir / 'data_instances.json'
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(evaluation_results, f, indent=2, ensure_ascii=False)
            logging.info(f"Resultados salvos em: {results_file}")
        
        except Exception as e:
            print(f"Erro ao processar regra {rule_name}: {e}")
            continue

if __name__ == '__main__':
    main()
# model_evaluation/1_evaluate_z3.py
import os
import json
import re
import logging
from z3 import *
from pathlib import Path
from tqdm import tqdm
import pandas as pd
import sys

PROJECT_ROOT = Path(__file__).parent.parent
DATASET_GENERATION_SRC_PATH = PROJECT_ROOT / 'dataset_generation' / 'src'
sys.path.append(str(DATASET_GENERATION_SRC_PATH))

os.environ['GRPC_VERBOSITY'] = 'ERROR'
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

from engine import ApiKeyManager, make_api_call

# --- CONFIGURAÇÃO DA AVALIAÇÃO Z3 ---
MODELS_TO_TEST = ['gemini-2.5-pro', 'gemini-2.5-flash']
EVALUATION_FILE = PROJECT_ROOT / "model_evaluation" / "dataframes" / "evaluation_spreadsheet.xlsx"
RAW_RESULTS_DIR = PROJECT_ROOT / "model_evaluation" / "z3_raw_results"
# ------------------------------------

def parse_expr(expr_str, vars_map):
    if not isinstance(expr_str, str): return BoolVal(True)
    expr_str = expr_str.strip()
    if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", expr_str):
        name = expr_str
        if name not in vars_map: vars_map[name] = Bool(name)
        return vars_map[name]
    m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\((.*)\)$", expr_str)
    if not m: raise ValueError(f"Erro ao analisar expressão: {expr_str}")
    func, args_text = m.group(1), m.group(2).strip()
    args, depth, current = [], 0, ''
    for ch in args_text:
        if ch == ',' and depth == 0:
            args.append(current.strip()); current = ''
            continue
        current += ch
        if ch == '(': depth += 1
        elif ch == ')': depth -= 1
    if current.strip(): args.append(current.strip())
    parsed_args = [parse_expr(a, vars_map) for a in args if a != '']
    if func == 'Not': return Not(parsed_args[0])
    if func == 'Implies': return Implies(parsed_args[0], parsed_args[1])
    if func == 'Or': return Or(*parsed_args)
    if func == 'And': return And(*parsed_args)
    raise ValueError(f"Função desconhecida: {func}")

def get_llm_formalization_from_text(context, model_name, key_manager):
    prompt = f"""Leia o contexto em linguagem natural abaixo. Identifique as premissas e a conclusão lógica implícita.
Traduza-as para um objeto JSON, usando variáveis de uma letra (p, q, r, s).
Use apenas as funções: Implies, Not, Or, And.

Contexto:
"{context['natural_context']}"

Retorne SOMENTE o objeto JSON, com o formato: {{"variables": ["p", "q"], "premises": ["Implies(p,q)", "Not(q)"], "conclusion": "Not(p)"}}.
JSON:"""
    response_text = make_api_call(key_manager, model_name, prompt, call_purpose=f"TextToZ3 ({context['rule']})")
    if not response_text: raise Exception("LLM retornou resposta vazia")
    try:
        match = re.search(r'\{.*\}', response_text, re.DOTALL)
        json_str = match.group(0) if match else response_text
        return json.loads(json_str)
    except (json.JSONDecodeError, AttributeError) as e:
        raise Exception(f"Erro ao analisar resposta da LLM: {e}")

def evaluate_z3_consequence(formalization_dict):
    try:
        solver = Solver()
        vars_map = {}
        for p_str in formalization_dict.get('premises', []):
            expr = parse_expr(p_str, vars_map)
            solver.add(expr)
        conclusion_expr = parse_expr(formalization_dict.get('conclusion', 'True'), vars_map)
        solver.add(Not(conclusion_expr))
        result = solver.check()
        is_consequence = (result == unsat)
        return {
            "z3_result_of_negation": str(result),
            "is_consequence_logic": is_consequence
        }
    except Exception as e:
        return {
            "z3_result_of_negation": f"Z3_ERROR: {e}",
            "is_consequence_logic": False
        }


def main():
    try:
        key_manager = ApiKeyManager()
    except Exception as e:
        print(f"CRÍTICO: Falha ao iniciar o gerenciador de chaves. Erro: {e}"); exit()

    try:
        df_tasks = pd.read_excel(EVALUATION_FILE, sheet_name="Z3_Evaluation")
        print(f"Planilha 'Z3_Evaluation' carregada com {len(df_tasks)} tarefas.")
    except (FileNotFoundError, ValueError) as e:
        print(f"ERRO: Não foi possível ler a aba 'Z3_Evaluation' do arquivo '{EVALUATION_FILE.name}'.")
        print("Por favor, execute o script 'generate_z3_sheet_template.py' primeiro.")
        exit()

    os.makedirs(RAW_RESULTS_DIR, exist_ok=True)

    # --- ETAPA 1: COLETA DE DADOS (RESUMÍVEL) ---
    for model_name in MODELS_TO_TEST:
        print(f"\n--- Iniciando coleta de dados para o modelo: {model_name} ---")
        output_jsonl_path = RAW_RESULTS_DIR / f"z3_results_{model_name.replace('-', '_')}.jsonl"
        
        completed_tasks = set()
        if output_jsonl_path.exists():
            with open(output_jsonl_path, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        completed_tasks.add(json.loads(line)['sample_id'])
                    except (json.JSONDecodeError, KeyError):
                        continue
        
        print(f"{len(completed_tasks)} tarefas já concluídas para {model_name}. Pulando.")

        with open(output_jsonl_path, 'a', encoding='utf-8') as f_out:
            tasks_to_run = df_tasks[~df_tasks['sample_id'].isin(completed_tasks)]
            
            for index, row in tqdm(tasks_to_run.iterrows(), total=len(tasks_to_run), desc=f"Avaliando {model_name}"):
                prompt = row['full_prompt']
                response_text = make_api_call(key_manager, model_name, prompt, call_purpose=f"ToZ3 ({row['rule']})")
                
                if not response_text:
                    response_text = "API_ERROR"
                
                result_data = {
                    "sample_id": row['sample_id'],
                    "llm_formalization": response_text
                }
                f_out.write(json.dumps(result_data, ensure_ascii=False) + '\n')

    print("\n--- COLETA DE DADOS CONCLUÍDA PARA TODOS OS MODELOS ---")

    # --- ETAPA 2: CONSOLIDAÇÃO E INCLUSÃO NA PLANILHA ---
    print("\nIniciando consolidação dos resultados na planilha Excel...")
    
    df_final = pd.read_excel(EVALUATION_FILE, sheet_name="Z3_Evaluation")

    for model_name in MODELS_TO_TEST:
        model_key = model_name.replace('-', '_')
        formalization_col = f"{model_key}_formalization"
        result_col = f"{model_key}_z3_result"
        
        if formalization_col not in df_final.columns: df_final[formalization_col] = None
        if result_col not in df_final.columns: df_final[result_col] = None
        
        results_path = RAW_RESULTS_DIR / f"z3_results_{model_key}.jsonl"
        if results_path.exists():
            with open(results_path, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        res = json.loads(line)
                        sample_id = res['sample_id']
                        formalization_str = res['llm_formalization']
                        
                        target_index = df_final[df_final['sample_id'] == sample_id].index
                        if not target_index.empty:
                            df_final.loc[target_index, formalization_col] = formalization_str
                            
                            match = re.search(r'\{.*\}', formalization_str, re.DOTALL)
                            json_str = match.group(0) if match else "{}"
                            z3_result_dict = evaluate_z3_consequence(json.loads(json_str))
                            df_final.loc[target_index, result_col] = z3_result_dict["z3_result_of_negation"]
                    except (json.JSONDecodeError, KeyError):
                        continue

    try:
        with pd.ExcelWriter(EVALUATION_FILE, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            df_final.to_excel(writer, sheet_name="Z3_Evaluation", index=False)
        print(f"\nSucesso! Os resultados foram preenchidos na aba 'Z3_Evaluation' do arquivo '{EVALUATION_FILE.name}'.")
    except Exception as e:
        print(f"\nERRO ao salvar os resultados no arquivo Excel: {e}")

if __name__ == '__main__':
    main()
import os
import json
import re
import logging
from pathlib import Path
from tqdm import tqdm
import sys
sys.path.append(str(Path(__file__).parent.parent))

os.environ['GRPC_VERBOSITY'] = 'ERROR'
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

from config import LOGIC_RULES_CONFIG
from engine import ApiKeyManager, make_api_call

PROJECT_ROOT = Path(__file__).parent.parent.parent

# --- CONFIGURAÇÃO DA ETAPA 2 ---
INPUT_FILE = PROJECT_ROOT / "artifacts" / "stage_1_sentence_banks.jsonl"
OUTPUT_FILE = PROJECT_ROOT / "artifacts" / "stage_2_naturalized_contexts.jsonl"
MODEL_NAME = 'gemini-2.5-pro'
# ------------------------------------

def naturalize_context(key_manager, model_name, filled_context, rule_key):
    """Função da Etapa 2b: Pega o contexto templatizado e o transforma em uma narrativa."""
    prompt = f"""Sua tarefa é transformar um conjunto de fatos lógicos em uma pequena história (narrativa) em português. A história deve conter as informações dos fatos de entrada de forma natural.

**Instruções Cruciais:**
1. Crie um pequeno cenário, talvez com um personagem.
2. A história deve apresentar as PREMISSAS, mas **NUNCA, EM HIPÓTESE ALGUMA, afirme ou descreva a CONCLUSÃO LÓGICA**. O objetivo é que a conclusão precise ser inferida.
3. A saída deve ser APENAS o parágrafo da história.

**AGORA, SUA TAREFA:**
Fatos de Entrada: "{filled_context}"
História de Saída:"""
    return make_api_call(key_manager, model_name, prompt, call_purpose=f"Naturalização ({rule_key})")

def parse_audit_log(log_path):
    """Lê o arquivo de log da Etapa 1."""
    if not log_path.exists():
        raise FileNotFoundError(f"Arquivo de log '{log_path}' não encontrado.")
    with open(log_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    parsed_data = []
    for line in lines:
        try:
            parsed_data.append(json.loads(line))
        except json.JSONDecodeError:
            logging.warning(f"Pulando linha malformada no log de entrada: {line.strip()}")
    return parsed_data

if __name__ == "__main__":
    try:
        key_path = Path("D:/IFCE/api_keys.json")
        key_manager = ApiKeyManager(key_path)
    except Exception as e:
        print(f"CRÍTICO: Falha ao iniciar o gerenciador de chaves. Erro: {e}"); exit()

    input_path = Path.cwd().parent / INPUT_FILE
    output_path = Path.cwd().parent / OUTPUT_FILE
    
    print(f"INICIANDO ETAPA 2: Naturalização de Contextos")
    print(f"Lendo bancos de sentenças de: {input_path}")
    print(f"O resultado será salvo em: {output_path}\n")

    all_banks_data = parse_audit_log(input_path)

    with open(output_path, 'w', encoding='utf-8') as f_out:
        for data in tqdm(all_banks_data, desc="Processando Instâncias"):
            try:
                rule_key = data["rule"]
                sentence_bank = data["sentence_bank"]
                logic_type, rule_name = rule_key.split('/')
                rule_template = LOGIC_RULES_CONFIG[logic_type][rule_name]
            except (KeyError, ValueError):
                logging.warning(f"Pulando entrada malformada: {data}")
                continue

            # MUDANÇA: Corrigido o regex para incluir espaços, capturando chaves como '{not q}'.
            all_props = set(re.findall(r'\{([a-zA-Z0-9_ ]+)\}', json.dumps(rule_template)))
            
            # Preenche negações que possam faltar
            for prop in all_props:
                if prop not in sentence_bank and prop.startswith("not "):
                    base_key = prop.replace("not ", "")
                    if base_key in sentence_bank:
                        sentence_bank[prop] = "não " + sentence_bank[base_key]
            
            # Etapa 2a: Contexto Templatizado (feito em memória)
            try:
                filled_context = rule_template["template_context"].format(**sentence_bank)
            except KeyError as e:
                logging.error(f"KeyError para a regra {rule_key} mesmo após a correção. Chave faltando: {e}. Banco de sentenças: {sentence_bank}")
                continue

            # Etapa 2b: Naturalização (a chamada de API)
            natural_context = naturalize_context(key_manager, MODEL_NAME, filled_context, rule_key)
            if not natural_context:
                natural_context = filled_context # Fallback para o texto robotizado se a API falhar

            # Salva o resultado combinado em uma nova linha no arquivo de saída
            output_data = {
                "rule": rule_key,
                "sentence_bank": sentence_bank,
                "natural_context": natural_context
            }
            f_out.write(json.dumps(output_data, ensure_ascii=False) + '\n')

    print(f"\nETAPA 2 CONCLUÍDA.")
    print(f"Por favor, analise o arquivo '{OUTPUT_FILE}' antes de prosseguir para a Etapa 3.")
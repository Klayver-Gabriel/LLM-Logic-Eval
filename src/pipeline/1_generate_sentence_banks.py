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
from prompts import PROMPT_BANK, FALLBACK_PROMPT
from engine import ApiKeyManager, make_api_call

PROJECT_ROOT = Path(__file__).parent.parent.parent

# --- CONFIGURAÇÃO DA ETAPA 1 ---
NUM_INSTANCES_PER_RULE = 10
MODEL_NAME = 'gemini-2.5-pro'
OUTPUT_FILE = PROJECT_ROOT / "artifacts" / "stage_1_sentence_banks.jsonl"
# ------------------------------------

if __name__ == "__main__":
    try:
        key_manager = ApiKeyManager()
    except Exception as e:
        print(f"CRÍTICO: Falha ao iniciar o gerenciador de chaves. Erro: {e}"); exit()

    pl_rules = LOGIC_RULES_CONFIG.get('PL', {})
    if not pl_rules:
        print("ERRO: Nenhuma regra de Lógica Proposicional ('PL') encontrada em config.py.")
        exit()

    print(f"INICIANDO ETAPA 1: Geração de Bancos de Sentenças (Foco: Lógica Proposicional)")
    print(f"O resultado será salvo em: {OUTPUT_FILE}\n")
    os.makedirs(OUTPUT_FILE.parent, exist_ok=True)

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        for rule_name, rule_template in tqdm(pl_rules.items(), desc="Processando Regras de PL"):
            
            logic_type = 'PL'
            rule_key = f"{logic_type}/{rule_name}"
            
            if rule_key not in PROMPT_BANK:
                logging.warning(f"Nenhum prompt especializado encontrado para {rule_key}. Pulando esta regra.")
                continue
            
            prompt_template = PROMPT_BANK[rule_key]
            
            prompt = prompt_template.format(num_instances=NUM_INSTANCES_PER_RULE)
            
            response_text = make_api_call(key_manager, MODEL_NAME, prompt, call_purpose=rule_key)
            
            if response_text:
                try:
                    match = re.search(r'\[.*\]', response_text, re.DOTALL)
                    json_str = match.group(0) if match else response_text
                    sentence_banks_array = json.loads(json_str)
                    
                    if isinstance(sentence_banks_array, list) and len(sentence_banks_array) > 0:
                        for bank in sentence_banks_array:
                            line_data = {"rule": rule_key, "sentence_bank": bank}
                            f.write(json.dumps(line_data, ensure_ascii=False) + '\n')
                    else:
                        logging.error(f"A resposta para {rule_key} não foi uma lista válida.")

                except json.JSONDecodeError:
                    logging.error(f"Falha ao decodificar a resposta JSON para {rule_key}. Resposta: {response_text}")

    print(f"\nETAPA 1 CONCLUÍDA.")
    print(f"Por favor, analise o arquivo '{OUTPUT_FILE}' antes de prosseguir para a Etapa 2.")
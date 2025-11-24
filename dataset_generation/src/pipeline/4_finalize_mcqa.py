import os
import json
import re
import logging
from pathlib import Path
from tqdm import tqdm
import random
from collections import defaultdict

import sys
sys.path.append(str(Path(__file__).parent.parent))

os.environ['GRPC_VERBOSITY'] = 'ERROR'
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

from config import LOGIC_RULES_CONFIG
from engine import ApiKeyManager, make_api_call

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

# --- CONFIGURAÇÃO DA ETAPA 3.2 (MCQA) ---
INPUT_FILE = PROJECT_ROOT / "dataset_generation" / "artifacts" / "stage_2b_naturalized_contexts.jsonl"
BASE_OUTPUT_DIR = PROJECT_ROOT / "dataset_generation" / "output" / "LogicBench(Eval)" / "MCQA"
MODEL_NAME = 'gemini-2.5-pro'
# ------------------------------------

def parse_stage_2_log(log_path):
    if not log_path.exists():
        raise FileNotFoundError(f"Arquivo de log da Etapa 2 '{log_path}' não encontrado.")
    
    instances_by_rule = defaultdict(list)
    with open(log_path, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                data = json.loads(line)
                rule_key = data["rule"]
                instances_by_rule[rule_key].append(data)
            except (json.JSONDecodeError, KeyError):
                logging.warning(f"Pulando linha malformada no log de entrada: {line.strip()}")
    return instances_by_rule

def generate_distractors(key_manager, model_name, context, correct_answer, rule_key):
    prompt = f"""Sua tarefa é gerar TRÊS opções incorretas (distratores) para uma pergunta de múltipla escolha.
As opções devem ser plausíveis dado o contexto, mas logicamente incorretas ou irrelevantes.

Contexto: "{context}"
Resposta Correta: "{correct_answer}"

**IMPORTANTE:** Forneça APENAS os três distratores, cada um em uma nova linha. Não use marcadores, numeração ou qualquer texto introdutório."""
    
    response_text = make_api_call(key_manager, model_name, prompt, call_purpose=f"Distratores ({rule_key})")
    
    if response_text:
        distractors = [line.strip() for line in response_text.split('\n') if line.strip()]
        return distractors[:3]
    return []

if __name__ == "__main__":
    try:
        key_manager = ApiKeyManager()
    except Exception as e:
        print(f"CRÍTICO: Falha ao iniciar o gerenciador de chaves. Erro: {e}"); exit()

    input_log_path = INPUT_FILE
    
    print(f"INICIANDO ETAPA 4: Geração do Dataset MCQA")
    print(f"Lendo contextos naturalizados de: {input_log_path}")
    all_instances_data = parse_stage_2_log(input_log_path)

    base_output_dir = BASE_OUTPUT_DIR
    print(f"Gerando arquivos finais em: {base_output_dir}\n")

    for rule_key, instances in tqdm(all_instances_data.items(), desc="Processando Regras (MCQA)"):
        try:
            logic_type, rule_name = rule_key.split('/')
            rule_template = LOGIC_RULES_CONFIG[logic_type][rule_name]
        except (KeyError, ValueError):
            logging.error(f"Regra '{rule_key}' não encontrada no config.py. Pulando.")
            continue
        
        logic_type_folder_name = {"PL": "propositional_logic", "FOL": "first_order_logic", "NM": "nm_logic"}.get(logic_type, logic_type)
        output_dir_for_rule = base_output_dir / logic_type_folder_name / rule_name
        os.makedirs(output_dir_for_rule, exist_ok=True)
        
        file_path = output_dir_for_rule / "data_instances.json"
        final_json_output = {"type": logic_type_folder_name, "axiom": rule_name.lower(), "samples": []}

        for i, instance_data in enumerate(instances):
            original_sentence_bank = instance_data["sentence_bank"]
            natural_context = instance_data["natural_context"]

            # Criamos um banco de sentenças limpo para formatar a conclusão
            cleaned_bank = {}
            for key, value in original_sentence_bank.items():
                cleaned_value = value.strip().removesuffix('.')
                if cleaned_value:
                    cleaned_value = cleaned_value[0].lower() + cleaned_value[1:]
                cleaned_bank[key] = cleaned_value

            # 1. Encontrar a conclusão correta usando a chave explícita 'mcqa_correct_conclusion'
            try:
                conclusion_format = rule_template["mcqa_correct_conclusion"]
                correct_conclusion_text = conclusion_format.format(**cleaned_bank)
                # Garante que a conclusão final comece com letra maiúscula
                if correct_conclusion_text:
                    correct_conclusion_text = correct_conclusion_text[0].upper() + correct_conclusion_text[1:]
            except KeyError:
                logging.error(f"A chave 'mcqa_correct_conclusion' não foi encontrada para a regra {rule_key}. Pulando.")
                continue
            
            # 2. Gerar os distratores via API
            distractors = generate_distractors(key_manager, MODEL_NAME, natural_context, correct_conclusion_text, rule_key)
            if len(distractors) < 3:
                logging.warning(f"Não foi possível gerar distratores suficientes para {rule_key}, instância {i+1}. Pulando.")
                continue

            # 3. Montar e embaralhar as opções
            options = [correct_conclusion_text] + distractors
            random.shuffle(options)
            
            # 4. Encontrar o índice da resposta correta
            try:
                correct_answer_index = options.index(correct_conclusion_text)
            except ValueError:
                logging.error(f"A resposta correta não foi encontrada na lista de opções para {rule_key}, instância {i+1}. Pulando.")
                continue

            # 5. Montar o sample final
            sample = {
                "id": i + 1,
                "context": natural_context,
                "question": "Qual seria a conclusão mais apropriada com base no contexto?",
                "options": options,
                "answer": correct_answer_index
            }
            final_json_output["samples"].append(sample)

        if final_json_output["samples"]:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(final_json_output, f, ensure_ascii=False, indent=4)

    print(f"\nETAPA 3.2 (MCQA) CONCLUÍDA.")
    print("Processo finalizado com sucesso.")
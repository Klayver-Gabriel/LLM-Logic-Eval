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

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

from config import LOGIC_RULES_CONFIG

PROJECT_ROOT = Path(__file__).parent.parent.parent

# --- CONFIGURAÇÃO DA PRIMEIRA PARTE DA ETAPA 3 (BQA) ---
INPUT_FILE = PROJECT_ROOT / "artifacts" / "stage_2_naturalized_contexts.jsonl"
BASE_OUTPUT_DIR = PROJECT_ROOT / "output" / "LogicBench(Eval)" / "BQA"
# ------------------------------------

def parse_stage_2_log(log_path):
    """Lê o log da Etapa 2 e agrupa as instâncias por regra."""
    if not log_path.exists():
        raise FileNotFoundError(f"Arquivo de log da Etapa 2 '{log_path}' não encontrado.")
    
    # Usamos defaultdict para facilitar o agrupamento
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

if __name__ == "__main__":
    input_log_path = Path.cwd().parent / INPUT_FILE
    
    print(f"INICIANDO ETAPA 3: Finalização e Montagem do Dataset")
    print(f"Lendo contextos naturalizados de: {input_log_path}")
    all_instances_data = parse_stage_2_log(input_log_path)

    base_output_dir = Path.cwd().parent / 'LogicBench(Eval)' / 'BQA'
    print(f"Gerando arquivos finais em: {base_output_dir}\n")

    for rule_key, instances in tqdm(all_instances_data.items(), desc="Finalizando Regras"):
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
            sentence_bank = instance_data["sentence_bank"]
            natural_context = instance_data["natural_context"]

            # Preenche negações que possam faltar (lógica de segurança)
            all_props = set(re.findall(r'\{([a-zA-Z0-9_ ]+)\}', json.dumps(rule_template)))
            for prop in all_props:
                if prop not in sentence_bank and prop.startswith("not "):
                    base_key = prop.replace("not ", "")
                    if base_key in sentence_bank:
                        sentence_bank[prop] = "não " + sentence_bank[base_key]

            # Formata os pares de pergunta e resposta (sem chamada de API)
            bqa_questions = []
            for q_template in rule_template["bqa_templates"]:
                try:
                    question_text_template = random.choice(q_template["question"])
                    formatted_question = question_text_template.format(**sentence_bank)
                    bqa_questions.append({"question": formatted_question, "answer": q_template["answer"]})
                except KeyError as e:
                    logging.error(f"KeyError na regra {rule_key}, instância {i+1}: Chave '{e}' não encontrada no banco de sentenças. Pulando esta pergunta.")
            
            if bqa_questions: # Adiciona o sample apenas se conseguiu gerar as perguntas
                sample = {"id": i + 1, "context": natural_context, "qa_pairs": bqa_questions}
                final_json_output["samples"].append(sample)

        if final_json_output["samples"]:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(final_json_output, f, ensure_ascii=False, indent=4)

    print(f"\nETAPA 3 CONCLUÍDA.")
    print("Dataset final gerado com sucesso na pasta 'LogicBench(Eval)/BQA'.")
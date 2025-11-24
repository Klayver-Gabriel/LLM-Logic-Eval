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

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

# --- CONFIGURAÇÃO DA ETAPA 2 ---
INPUT_FILE = PROJECT_ROOT / "dataset_generation" / "artifacts" / "stage_1_sentence_banks.jsonl"
OUTPUT_STAGE_2A_FILE = PROJECT_ROOT / "dataset_generation" / "artifacts" / "stage_2a_templated_contexts.jsonl"
OUTPUT_STAGE_2B_FILE = PROJECT_ROOT / "dataset_generation" / "artifacts" / "stage_2b_naturalized_contexts.jsonl"
MODEL_NAME = 'gemini-2.5-pro'
# ------------------------------------

def naturalize_context(key_manager, model_name, condition, situation, rule_key):
    
    example_context = """Regra: Condição: Se Liam terminar seu trabalho cedo, então ele pedirá pizza para o jantar.; Situação: Ele não vai pedir pizza para o jantar.
Contexto: Liam terminou seu trabalho mais cedo naquele dia, o que significava que ele normalmente pediria pizza para o jantar. No entanto, neste dia em particular, ele decidiu não pedir pizza e optou por outra coisa."""

    prompt = f"""Melhore o contexto para uma linguagem humana e crie uma história com as sentenças reformuladas.
Instruções para gerar uma boa história:
1. Ao gerar a história, use as sentenças reformuladas do contexto da história.
2. Certifique-se de incluir sentenças correspondentes à condição e à situação da regra na história.
3. Não adicione nenhuma outra informação extra.
4. Para gerar a história, NÃO mude o nome do personagem principal do contexto, se houver.
5. Gere apenas um parágrafo com as sentenças reformuladas.
6. **NUNCA, EM HIPÓTESE ALGUMA, afirme ou descreva a CONCLUSÃO LÓGICA**. O objetivo é que a conclusão precise ser inferida.

---
{example_context}
---
Regra: Condição: {condition}; Situação: {situation}
Contexto:"""
    return make_api_call(key_manager, model_name, prompt, call_purpose=f"Naturalização ({rule_key})")

def parse_audit_log(log_path):
    
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

def run_stage_2a(input_path, output_path):
    """Etapa 2a: Lê os bancos de sentenças, limpa os dados e gera o arquivo com os contextos templatizados."""
    print(f"INICIANDO ETAPA 2a: Geração de Contextos Templatizados")
    print(f"Lendo bancos de sentenças de: {input_path}")
    print(f"O resultado será salvo em: {output_path}\n")

    if not input_path.exists():
        raise FileNotFoundError(f"Arquivo de entrada '{input_path.name}' não encontrado.")

    all_banks_data = parse_audit_log(input_path)

    with open(output_path, 'w', encoding='utf-8') as f_out:
        for data in tqdm(all_banks_data, desc="Etapa 2a - Gerando Templates"):
            try:
                rule_key = data["rule"]
                sentence_bank = data["sentence_bank"]
                logic_type, rule_name = rule_key.split('/')
                rule_template = LOGIC_RULES_CONFIG[logic_type][rule_name]
            except (KeyError, ValueError):
                continue

            # Etapa de limpeza do banco de sentenças
            cleaned_bank = {}
            for key, value in sentence_bank.items():
                # 1. Remove espaços em branco e o ponto final
                cleaned_value = value.strip().removesuffix('.')
                # 2. Converte a primeira letra para minúscula
                if cleaned_value:
                    cleaned_value = cleaned_value[0].lower() + cleaned_value[1:]
                cleaned_bank[key] = cleaned_value
            
            all_props = set(re.findall(r'\{([a-zA-Z0-9_ ]+)\}', json.dumps(rule_template)))
            for prop in all_props:
                if prop not in cleaned_bank and prop.startswith("not "):
                    base_key = prop.replace("not ", "")
                    if base_key in cleaned_bank:
                        cleaned_bank[prop] = "não " + cleaned_bank[base_key]
            
            try:
                filled_context = rule_template["template_context"].format(**cleaned_bank)
                # Garante que a frase final comece com letra maiúscula
                if filled_context:
                    filled_context = filled_context[0].upper() + filled_context[1:]
                
                parts = filled_context.split('. ')
                condition = ('. '.join(parts[:-1]) + '.') if len(parts) > 1 else filled_context
                situation = parts[-1] if len(parts) > 1 else ""

                output_data = {
                    "rule": rule_key,
                    "sentence_bank": sentence_bank, # Salva o original para referência
                    "templated_context": filled_context, # Salva o contexto limpo
                    "condition": condition,
                    "situation": situation
                }
                f_out.write(json.dumps(output_data, ensure_ascii=False) + '\n')
            except KeyError as e:
                logging.error(f"KeyError para a regra {rule_key}. Chave faltando: {e}.")

    print(f"\nETAPA 2a CONCLUÍDA.")

def run_stage_2b(input_path, output_path, key_manager):
  
    print(f"\nINICIANDO ETAPA 2b: Naturalização de Contextos")
    print(f"Lendo contextos templatizados de: {input_path}")
    print(f"O resultado será salvo em: {output_path}\n")

    if not input_path.exists():
        raise FileNotFoundError(f"Arquivo de entrada da Etapa 2a '{input_path.name}' não encontrado.")

    with open(input_path, 'r', encoding='utf-8') as f_in, open(output_path, 'w', encoding='utf-8') as f_out:
        lines = f_in.readlines()
        for line in tqdm(lines, desc="Etapa 2b - Naturalizando"):
            try:
                data = json.loads(line)
                rule_key = data["rule"]
                condition = data["condition"]
                situation = data["situation"]
            except (json.JSONDecodeError, KeyError):
                continue
            
            natural_context = naturalize_context(key_manager, MODEL_NAME, condition, situation, rule_key)
            if not natural_context:
                natural_context = f"{condition} {situation}".strip()

            output_data = {
                "rule": rule_key,
                "sentence_bank": data["sentence_bank"],
                "natural_context": natural_context
            }
            f_out.write(json.dumps(output_data, ensure_ascii=False) + '\n')

    print(f"\nETAPA 2b CONCLUÍDA.")

if __name__ == "__main__":
    try:
        key_manager = ApiKeyManager()
    except Exception as e:
        print(f"CRÍTICO: Falha ao iniciar o gerenciador de chaves. Erro: {e}"); exit()

    run_stage_2a(INPUT_FILE, OUTPUT_STAGE_2A_FILE)

    print("-" * 50)
    print(f"Artefato da Etapa 2a foi salvo em '{OUTPUT_STAGE_2A_FILE.name}'.")
    user_input = input("Por favor, verifique o arquivo. Deseja continuar para a Etapa 2b (Naturalização)? (s/n): ")
    print("-" * 50)

    if user_input.lower() == 's':
        run_stage_2b(OUTPUT_STAGE_2A_FILE, OUTPUT_STAGE_2B_FILE, key_manager)
        print(f"Processo completo. O resultado final da Etapa 2 está em '{OUTPUT_STAGE_2B_FILE.name}'.")
    else:
        print("Execução da Etapa 2b cancelada pelo usuário.")
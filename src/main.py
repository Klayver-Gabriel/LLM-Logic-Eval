# src/main.py
import os
import json
from pathlib import Path
from tqdm import tqdm
import logging 

# Importa as lógicas
from config import LOGIC_RULES_CONFIG
from engine import ApiKeyManager, generate_dataset_instance

# --- Bloco de Execução Principal ---
if __name__ == "__main__":
    
    # --- SUPRESSÃO DE WARNINGS ---
    logging.basicConfig()
    logging.getLogger('google.auth.transport.grpc').setLevel(logging.CRITICAL)
    logging.getLogger('google.auth.transport.requests').setLevel(logging.CRITICAL)
    
    # --- Parâmetros Configuráveis ---
    NUM_INSTANCES_PER_RULE = 5
    MODEL_NAME = 'gemini-2.5-pro' # Nome correto da API
    
    # --- Inicialização ---
    try:
        # Caminho relativo ao CWD (current working directory) que será a pasta do projeto
        key_path = Path.cwd() / '..' / 'api_keys.json'
        
        key_path = Path("D:/IFCE/api_keys.json")

        key_manager = ApiKeyManager(key_path)
    except Exception as e:
        print(f"CRÍTICO: Falha ao iniciar o gerenciador de chaves. Verifique o caminho. Erro: {e}")
        exit()

    print("Iniciando a geração do dataset completo no formato LogicBench...")

    # --- Loop Principal de Geração ---
    for logic_type, rules in LOGIC_RULES_CONFIG.items():
        output_dir = Path.cwd() / 'data' / logic_type
        os.makedirs(output_dir, exist_ok=True)

        for rule_name, rule_template in rules.items():
            print(f"\n--- Gerando {NUM_INSTANCES_PER_RULE} instâncias para: {logic_type} / {rule_name} ---")
            
            all_instances_for_rule = []
            pbar = tqdm(range(NUM_INSTANCES_PER_RULE))
            for i in pbar:
                pbar.set_description(f"Processando instância {i+1}")
                instance = generate_dataset_instance(key_manager, MODEL_NAME, rule_template)
                if instance:
                    all_instances_for_rule.append(instance)

            # --- Salvando o Arquivo ---
            if all_instances_for_rule:
                file_path = output_dir / f"{rule_name}.json"
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(all_instances_for_rule, f, ensure_ascii=False, indent=4)
                print(f"Sucesso! Arquivo salvo em: {file_path}")

    print("\n\nProcesso de geração do dataset completo foi concluído.")
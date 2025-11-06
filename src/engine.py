import google.generativeai as genai
from google.api_core import exceptions
import json
import time
import logging
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent

class ApiKeyManager:
    def __init__(self):
      
        key_path = PROJECT_ROOT / "api_keys.json"
        try:
            with open(key_path, 'r') as f:
                data = json.load(f)
            self.keys = list(data['API_KEYS'].values())
        except Exception as e:
            raise ValueError(f"Não foi possível carregar as chaves de API de {key_path}: {e}")
        self.current_index = 0
        if not self.keys:
            raise ValueError("Nenhuma chave de API do Gemini foi encontrada.")

    def get_current_key(self):
        return self.keys[self.current_index]

    def rotate_key(self):
        self.current_index = (self.current_index + 1) % len(self.keys)
        logging.warning(f"Rotacionando para a chave de API índice #{self.current_index}...")
        return self.keys[self.current_index]

    def __len__(self):
        return len(self.keys)

def make_api_call(key_manager, model_name, prompt, call_purpose="Geral"):
    API_CALL_COOLDOWN = 35
    for _ in range(len(key_manager)):
        try:
            current_key = key_manager.get_current_key()
            genai.configure(api_key=current_key)
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            logging.info(f"Chamada [{call_purpose}] bem-sucedida. Aguardando {API_CALL_COOLDOWN}s...")
            time.sleep(API_CALL_COOLDOWN)
            return response.text.strip()
        except exceptions.ResourceExhausted:
            logging.warning(f"Quota excedida na chamada [{call_purpose}].")
            key_manager.rotate_key()
            time.sleep(5)
            continue
        except Exception as e:
            logging.error(f"A API retornou um erro inesperado na chamada [{call_purpose}]: {e}")
            key_manager.rotate_key()
            time.sleep(5)
    logging.critical(f"Todas as chaves falharam para a chamada [{call_purpose}].")
    return None
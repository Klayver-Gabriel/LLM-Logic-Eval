# src/engine.py
import google.generativeai as genai
from google.api_core import exceptions
import json
import random
import time
import re

class ApiKeyManager:
    """Gerencia o carregamento e a rotação de chaves de API do Gemini."""
    def __init__(self, json_path):
        self.keys = self._load_keys(json_path)
        self.current_index = 0
        if not self.keys: raise ValueError("Nenhuma chave de API do Gemini foi encontrada.")
        print(f"Gerenciador de chaves iniciado com {len(self.keys)} chaves.")

    def _load_keys(self, json_path):
        try:
            with open(json_path, 'r') as f: data = json.load(f)
            return list(data['API_KEYS'].values())
        except Exception as e:
            print(f"ERRO: Não foi possível carregar as chaves de '{json_path}'. Verifique o arquivo. Erro: {e}")
            return []

    def get_current_key(self):
        """Retorna a chave atual sem avançar o índice."""
        return self.keys[self.current_index]

    def rotate_key(self):
        """Avança para a próxima chave na lista."""
        self.current_index = (self.current_index + 1) % len(self.keys)
        print(f"Aviso: Rotacionando para a chave de API índice #{self.current_index}...")
        return self.keys[self.current_index]

    def __len__(self): return len(self.keys)

def call_gemini_api(key_manager, model_name, prompt):
    """
    Função central para chamadas à API com lógica de rotação corrigida.
    Só rotaciona a chave em caso de erro de quota.
    """
    # Tenta usar todas as chaves em sequência se necessário
    for _ in range(len(key_manager)):
        try:
            current_key = key_manager.get_current_key()
            genai.configure(api_key=current_key)
            model = genai.GenerativeModel(model_name)
            
            response = model.generate_content(prompt)
            # Se a chamada for bem-sucedida, retorna o resultado imediatamente.
            return response.text.strip()

        except exceptions.ResourceExhausted:
            # Erro de quota: rotaciona a chave e tenta novamente no próximo loop
            print("Aviso: Quota excedida.")
            key_manager.rotate_key()
            # Pequeno delay antes de tentar com a nova chave
            time.sleep(1)
            continue

        except Exception as e:
            # Outros erros: rotaciona a chave para evitar ficar preso em uma chave com problema
            print(f"ERRO: A API retornou um erro inesperado: {e}")
            key_manager.rotate_key()
            time.sleep(5)

    # Se o loop terminar, todas as chaves falharam
    print("ERRO CRÍTICO: Todas as chaves falharam em sequência. Aguardando 60 segundos...")
    time.sleep(60)
    return None


def generate_sentence_bank(key_manager, model_name, propositions_needed):
    prompt = f"""
    Sua tarefa é gerar um conjunto de sentenças simples e coerentes para as seguintes proposições: {', '.join(propositions_needed)}.
    As sentenças devem ter uma conexão temática.
    Instruções de Formatação: Retorne a resposta em um formato JSON. As chaves do JSON devem ser exatamente as proposições solicitadas.
    Exemplo para ['p', 'not p', 'q', 'not q']:
    {{
      "p": "O alarme de incêndio é acionado.", "not p": "O alarme de incêndio não é acionado.",
      "q": "Os sprinklers são ativados.", "not q": "Os sprinklers não são ativados."
    }}
    Gere um novo conjunto agora para: {', '.join(propositions_needed)}"""
    response_text = call_gemini_api(key_manager, model_name, prompt)
    if not response_text: return None
    try:
        json_str = response_text.strip().replace("```json", "").replace("```", "")
        return json.loads(json_str)
    except json.JSONDecodeError:
        print(f"ERRO: Falha ao decodificar JSON da resposta do LLM:\n{response_text}")
        return None

def naturalize_context(key_manager, model_name, filled_context):
    prompt = f"""Reescreva o texto abaixo para que soe como uma narrativa curta e natural. Preserve toda a informação e a estrutura lógica. Não adicione informação nova e não tire nenhuma conclusão.
    Texto para reescrever: "{filled_context}"
    Narrativa reescrita:"""
    return call_gemini_api(key_manager, model_name, prompt)

def generate_mcq_distractors(key_manager, model_name, context, correct_answer):
    prompt = f"""Você está criando um teste de raciocínio lógico. Dado o contexto e a conclusão correta, crie três (3) opções incorretas (distratores).
    Contexto: "{context}"
    Conclusão Correta: "{correct_answer}"
    Instruções: Os distratores devem ser plausíveis, mas logicamente inválidos. Devem ser distintos. Formate a saída como uma lista, com cada item em uma nova linha, começando com '- '.
    - [Distrator 1]
    - [Distrator 2]
    - [Distrator 3]"""
    response_text = call_gemini_api(key_manager, model_name, prompt)
    if not response_text: return []
    return [line.strip('- ').strip() for line in response_text.split('\n')]

def generate_dataset_instance(key_manager, model_name, rule_template):
    propositions_needed = list(set(re.findall(r'\{([^}]+)\}', json.dumps(rule_template))))
    
    sentence_bank = generate_sentence_bank(key_manager, model_name, propositions_needed)
    if not sentence_bank: return None

    # Adiciona um pequeno delay entre as chamadas de API para a mesma instância
    time.sleep(2) 
    filled_context = rule_template["template_context"].format(**sentence_bank)

    natural_context = naturalize_context(key_manager, model_name, filled_context)
    if not natural_context: natural_context = filled_context
    
    time.sleep(2)
    bqa_questions = [
        {"question": q["question"].format(**sentence_bank), "answer": q["answer"]}
        for q in rule_template["bqa_templates"]
    ]
    
    try:
        correct_conclusion_text = bqa_questions[0]["question"].split("'")[1]
    except IndexError:
        correct_conclusion_text = rule_template["bqa_templates"][0]["question"].format(**sentence_bank).replace("Podemos concluir que ", "").replace("?", "")

    distractors = generate_mcq_distractors(key_manager, model_name, natural_context, correct_conclusion_text)
    if len(distractors) < 3:
        mcq_data = None
    else:
        options = distractors[:3] + [correct_conclusion_text]
        random.shuffle(options)
        correct_answer_index = options.index(correct_conclusion_text)
        mcq_data = {
            "question": "Com base no contexto fornecido, qual seria a conclusão mais apropriada?",
            "options": options,
            "answer": f"Option {correct_answer_index + 1}"
        }

    return {"context": natural_context, "questions": bqa_questions, "mcq": mcq_data}
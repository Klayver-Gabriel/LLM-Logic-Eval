import logging
import sys
import pandas as pd
from pathlib import Path
import time

# --- Configuração de Path ---
PROJECT_ROOT = Path(__file__).parent
sys.path.append(str(PROJECT_ROOT / 'src'))

try:
    from engine import ApiKeyManager, make_api_call
except ImportError as e:
    print(f"Erro de Importação: {e}")
    sys.exit(1)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%H:%M:%S')

# Arquivo gerado em processar_pasta.py
ARQUIVO_ENTRADA = "output/analise.xlsx"

ARQUIVO_SAIDA = "output/analise.xlsx"

# Mapeia: Nome da Coluna no Excel -> Nome do Modelo na API
MODELS_TO_RUN = {
    "flash_answer": "models/gemini-2.5-flash",
    "pro_answer":   "models/gemini-2.5-pro"
}


def limpar_resposta(texto, task_type):
    if not texto:
        return "Erro"
    texto = str(texto).strip()

    if task_type == "BQA":
        t = texto.lower()
        if "sim" in t: return "Sim"
        if "não" in t or "nao" in t: return "Não"
        return "Indeterminado"

    return texto.replace("\n", " ").strip()

# PIPELINE
def processar_dataset_existente():
    input_path = PROJECT_ROOT / ARQUIVO_ENTRADA
    output_path = PROJECT_ROOT / ARQUIVO_SAIDA

    # Verifica arquivo
    if not input_path.exists():
        logging.critical(f"Arquivo não encontrado: {input_path}")
        logging.critical("Verifique se o arquivo 'analise.xlsx' está dentro da pasta 'output'.")
        return

    logging.info(f"Lendo dataset: {input_path}")
    # Lê o arquivo Excel
    try:
        df = pd.read_excel(input_path)
    except Exception as e:
        logging.error(f"Erro ao abrir o Excel: {e}")
        return

    # Verifica colunas obrigatórias
    obrigatorias = ["context", "question", "task_type"]
    for col in obrigatorias:
        if col not in df.columns:
            logging.error(f"Faltando coluna obrigatória no Excel: {col}")
            return

    # Cria colunas de resposta se não existirem
    for col in MODELS_TO_RUN.keys():
        if col not in df.columns:
            df[col] = None

    # Inicializa API
    try:
        key_manager = ApiKeyManager()
    except Exception as e:
        logging.error(f"Erro ao inicializar chaves: {e}")
        return

    total = len(df)
    logging.info(f"Iniciando avaliação de {total} linhas...")

    # Loop principal
    for index, row in df.iterrows():
        contexto = row["context"]
        pergunta = row["question"]
        tipo = row["task_type"]

        # Verifica se essa linha JÁ TEM RESPOSTAS
        # Se flash_answer E pro_answer já estiverem preenchidos, pula.
        ja_tem_flash = pd.notna(row.get("flash_answer")) and row.get("flash_answer") != "Erro"
        ja_tem_pro = pd.notna(row.get("pro_answer")) and row.get("pro_answer") != "Erro"

        if ja_tem_flash and ja_tem_pro:
            continue # Pula para a próxima linha

        logging.info(f"--- Processando item {index+1}/{total} ---")

        # Monta o Prompt
        if tipo == "BQA":
            prompt = (
                f"CONTEXTO: {contexto}\n"
                f"PERGUNTA: {pergunta}\n"
                f"Responda APENAS com 'Sim' ou 'Não'."
            )
        else:
            prompt = (
                f"Atue como um motor lógico.\n"
                f"PREMISSAS: {contexto}\n"
                f"TAREFA: {pergunta}\n"
                f"Responda apenas com a conclusão."
            )

        # Chama os modelos
        salvar_agora = False
        for coluna_excel, modelo_api in MODELS_TO_RUN.items():
            
            # Se esse modelo específico já respondeu, não executa novamente
            if pd.notna(row.get(coluna_excel)) and row.get(coluna_excel) != "Erro":
                continue
            try:
                resposta_raw = make_api_call(key_manager, modelo_api, prompt, call_purpose=f"Row {index}")
            except Exception as e:
                logging.error(f"Erro na API ({modelo_api}): {e}")
                resposta_raw = "Erro"
                
            resposta_limpa = limpar_resposta(resposta_raw, tipo)
            df.at[index, coluna_excel] = resposta_limpa
            salvar_agora = True

        # Salva o arquivo a cada linha processada (se houve mudança)
        if salvar_agora:
            try:
                df.to_excel(output_path, index=False)
            except PermissionError:
                logging.warning(f"AVISO: Não foi possível salvar a linha {index+1}. O Excel está aberto?")
            except Exception as e:
                logging.error(f"Erro ao salvar: {e}")

    logging.info("Processo concluído! Todas as perguntas foram respondidas.")

# EXECUÇÃO
if __name__ == "__main__":
    processar_dataset_existente()
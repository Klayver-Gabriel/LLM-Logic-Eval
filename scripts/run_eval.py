import logging
import sys
import pandas as pd
from pathlib import Path
import time

THIS_FOLDER = Path(__file__).parent

# Detecta se está dentro da pasta scripts ou raiz
if THIS_FOLDER.name == 'scripts':
    PROJECT_ROOT = THIS_FOLDER.parent
else:
    PROJECT_ROOT = THIS_FOLDER
    
sys.path.append(str(PROJECT_ROOT / 'src'))

try:
    from engine import ApiKeyManager, make_api_call
except ImportError as e:
    print(f"Erro de Importação: {e}")
    sys.exit(1)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%H:%M:%S')


ARQUIVO_ENTRADA = "scripts/analise.xlsx"
ARQUIVO_SAIDA = "scripts/analise.xlsx"

MODELS_TO_RUN = {
    "flash_answer": "models/gemini-2.5-flash",
    "pro_answer":   "models/gemini-2.5-pro"
}

# LIMPEZA DA RESPOSTA
def limpar_resposta(texto, task_type):
    if not texto:
        return "Erro"

    texto = str(texto).strip()

    if task_type == "BQA":
        t = texto.lower()
        if "sim" in t:  return "Sim"
        if "não" in t or "nao" in t: return "Não"
        return "Indeterminado"

    # MCQA
    return texto.replace("\n", " ").strip()

# PROCESSAMENTO DO EXCEL
def processar_dataset_existente():
    input_path = PROJECT_ROOT / ARQUIVO_ENTRADA
    output_path = PROJECT_ROOT / ARQUIVO_SAIDA

    if not input_path.exists():
        logging.critical(f"Arquivo não encontrado: {input_path}")
        return

    logging.info(f"Lendo dataset: {input_path}")

    try:
        df = pd.read_excel(input_path)
    except Exception as e:
        logging.error(f"Erro ao abrir Excel: {e}")
        return

    # Garante colunas de respostas
    for col in MODELS_TO_RUN.keys():
        if col not in df.columns:
            df[col] = None

    # Conecta chaves
    try:
        key_manager = ApiKeyManager()
    except Exception as e:
        logging.error(f"Erro ao carregar chaves: {e}")
        return

    total = len(df)
    logging.info(f"Iniciando avaliação de {total} linhas...")

    # LOOP PRINCIPAL
    for index, row in df.iterrows():

        ja_tem_flash = pd.notna(row.get("flash_answer")) and str(row.get("flash_answer")) not in ["Erro", "Erro_Quota"]
        ja_tem_pro   = pd.notna(row.get("pro_answer"))   and str(row.get("pro_answer"))   not in ["Erro", "Erro_Quota"]

        if ja_tem_flash and ja_tem_pro:
            continue

        logging.info(f"--- Processando item {index+1}/{total} ---")

        contexto = row.get("context", "")
        pergunta = row.get("question", "")
        tipo     = row.get("task_type", "MCQA")
        opcoes   = row.get("options", [])

        # GERANDO O PROMPT CORRETO (BQA / MCQA)
        if tipo == "BQA":  # Boolean Question Answering
            prompt = (
                f"CONTEXTO: {contexto}\n"
                f"PERGUNTA: {pergunta}\n"
                "Responda APENAS com 'Sim' ou 'Não'."
            )

        else:  # MCQA
            if isinstance(opcoes, list) and len(opcoes) > 0:
                lista_opcoes = "\n".join(
                    [f"{chr(65+i)}) {op}" for i, op in enumerate(opcoes)]
                )
                prompt = (
                    "Atue como um motor lógico.\n"
                    f"PREMISSAS: {contexto}\n"
                    f"PERGUNTA: {pergunta}\n"
                    f"OPÇÕES:\n{lista_opcoes}\n"
                    "Responda apenas com a letra correta (A, B, C...)."
                )
            else:
                # Fallback MCQA sem opções
                prompt = (
                    "Atue como um motor lógico.\n"
                    f"PREMISSAS: {contexto}\n"
                    f"TAREFA: {pergunta}\n"
                    "Responda apenas com a conclusão."
                )

        salvar_agora = False

        # LOOP DOS MODELOS (flash / pro)
        for coluna_excel, modelo_api in MODELS_TO_RUN.items():

            valor_atual = row.get(coluna_excel)

            if pd.notna(valor_atual) and str(valor_atual) not in ["Erro", "Erro_Quota"]:
                continue

            sucesso = False
            tentativas = 0
            max_tentativas = 5

            while not sucesso:
                try:
                    tentativas += 1
                    resposta_raw = make_api_call(
                        key_manager, modelo_api, prompt, call_purpose=f"Row {index}"
                    )

                    if resposta_raw is None:
                        if tentativas >= max_tentativas:
                            df.at[index, coluna_excel] = "Erro_Quota"
                            salvar_agora = True
                            sucesso = True
                        else:
                            tempo_espera = 60 * (2 ** (tentativas - 1))
                            logging.warning(f"⚠ Quota excedida. Aguardando {tempo_espera}s...")
                            time.sleep(tempo_espera)
                    else:
                        resposta_limpa = limpar_resposta(resposta_raw, tipo)
                        df.at[index, coluna_excel] = resposta_limpa
                        salvar_agora = True
                        sucesso = True

                except Exception as e:
                    logging.error(f"Erro inesperado: {e}")
                    df.at[index, coluna_excel] = "Erro"
                    sucesso = True
                    time.sleep(5)

        # SALVAMENTO COM PAUSA
        if salvar_agora:
            try:
                df.to_excel(output_path, index=False)
                logging.info("Salvo. Pausando 20s para segurança...")
                time.sleep(20)
            except PermissionError:
                logging.warning(f"⚠ Feche o Excel '{ARQUIVO_SAIDA}' para salvar!")
            except Exception:
                pass

    logging.info("Processo concluído!")


if __name__ == "__main__":
    processar_dataset_existente()

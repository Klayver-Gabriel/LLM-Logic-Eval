import logging
import sys
import json
import pandas as pd
from pathlib import Path
import os
import hashlib
import ast
import time
import re

THIS_FOLDER = Path(__file__).resolve().parent

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

ARQUIVO_FINAL = "analise.xlsx"


MODELS_TO_RUN = {
    "flash_answer": "models/gemini-2.5-flash", 
    "pro_answer":   "models/gemini-2.5-pro"
}

MODEL_MIN_DELAY = {
    "flash": 8,   
    "pro": 45     
}

# Salvar a cada N linhas alteradas 
SAVE_EVERY = 5


def gerar_id(contexto, pergunta):
    base = (str(contexto) + str(pergunta)).encode("utf-8")
    return hashlib.md5(base).hexdigest()

def extrair_dados_do_json(caminho_arquivo, dados_json):
    itens = []
    nome_regra = caminho_arquivo.parent.name
    
    # Cria colunas vazias para os modelos
    respostas_vazias = {key: None for key in MODELS_TO_RUN.keys()}

    # Lógica para datasets tipo MCQA
    if "mcq_samples" in dados_json:
        for sample in dados_json["mcq_samples"]:
            contexto = sample.get("context")
            pergunta = sample.get("question")
            opcoes = sample.get("options", [])
            idx = sample.get("answer")
            gabarito = opcoes[idx] if isinstance(idx, int) and idx < len(opcoes) else None

            item = {
                "id": gerar_id(contexto, pergunta),
                "task_type": "MCQA",
                "rule_name": nome_regra,
                "context": contexto,
                "question": pergunta,
                "options": opcoes,
                "correct_answer": gabarito
            }
            item.update(respostas_vazias)
            itens.append(item)
        return itens

    # Lógica para datasets mistos/BQA
    if "samples" in dados_json:
        for sample in dados_json["samples"]:
            contexto = sample.get("context")

            if "qa_pairs" in sample:
                for pair in sample["qa_pairs"]:
                    pergunta = pair.get("question")
                    gabarito = pair.get("answer")

                    item = {
                        "id": gerar_id(contexto, pergunta),
                        "task_type": "BQA",
                        "rule_name": nome_regra,
                        "context": contexto,
                        "question": pergunta,
                        "options": None,
                        "correct_answer": gabarito
                    }
                    item.update(respostas_vazias)
                    itens.append(item)
            else:
                pergunta = sample.get("question")
                opcoes = sample.get("options", [])
                idx = sample.get("answer")
                gabarito = opcoes[idx] if isinstance(idx, int) and idx < len(opcoes) else None

                item = {
                    "id": gerar_id(contexto, pergunta),
                    "task_type": "MCQA",
                    "rule_name": nome_regra,
                    "context": contexto,
                    "question": pergunta,
                    "options": opcoes,
                    "correct_answer": gabarito
                }
                item.update(respostas_vazias)
                itens.append(item)

    return itens

def rastrear_diretorios():
    pasta_output = PROJECT_ROOT / "output"
    if not pasta_output.exists():
        logging.error(f"Pasta output não encontrada em: {pasta_output}")
        return pd.DataFrame()

    registros = []
    todos = list(pasta_output.rglob("*.json"))
    logging.info(f"Lendo {len(todos)} arquivos JSON...")

    for caminho in todos:
        try:
            with open(caminho, 'r', encoding='utf-8') as f:
                dados = json.load(f)
            registros.extend(extrair_dados_do_json(caminho, dados))
        except Exception as e:
            logging.error(f"Erro ao ler {caminho.name}: {e}")

    return pd.DataFrame(registros)

def carregar_progresso_existente(df, caminho_excel):
    if not caminho_excel.exists():
        return df, 0

    try:
        logging.info(f"Carregando progresso salvo de: {caminho_excel.name}...")
        df_salvo = pd.read_excel(caminho_excel)

        colunas_modelos = list(MODELS_TO_RUN.keys())
        for col in colunas_modelos:
            if col not in df_salvo.columns:
                df_salvo[col] = None
        
        # Atualiza o DataFrame principal com o que já foi feito
        df.set_index("id", inplace=True)
        df_salvo.set_index("id", inplace=True)
        df.update(df_salvo[colunas_modelos])
        df.reset_index(inplace=True)
        
        # Conta quantos estão totalmente prontos
        mask_completo = pd.Series([True] * len(df))
        for col in colunas_modelos:
            mask_col = (df[col].notna()) & (~df[col].astype(str).isin(["Erro", "Erro_Quota", "None", "nan"]))
            mask_completo = mask_completo & mask_col
        
        feitos = df[mask_completo].shape[0]
        return df, feitos
    except Exception as e:
        logging.warning(f"Falha ao carregar progresso (iniciando do zero): {e}")
        return df, 0
    

def limpar_resposta(texto, tipo):
    if not texto:
        return "Erro"

    # Converte para string e remove espaços extras
    texto = str(texto).strip()

    # Limpeza para Sim/Não (BQA)
    if tipo == "BQA":
        t = texto.lower()
        # Remove pontuação para o modelo não confundir "Sim." com erro
        t = re.sub(r'[^\w\s]', '', t)
        
        if "sim" in t: return "Sim"
        if "não" in t or "nao" in t: return "Não"
        return "Indeterminado"

    #  Limpeza para Múltipla Escolha (MCQA) 
    if tipo == "MCQA":
        match_forte = re.search(r"[\(\*\s]([A-E])[\)\.\*]", texto, re.IGNORECASE)
        if match_forte:
            return match_forte.group(1).upper()
        
        # Procura a letra isolada no início ou fim
        match_iso = re.search(r"\b([A-E])\b", texto, re.IGNORECASE)
        if match_iso:
            return match_iso.group(1).upper()

        match_final = re.findall(r"([A-E])", texto.upper())
        if match_final:
            # Pega a última letra encontrada (geralmente a conclusão) ou a primeira se for curta
            if len(texto) < 10: 
                return match_final[0] 
            return match_final[-1]    

    # Se não achou nada parecido com A, B, C, D, E, devolve o texto original 
    return texto

def run_pipeline():
    # Carrega dados brutos dos JSONs
    df = rastrear_diretorios()
    if df.empty:
        logging.error("Nenhum JSON encontrado.")
        return

    # Converte strings de listas de volta para listas reais
    if 'options' in df.columns:
        df['options'] = df['options'].apply(
            lambda x: ast.literal_eval(x) if isinstance(x, str) else (x if isinstance(x, list) else [])
        )

    caminho_completo = THIS_FOLDER / ARQUIVO_FINAL

    # Limpa duplicatas e carrega progresso anterior
    df.drop_duplicates(subset=["id"], keep="first", inplace=True)
    df, ja = carregar_progresso_existente(df, caminho_completo)
    
    total = len(df)
    logging.info(f"Total de itens na base: {total}")

    try:
        key_manager = ApiKeyManager()
    except Exception as e:
        logging.error(f"Erro ao iniciar KeyManager: {e}")
        return

    colunas_ordenadas = sorted(MODELS_TO_RUN.items(), key=lambda x: "pro" in x[1].lower())

    for col, modelo in colunas_ordenadas:
        logging.info(f"\n{'='*50}")
        logging.info(f"INICIANDO CICLO PARA: {modelo} (Coluna: {col})")
        logging.info(f"{'='*50}")
        
        # Define delay baseado no tipo do modelo
        delay_base = MODEL_MIN_DELAY["pro"] if "pro" in modelo.lower() else MODEL_MIN_DELAY["flash"]
        
        # Filtra apenas linhas que precisam ser processadas para este modelo específico
        linhas_pendentes = df[
            (pd.isna(df[col])) | 
            (df[col].astype(str).isin(["Erro", "Erro_Quota", "None", "nan"]))
        ].index
        
        total_pendente = len(linhas_pendentes)
        if total_pendente == 0:
            logging.info(f"Nada pendente para {modelo}.")
            continue

        logging.info(f"Itens restantes para {modelo}: {total_pendente}")
        
        count_save = 0
        
        for i, idx in enumerate(linhas_pendentes):
            row = df.loc[idx]
            
            # Montagem do Prompt
            tipo = row["task_type"]
            if tipo == "BQA":
                prompt = f"CONTEXTO: {row['context']}\nPERGUNTA: {row['question']}\nResponda APENAS com 'Sim' ou 'Não'."
            else:
                str_opts = ""
                if isinstance(row["options"], list) and len(row["options"]) > 0:
                    str_opts = "\n".join([f"{chr(65+k)}) {op}" for k, op in enumerate(row["options"])])
                    prompt = f"Atue como um motor lógico.\nPREMISSAS: {row['context']}\nPERGUNTA: {row['question']}\nOPÇÕES:\n{str_opts}\nResponda somente com a letra da alternativa correta."
                else:
                    prompt = f"Atue como motor lógico.\nPREMISSAS: {row['context']}\nPERGUNTA: {row['question']}\nResponda somente com a conclusão final."

            # Delay inteligente: Só espera se não for a primeira chamada
            if i > 0: 
                logging.info(f"{modelo}: Esperando {delay_base}s...")
                time.sleep(delay_base)

            logging.info(f"[{modelo}] Processando item {i+1}/{total_pendente}...")

            sucesso = False
            tentativas = 0
            max_tentativas = 3 # Tenta 3 vezes a mesma linha antes de desistir
            
            while not sucesso and tentativas < max_tentativas:
                tentativas += 1
                try:
                    resp_raw = make_api_call(key_manager, modelo, prompt, call_purpose=f"{col} - item {i}")
                    
                    if resp_raw is None:
                        logging.warning(f"API retornou VAZIO para {modelo}. Pausando 70s para esfriar...")
                        time.sleep(70) 
                        
                        # Se falhou na última tentativa, marca como erro
                        if tentativas == max_tentativas:
                            df.at[idx, col] = "Erro_Quota"
                    else:
                        # Sucesso!
                        df.at[idx, col] = limpar_resposta(resp_raw, tipo)
                        logging.info(f"OK")
                        sucesso = True

                except Exception as e:
                    logging.error(f"Erro inesperado no loop: {e}")
                    df.at[idx, col] = "Erro"
                    break
            
            # Salvar incrementalmente
            count_save += 1
            if count_save >= SAVE_EVERY:
                try:
                    df.to_excel(caminho_completo, index=False)
                    logging.info("Progresso salvo no Excel.")
                    count_save = 0
                except PermissionError:
                    logging.warning("Excel aberto! Não foi possível salvar agora (dados seguem na memória).")

        # Salva ao final de cada modelo completo
        try:
            df.to_excel(caminho_completo, index=False)
            logging.info(f"Ciclo do modelo {modelo} finalizado e salvo com sucesso.")
        except:
            logging.error("Erro ao salvar final do ciclo.")

    logging.info(" PIPELINE FINALIZADO! Todos os modelos processados.")

if __name__ == "__main__":
    run_pipeline()
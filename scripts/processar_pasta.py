import logging
import sys
import json
import pandas as pd
from pathlib import Path
import os


THIS_FOLDER = Path(__file__).parent

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

def extrair_dados_do_json(caminho_arquivo, dados_json):
    itens_extraidos = []
    caminho_str = str(caminho_arquivo).upper()
    tipo_tarefa = "BQA" if "BQA" in caminho_str else "MCQA"
    nome_regra = caminho_arquivo.parent.name

    if isinstance(dados_json, dict) and "samples" in dados_json:
        for sample in dados_json["samples"]:
            contexto = sample.get("context")
            qa_pairs = sample.get("qa_pairs", [])
            for pair in qa_pairs:
                pergunta = pair.get("question")
                gabarito = pair.get("answer")
                if contexto and pergunta:
                    itens_extraidos.append({
                        "id_unico": f"{contexto[:20]}_{pergunta[:20]}", 
                        "task_type": tipo_tarefa,
                        "rule_name": nome_regra,
                        "context": contexto,
                        "question": pergunta,
                        "correct_answer": gabarito,
                        "flash_answer": None,
                        "pro_answer":   None
                    })
    return itens_extraidos

def rastrear_diretorios():
    pasta_output = PROJECT_ROOT / "output"
    registros = []
    todos_arquivos = list(pasta_output.rglob("*.json"))
    logging.info(f"Lendo estrutura de {len(todos_arquivos)} arquivos JSON...")

    for caminho in todos_arquivos:
        try:
            with open(caminho, 'r', encoding='utf-8') as f:
                dados = json.load(f)
            registros.extend(extrair_dados_do_json(caminho, dados))
        except Exception as e:
            logging.error(f"Erro ao ler {caminho.name}: {e}")

    return pd.DataFrame(registros)


def carregar_progresso_existente(df_novo, caminho_excel):
    """
    Pega o DataFrame novo (dos JSONs) e preenche com as respostas
    que já existem no Excel, se houver.
    """
    if not os.path.exists(caminho_excel):
        return df_novo, 0

    try:
        logging.info("Encontrado arquivo existente. Carregando respostas salvas...")
        df_salvo = pd.read_excel(caminho_excel)
        
        # Cria um dicionário de consulta rápida: id_unico -> resposta
        mapa_flash = dict(zip(df_salvo['question'] + df_salvo['context'], df_salvo['flash_answer']))
        mapa_pro = dict(zip(df_salvo['question'] + df_salvo['context'], df_salvo['pro_answer']))

        recuperados = 0
        
        # Atualiza o DF Novo com os dados do Velho
        for index, row in df_novo.iterrows():
            chave = row['question'] + row['context']
            
            # Se já tem resposta salva E ela não é vazia/erro, recupera
            if chave in mapa_flash and pd.notna(mapa_flash[chave]) and mapa_flash[chave] != "Erro":
                df_novo.at[index, 'flash_answer'] = mapa_flash[chave]
                
            if chave in mapa_pro and pd.notna(mapa_pro[chave]) and mapa_pro[chave] != "Erro":
                df_novo.at[index, 'pro_answer'] = mapa_pro[chave]
                
            # Conta se linha está completa
            if pd.notna(df_novo.at[index, 'flash_answer']) and pd.notna(df_novo.at[index, 'pro_answer']):
                recuperados += 1

        return df_novo, recuperados

    except Exception as e:
        logging.warning(f"Não foi possível ler o arquivo antigo ({e}). Começando do zero.")
        return df_novo, 0

def limpar_resposta(texto, task_type):
    if not texto: return "Erro"
    texto = str(texto).strip()
    if task_type == "BQA":
        t = texto.lower()
        if "sim" in t: return "Sim"
        if "não" in t or "nao" in t: return "Não"
        return "Indeterminado"
    return texto.replace("\n", " ").strip()

def run_pipeline():
    # Lê a estrutura atual dos JSONs
    df = rastrear_diretorios()
    if df.empty:
        logging.error("Nenhum JSON encontrado.")
        return

    caminho_final = PROJECT_ROOT / "output" / ARQUIVO_FINAL
    df, ja_feitos = carregar_progresso_existente(df, caminho_final)

    total = len(df)
    faltam = total - ja_feitos
    logging.info(f"Total de Perguntas: {total}")
    logging.info(f"Já processadas: {ja_feitos}")
    logging.info(f"Faltam processar: {faltam}")

    if faltam == 0:
        logging.info("Tudo já está concluído!")
        return

    # Inicializa Chaves
    try:
        key_manager = ApiKeyManager()
    except Exception:
        return

    # Só processa o que falta
    for index, row in df.iterrows():
        
        # Verifica se essa linha já tem as duas respostas
        tem_flash = pd.notna(row['flash_answer']) and row['flash_answer'] != "Erro"
        tem_pro = pd.notna(row['pro_answer']) and row['pro_answer'] != "Erro"

        if tem_flash and tem_pro:
            continue # pula a interação

        logging.info(f"--- Processando item {index+1}/{total} ---")

        tipo = row['task_type']
        prompt = ""
        if tipo == "BQA":
            prompt = f"CONTEXTO: {row['context']}\nPERGUNTA: {row['question']}\nResponda APENAS com 'Sim' ou 'Não'."
        else:
            prompt = f"Atue como um motor lógico.\nPREMISSAS: {row['context']}\nTAREFA: {row['question']}\nResponda apenas com a conclusão."

        # Roda apenas os modelos que faltam
        for col_excel, model_api in MODELS_TO_RUN.items():
            
            
            valor_atual = row[col_excel]
            if pd.notna(valor_atual) and valor_atual != "Erro":
                logging.info(f"   -> {model_api} já respondido. Pulando.")
                continue

            try:
                resp = make_api_call(key_manager, model_api, prompt, call_purpose=f"Row {index}")
            except Exception as e:
                logging.error(f"Erro: {e}")
                resp = "Erro"

            df.at[index, col_excel] = limpar_resposta(resp, tipo)

        if index % 1 == 0: 
            df.to_excel(caminho_final, index=False)
          

    logging.info(f"FINALIZADO COMPLETAMENTE!")

if __name__ == "__main__":
    run_pipeline()
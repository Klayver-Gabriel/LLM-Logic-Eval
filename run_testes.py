import logging
import random
import sys
from pathlib import Path

# --- Configuração de Path ---
# Adiciona a pasta 'src' ao path do Python

PROJECT_ROOT = Path(__file__).parent
sys.path.append(str(PROJECT_ROOT / 'src'))



try:
    #engine.py
    from engine import ApiKeyManager, make_api_call
    
    #config.py
    from config import LOGIC_RULES_CONFIG
    

except ImportError as e:
    print(f"Erro de Importação: {e}")
    print("Certifique-se de que os arquivos 'engine.py' e 'config.py' estão na pasta 'src/'.")
    print("E que 'proposicoes.py' também está na pasta 'src/'.")
    sys.exit(1)


# --- Configuração do Logging ---
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)



# INÍCIO DO SCRIPT DE TESTAGEM
# (Limpam a saída da LLM para True/False/None)

def parse_llm_resposta_direta(texto: str | None) -> bool | None:
    """Converte 'Sim'/'Não' da LLM para um booleano."""
    if texto is None: return None
    texto_limpo = texto.strip().lower()
    if texto_limpo.startswith("sim"):
        return True
    if texto_limpo.startswith("não"):
        return False
    return None # Resposta ambígua

def parse_llm_resposta_estilo_z3(texto: str | None) -> bool | None:
    """Converte 'sat'/'unsat' da LLM para um booleano."""
    if texto is None: return None
    texto_limpo = texto.strip().lower()
    if "unsat" in texto_limpo:
        return True
    if "sat" in texto_limpo:
        return False
    return None 

# --- FUNÇÃO AUXILIAR: EXTRATOR DE CONCLUSÃO ---

def extrair_conclusao_simples(pergunta_instanciada: str) -> str | None:
    """Tenta extrair a conclusão de dentro do texto da pergunta."""
    pergunta_limpa = pergunta_instanciada.strip("?").strip()
    prefixos = [
        "Isso implica que ",
        "Podemos inferir que ",
        "isso significa que "
    ]
    for p in prefixos:
        if p in pergunta_limpa:
            conclusao = pergunta_limpa.split(p, 1)[-1]
            return conclusao
    return None


# (Formatam os prompts e usam sua função 'make_api_call')

def run_evaluation_direct(key_manager, model_name, contexto, pergunta):
    """Formata e executa o prompt direto (Sim/Não)."""
    prompt = f"""Considere o seguinte contexto:
{contexto}

Pergunta: {pergunta}

Responda apenas 'Sim' ou 'Não'.
"""
    # Usa API!
    raw_response = make_api_call(key_manager, model_name, prompt, call_purpose="Avaliação Direta")
    return raw_response, parse_llm_resposta_direta(raw_response)

def run_evaluation_z3_style(key_manager, model_name, contexto, conclusao):
    """Formata e executa o prompt estilo Z3 (sat/unsat)."""
    prompt = f"""Considere o formato SMT-LIB. Para verificar se uma conclusão é consequência de premissas, checa-se se (Premissas E (NÃO Conclusão)) é 'sat' ou 'unsat'.

Premissas:
{contexto}

Conclusão: {conclusao}

Qual seria o resultado dessa verificação? Responda apenas 'sat' ou 'unsat'.
"""
    # Usa a função API!
    raw_response = make_api_call(key_manager, model_name, prompt, call_purpose="Avaliação Estilo Z3")
    return raw_response, parse_llm_resposta_estilo_z3(raw_response)

# "CONDUTOR" DA AVALIAÇÃO ---

def run_evaluation_pipeline(model_name="gemini-1.5-flash"):
    """
    Função principal que roda todo o pipeline de avaliação.
    """
    logging.info("Iniciando pipeline de avaliação...")
    
    # 1. Inicializa seu KeyManager
    try:
        key_manager = ApiKeyManager()
        logging.info(f"{len(key_manager)} chaves de API carregadas com sucesso.")
    except Exception as e:
        logging.critical(f"Falha ao iniciar o ApiKeyManager: {e}")
        logging.critical("Verifique se o arquivo 'api_keys.json' existe na pasta raiz.")
        return

    # 2. Configurações do Teste
    # CUIDADO: Seu cooldown é de 35s. 1 instância x 9 regras x ~4 perguntas = 36 testes.
    # 36 testes * 2 métodos = 72 chamadas de API.
    # 72 * 35s = 2520 segundos = ~42 minutos.
    # Comece com 1 instância para testar.
    N_INSTANCIAS_POR_PERGUNTA = 1 
    
    resultados_finais = []
    
    # Loop de Geração e Teste
    for nome_regra, config_regra in LOGIC_RULES_CONFIG["PL"].items():
        logging.info(f"Processando Regra: {nome_regra}")
        
        for bqa in config_regra["bqa_templates"]:
            ground_truth = (bqa["answer"].lower() == "sim")
            
            for template_pergunta in bqa["question"]:
                if not isinstance(template_pergunta, str):
                    continue # Pula perguntas complexas por enquanto
                    
                for i in range(N_INSTANCIAS_POR_PERGUNTA):
                    # Instancia o template com frases
                    
                    contexto_txt = config_regra["template_context"]
                    pergunta_txt = template_pergunta
                    for token, valor in mapa_substituicao.items():
                        contexto_txt = contexto_txt.replace(token, f"'{valor}'")
                        pergunta_txt = pergunta_txt.replace(token, f"'{valor}'")
                    
                    logging.info(f"  Instância {i+1} (GT: {ground_truth}): {pergunta_txt[:50]}...")
                    
                    # --- Execução ---
                    
                    # Teste 1: Método Direto
                    raw_direto, parsed_direto = run_evaluation_direct(key_manager, model_name, contexto_txt, pergunta_txt)
                    
                    # Teste 2: Método Estilo Z3
                    raw_z3, parsed_z3 = None, None
                    conclusao_txt = extrair_conclusao_simples(pergunta_txt)
                    if conclusao_txt:
                        raw_z3, parsed_z3 = run_evaluation_z3_style(key_manager, model_name, contexto_txt, conclusao_txt)
                    else:
                        logging.warning(f"  -> Pulando teste 'Estilo Z3' (não foi possível extrair conclusão).")

                    # --- Agregação ---
                    resultados_finais.append({
                        "regra": nome_regra,
                        "ground_truth": ground_truth,
                        "llm_direto_parsed": parsed_direto,
                        "llm_z3_parsed": parsed_z3,
                        "correto_direto": parsed_direto == ground_truth,
                        "correto_z3": parsed_z3 == ground_truth if parsed_z3 is not None else None,
                    })

    # Relatório Final
    print("\n" + "="*50)
    print("Relatório Final de Acurácia")
    print("="*50)
    
    total_testes = len(resultados_finais)
    if total_testes == 0:
        print("Nenhum teste foi executado.")
        return

    # Acurácia - Método Direto
    acertos_direto = sum(1 for r in resultados_finais if r["correto_direto"])
    
    # Acurácia - Método Estilo Z3
    testes_z3_validos = [r for r in resultados_finais if r["llm_z3_parsed"] is not None]
    acertos_z3 = sum(1 for r in testes_z3_validos if r["correto_z3"])
    total_z3 = len(testes_z3_validos)

    print(f"Total de Testes Gerados: {total_testes}")
    print(f"\n--- Método 1: Direto (Sim/Não) ---")
    print(f"Acurácia: {acertos_direto / total_testes:.2%}")

    print(f"\n--- Método 2: Estilo Z3 (sat/unsat) ---")
    if total_z3 > 0:
        print(f"(Testes válidos: {total_z3} de {total_testes})")
        print(f"Acurácia: {acertos_z3 / total_z3:.2%}")
    else:
        print("Nenhum teste 'Estilo Z3' pôde ser executado.")

    print("\n" + "="*50)
    print("Detalhe das Falhas (Método Direto)")
    print("="*50)
    falhas = 0
    for r in resultados_finais:
        if not r["correto_direto"]:
            falhas += 1
            print(f"Falha - Regra: {r['regra']} (Esperado: {r['ground_truth']}, Recebido: {r['llm_direto_parsed']})")
    if falhas == 0:
        print("Nenhuma falha! (Método Direto)")


# --- Ponto de Entrada: Roda o script ---
if __name__ == "__main__":
    run_evaluation_pipeline()

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import sys
from pathlib import Path

THIS_SCRIPT_DIR = Path(__file__).resolve().parent

PROJECT_ROOT = THIS_SCRIPT_DIR.parent

sys.path.append(str(PROJECT_ROOT / 'src'))

# Nome exato do arquivo gerado pelo processar_pasta.py
NOME_ARQUIVO = "analise.xlsx"

CAMINHO_ARQUIVO = PROJECT_ROOT / "output" / NOME_ARQUIVO


# Nomes das colunas no Excel
COL_FLASH = "flash_answer"
COL_PRO = "pro_answer"
COL_GABARITO = "correct_answer"


if not CAMINHO_ARQUIVO.exists():
    print(f"ERRO: O arquivo não foi encontrado em: {CAMINHO_ARQUIVO}")
    print("Certifique-se de ter rodado o 'processar_pasta.py' primeiro.")
    sys.exit(1)

print(f"Lendo dados de: {CAMINHO_ARQUIVO.name}...")
try:
    df = pd.read_excel(CAMINHO_ARQUIVO)
except Exception as e:
    print(f"ERROR ao abrir excel: {e}")
    sys.exit(1)

cols_para_limpar = [COL_GABARITO, COL_FLASH, COL_PRO]
for col in cols_para_limpar:
    if col in df.columns:
        df[col] = df[col].astype(str).str.lower().str.strip()
    else:
        print(f"AVISO CRÍTICO: Coluna '{col}' não encontrada no Excel!")
        print(f"   Colunas disponíveis: {list(df.columns)}")
        sys.exit(1) 

print(f"Dados carregados: {len(df)} linhas.")

# CÁLCULO DE ERROS

# Cria colunas de Erro (True = Errou, False = Acertou)
df['erro_flash'] = df[COL_GABARITO] != df[COL_FLASH]
df['erro_pro']   = df[COL_GABARITO] != df[COL_PRO]

# Agrupa por tipo de tarefa (BQA vs MCQA)
# A média de True/False resulta na porcentagem de True (Erros)
taxa_erro = df.groupby('task_type')[['erro_flash', 'erro_pro']].mean()


taxa_erro.columns = ['Gemini Flash', 'Gemini Pro']

# GRÁFICO 1: TAXA DE ERRO GERAL
if not taxa_erro.empty:
    plt.figure(figsize=(10, 6))
    
    # Plota
    ax = taxa_erro.plot(kind='bar', color=['#4CAF50', '#F44336'], edgecolor='black', width=0.7)

    plt.title('Taxa de Erro por Modelo (Menor é Melhor)', fontsize=16, fontweight='bold')
    plt.ylabel('Porcentagem de Erro', fontsize=12)
    plt.xlabel('Tipo de Tarefa', fontsize=12)
    plt.xticks(rotation=0)
    plt.grid(axis='y', linestyle='--', alpha=0.3)
    plt.legend(title='Modelo')

    # Eixo Y em porcentagem
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))

    # Rótulos nas barras
    for container in ax.containers:
        ax.bar_label(container, fmt='{:.1%}', padding=3, fontweight='bold')

    plt.tight_layout()
    print("Gerando Gráfico 1: Taxa de Erro Geral...")
    plt.show()
else:
    print("Sem dados suficientes para o Gráfico 1.")

# GRÁFICO 2: ANÁLISE DE BQA (Falsos Positivos/Negativos)
df_bqa = df[df['task_type'].str.upper() == 'BQA'].copy()

if not df_bqa.empty:
    def classificar_falha(row, col_modelo):
        resposta_ia = row[col_modelo]
        gabarito = row[COL_GABARITO]
        
        # Ignora se a IA deu erro de API
        if resposta_ia == 'erro' or resposta_ia == 'indeterminado':
            return None

        if resposta_ia == gabarito:
            return None # Acertou
        
        if gabarito == 'não' and resposta_ia == 'sim':
            return "Falso Positivo\n(Alucinação)"
        
        if gabarito == 'sim' and resposta_ia == 'não':
            return "Falso Negativo\n(Ceticismo)"
            
        return "Outro Erro"

    # Conta os tipos de erro
    dados_grafico_2 = pd.DataFrame()

    for nome_legenda, col_excel in [('Gemini Flash', COL_FLASH), ('Gemini Pro', COL_PRO)]:
        # Classifica cada linha
        erros = df_bqa.apply(classificar_falha, args=(col_excel,), axis=1)
        # Conta e normaliza (%)
        contagem = erros.value_counts(normalize=True)
        dados_grafico_2[nome_legenda] = contagem

    # Plota
    if not dados_grafico_2.empty:
        plt.figure(figsize=(10, 6))
        ax2 = dados_grafico_2.plot(kind='bar', color=['#2196F3', '#FF9800'], edgecolor='black')
        
        plt.title('Tipos de Erro em Lógica Binária (BQA)', fontsize=16, fontweight='bold')
        plt.ylabel('% do Total de Erros', fontsize=12)
        plt.xlabel('Tipo de Falha', fontsize=12)
        plt.xticks(rotation=0)
        plt.legend(title='Modelo')
        
        ax2.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
        
        for container in ax2.containers:
            ax2.bar_label(container, fmt='{:.1%}', padding=3)

        plt.grid(axis='y', linestyle='--', alpha=0.3)
        plt.tight_layout()
        print("Gerando Gráfico 2: Tipos de Erro (Alucinação vs Ceticismo)...")
        plt.show()
    else:
        print("Incrível! Nenhum erro do tipo Sim/Não encontrado para gerar o Gráfico 2.")
else:
    print("Nenhuma tarefa BQA encontrada no Excel.")
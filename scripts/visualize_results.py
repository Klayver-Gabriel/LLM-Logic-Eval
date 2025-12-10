import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import sys
import re
from pathlib import Path

THIS_SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = THIS_SCRIPT_DIR.parent
sys.path.append(str(PROJECT_ROOT / 'src'))

# Arquivo de dados (Excel)
NOME_ARQUIVO = "analise.xlsx"
CAMINHO_ARQUIVO = PROJECT_ROOT / "scripts" / NOME_ARQUIVO

# Pasta para salvar gráficos
PASTA_GRAFICOS = THIS_SCRIPT_DIR / "graficos"
PASTA_GRAFICOS.mkdir(parents=True, exist_ok=True)

COL_FLASH = "flash_answer"
COL_PRO = "pro_answer"
COL_GABARITO = "correct_answer"

# CARREGAMENTO
if not CAMINHO_ARQUIVO.exists():
    print(f"Arquivo não encontrado: {CAMINHO_ARQUIVO}")
    sys.exit(1)

print(f"Lendo dados de: {CAMINHO_ARQUIVO.name}...")
df = pd.read_excel(CAMINHO_ARQUIVO)

# Garante colunas corretas
for col in [COL_GABARITO, COL_FLASH, COL_PRO]:
    if col not in df.columns:
        df[col] = ""
    else:
        df[col] = df[col].astype(str)

print(f"Dados carregados: {len(df)} linhas.")


# FUNÇÕES AUXILIARES
def normalizar_texto(texto):
    if pd.isna(texto) or texto.lower() in ["nan", "none"]:
        return ""
    texto_limpo = re.sub(r'[^\w\s]', '', str(texto).lower())
    return " ".join(texto_limpo.split())

def verificar_acerto(row, col_ia):
    resp = normalizar_texto(row[col_ia])
    gab = normalizar_texto(row[COL_GABARITO])
    tipo = row.get("task_type", "MCQA").upper()

    if resp in ["erro", "erro_quota", "indeterminado", "", "none"]:
        return False

    if tipo == "BQA":
        palavras_ia = resp.split()
        if gab == "sim": return "sim" in palavras_ia and "não" not in palavras_ia
        if gab in ["não", "nao"]: return "não" in palavras_ia or "nao" in palavras_ia
        return resp == gab
    else:
        return gab in resp


# AVALIAÇÃO
df['acerto_flash'] = df.apply(lambda row: verificar_acerto(row, COL_FLASH), axis=1)
df['acerto_pro']   = df.apply(lambda row: verificar_acerto(row, COL_PRO), axis=1)
df['erro_flash'] = ~df['acerto_flash']
df['erro_pro']   = ~df['acerto_pro']


# GRÁFICO 1: TAXA DE ERRO POR TIPO DE TAREFA
taxa_erro = df.groupby('task_type')[['erro_flash', 'erro_pro']].mean()
taxa_erro.columns = ['Gemini Flash', 'Gemini Pro']

if not taxa_erro.empty:
    plt.figure(figsize=(10,6))
    ax = taxa_erro.plot(kind='bar', color=['#4CAF50','#F44336'], edgecolor='black', width=0.7)
    plt.title('Taxa de Erro (Validação Inteligente)', fontsize=16, fontweight='bold')
    plt.ylabel('Taxa de Erro (%)', fontsize=12)
    plt.grid(axis='y', linestyle='--', alpha=0.3)
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    for c in ax.containers: ax.bar_label(c, fmt='{:.1%}', padding=3, fontweight='bold')
    plt.tight_layout()
    caminho_img1 = PASTA_GRAFICOS / "grafico_taxa_erro.png"
    plt.savefig(caminho_img1, dpi=150)
    plt.close()
    print(f"Gráfico salvo: {caminho_img1}")

# GRÁFICO 2: TIPOS DE ERRO BQA
df_bqa = df[df['task_type'].str.upper() == 'BQA'].copy()
if not df_bqa.empty:
    def classificar_erro_bqa(row, col):
        if verificar_acerto(row, col): return None
        resp, gab = normalizar_texto(row[col]), normalizar_texto(row[COL_GABARITO])
        if gab in ['não', 'nao'] and 'sim' in resp: return "Alucinação (Falso Positivo)"
        if gab == 'sim' and ('não' in resp or 'nao' in resp): return "Ceticismo (Falso Negativo)"
        return "Outro Erro"

    dados_grafico_2 = pd.DataFrame()
    for nome, col in [('Flash', COL_FLASH), ('Pro', COL_PRO)]:
        dados_grafico_2[nome] = df_bqa.apply(lambda r: classificar_erro_bqa(r, col), axis=1).value_counts(normalize=True)

    if not dados_grafico_2.empty:
        plt.figure(figsize=(10,6))
        ax2 = dados_grafico_2.plot(kind='bar', color=['#2196F3','#FF9800'], edgecolor='black')
        plt.title('Tipos de Erro BQA', fontsize=16, fontweight='bold')
        plt.ylabel('% do Total de Erros', fontsize=12)
        plt.grid(axis='y', linestyle='--', alpha=0.3)
        ax2.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
        for c in ax2.containers: ax2.bar_label(c, fmt='{:.1%}', padding=3)
        plt.tight_layout()
        caminho_img2 = PASTA_GRAFICOS / "grafico_tipos_erro_bqa.png"
        plt.savefig(caminho_img2, dpi=150)
        plt.close()
        print(f"Gráfico salvo: {caminho_img2}")

# GRÁFICO 3: ACURÁCIA GERAL (MCQA + BQA)
acuracia_total = pd.DataFrame({
    'Gemini Flash': [df['acerto_flash'].mean()],
    'Gemini Pro': [df['acerto_pro'].mean()]
}, index=['Total'])

plt.figure(figsize=(8,5))
ax3 = acuracia_total.plot(kind='bar', color=['#4CAF50','#F44336'], edgecolor='black', width=0.5)
plt.title('Acurácia Geral (Todas Tarefas)', fontsize=16, fontweight='bold')
plt.ylabel('Acurácia (%)', fontsize=12)
plt.ylim(0,1)
plt.grid(axis='y', linestyle='--', alpha=0.3)
ax3.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
for c in ax3.containers: ax3.bar_label(c, fmt='{:.1%}', padding=3)
plt.tight_layout()
caminho_img3 = PASTA_GRAFICOS / "grafico_acuracia_geral.png"
plt.savefig(caminho_img3, dpi=150)
plt.close()
print(f"Gráfico salvo: {caminho_img3}")

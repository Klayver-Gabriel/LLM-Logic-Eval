# src/prompts.py
"""
Este arquivo centraliza os prompts para a ETAPA 1. Cada prompt é projetado
para instruir o LLM a gerar um ARRAY de bancos de sentenças para uma regra específica.
"""

DEFAULT_PROMPT = """Sua tarefa é gerar um array JSON contendo {num_instances} objetos.
Cada objeto deve ter as chaves: {propositions}.
**Instrução Crucial de Causalidade para cada objeto:** A sentença para a chave 'p' deve descrever uma causa ou condição que levaria de forma plausível e lógica à sentença da chave 'q'. A relação "Se p, então q" deve fazer sentido no mundo real. Tente variar os temas entre os objetos no array.
**IMPORTANTE:** Forneça APENAS o array JSON bruto, sem nenhum texto antes ou depois, e sem markdown."""

PROMPT_BANK = {
    # ============================ PL ============================
    "PL/Hypothetical_Syllogism": """Sua tarefa é gerar um array JSON contendo {num_instances} objetos. Cada objeto deve ter as chaves: {propositions}.
**Instrução Crucial de Cadeia Causal para cada objeto:** Você deve criar uma cadeia lógica de três eventos: 'p' causa 'q', e 'q' causa 'r'.
**Exemplo:** [{{"p": "Eu estudei para a prova.", "q": "Eu passei na prova.", "r": "Eu ganhei um presente."}}]
**IMPORTANTE:** Forneça APENAS o array JSON bruto, sem markdown.""",

    "PL_DILEMMAS": """Sua tarefa é gerar um array JSON contendo {num_instances} objetos. Cada objeto deve ter as chaves: {propositions}.
**Instrução Crucial de Alternativas Temáticas para cada objeto:** Cada objeto deve conter dois cenários de causa e efeito (p->q e r->s) que sejam alternativas relacionadas ao mesmo tema.
**Exemplo:** [{{"p": "Eu escolho ir à praia", "q": "Eu vou nadar", "r": "Eu escolho ir à montanha", "s": "Eu vou fazer uma trilha"}}]
**IMPORTANTE:** Forneça APENAS o array JSON bruto, sem markdown.""",

    # ============================ FOL ============================
    "FOL/Universal_Instantiation": """Sua tarefa é gerar um array JSON contendo {num_instances} objetos. Cada objeto deve ter as chaves: {propositions}.
**Instrução sobre Papéis para cada objeto:** 'entidades_plural' (ex: "cães"), 'entidade_singular' (ex: "cão"), 'propriedade' (ex: "leais"), 'a' (ex: "Rex").
**Exemplo:** [{{"entidades_plural": "gatos", "entidade_singular": "gato", "propriedade": "independentes", "a": "Bichano"}}]
**IMPORTANTE:** Forneça APENAS o objeto JSON bruto, sem markdown.""",
    
    "FOL/Existential_Generalization": """Sua tarefa é gerar um array JSON contendo {num_instances} objetos. Cada objeto deve ter as chaves: {propositions}.
**Instrução sobre Papéis para cada objeto:** 'entidade_singular' (ex: "pássaro"), 'propriedade' (ex: "não voa"), 'a' (ex: "o pinguim").
**Exemplo:** [{{"a": "o pinguim", "entidade_singular": "pássaro", "propriedade": "não voa"}}]
**IMPORTANTE:** Forneça APENAS o objeto JSON bruto, sem markdown.""",

    "FOL_CAUSAL": """Sua tarefa é gerar um array JSON contendo {num_instances} objetos. Cada objeto deve ter as chaves: {propositions}.
**Instrução de Causalidade de Propriedades para cada objeto:** 'entidades_plural' (ex: "pássaros"), 'a' (ex: "o pinguim"), 'propriedade_p' e 'propriedade_q' devem ter uma relação causal (ser 'p' implica ser 'q').
**Exemplo:** [{{"a": "o pinguim", "entidades_plural": "pássaros", "propriedade_p": "vive na Antártida", "propriedade_q": "é adaptado ao frio"}}]
**IMPORTANTE:** Forneça APENAS o array JSON bruto, sem markdown.""",

    "FOL/Hypothetical_Syllogism_FOL": """Sua tarefa é gerar um array JSON contendo {num_instances} objetos. Cada objeto deve ter as chaves: {propositions}.
**Instrução de Cadeia Causal de Propriedades:** 'entidades_plural' e 'entidade_singular' (ex: "mamíferos", "mamífero"), 'propriedade_p', 'propriedade_q', 'propriedade_r' devem formar uma cadeia lógica (p->q->r).
**Exemplo:** [{{"entidades_plural": "mamíferos", "entidade_singular": "mamífero", "propriedade_p": "é um carnívoro", "propriedade_q": "se alimenta de carne", "propriedade_r": "possui um sistema digestivo adaptado"}}]
**IMPORTANTE:** Forneça APENAS o objeto JSON bruto, sem markdown.""",
    
    # AJUSTE FINAL AQUI
    "FOL_ALTERNATIVES": """Sua tarefa é gerar um array JSON contendo {num_instances} objetos. Cada objeto deve ter as chaves: {propositions}.
**Instrução de Propriedades Alternativas e Excludentes:**
- 'entidade_singular': Uma categoria (ex: "animal", "veículo").
- 'a': Uma instância dessa categoria (ex: "o gato", "o carro").
- 'propriedade_p' e 'propriedade_q' devem ser duas propriedades que são **alternativas plausíveis ou estados excludentes**. Um objeto geralmente não possui ambas ao mesmo tempo.
**Exemplo de Alta Qualidade:** {{"a": "o gato", "entidade_singular": "animal", "propriedade_p": "está dormindo", "propriedade_q": "está acordado"}}
**Exemplo de Falha (A SER EVITADO):** {{"a": "o carro", "propriedade_p": "é rápido", "propriedade_q": "tem quatro rodas"}} (Um carro pode ser ambos.)
**IMPORTANTE:** Forneça APENAS o array JSON bruto, sem markdown.""",

    # AJUSTE FINAL AQUI
    "FOL_DILEMMAS": """Sua tarefa é gerar um array JSON contendo {num_instances} objetos. Cada objeto deve ter as chaves: {propositions}.
**Instrução de Alternativas Temáticas e Excludentes:**
- Cada objeto deve conter dois cenários de causa e efeito (p->q e r->s) sobre a instância 'a'.
- Os cenários devem ser **alternativas excludentes ou escolhas distintas**.
**Exemplo de Alta Qualidade:** {{"a": "Ana", "propriedade_p": "escolhe estudar para a prova", "propriedade_q": "tira uma boa nota", "propriedade_r": "escolhe ir à festa", "propriedade_s": "se diverte com os amigos"}} (Ana não pode fazer ambos ao mesmo tempo.)
**IMPORTANTE:** Forneça APENAS o objeto JSON bruto, sem markdown.""",

    # ============================ NM ============================
    "NM_GENERIC": """Sua tarefa é gerar um array JSON contendo {num_instances} objetos. Cada objeto deve ter as chaves: {propositions}.
**Instrução sobre Papéis:** 'Coisas' (ex: "pássaros"), 'Coisa' (ex: "pássaro"), 'propriedade' (ex: "voam"), 'x' (ex: "o pinguim Tweety").
**Exemplo:** [{{"Coisas": "pássaros", "Coisa": "pássaro", "propriedade": "voam", "x": "o pinguim Tweety"}}]
**IMPORTANTE:** Forneça APENAS o objeto JSON bruto, sem markdown.""",
    
    "NM/Default_Reasoning_Irrelevant_Info": """Sua tarefa é gerar um array JSON contendo {num_instances} objetos. Cada objeto deve ter as chaves: {propositions}.
**Instrução sobre Papéis:** 'Coisas' (ex: "pássaros"), 'Coisa' (ex: "pássaro"), 'propriedade' (ex: "voam"), 'x' (ex: "o canário Piu-Piu"), 'propriedade_irrelevante' (ex: "amarelo").
**Exemplo:** [{{"Coisas": "pássaros", "Coisa": "pássaro", "propriedade": "voam", "x": "o canário Piu-Piu", "propriedade_irrelevante": "amarelo"}}]
**IMPORTANTE:** Forneça APENAS o objeto JSON bruto, sem markdown.""",

    "NM/Default_Reasoning_Several_Defaults": """Sua tarefa é gerar um array JSON contendo {num_instances} objetos. Cada objeto deve ter as chaves: {propositions}.
**Instrução sobre Papéis:** 'Coisa1' e 'Coisa2' (ex: "Quakers", "Republicanos"), 'propriedade1' e 'propriedade2' (propriedades típicas, mas conflitantes, ex: "são pacifistas", "não são pacifistas"), 'x' (instância de ambos, ex: "Richard Nixon").
**Exemplo:** [{{"Coisa1": "Quaker", "Coisa2": "Republicano", "propriedade1": "é pacifista", "propriedade2": "não é pacifista", "x": "Richard Nixon"}}]
**IMPORTANTE:** Forneça APENAS o objeto JSON bruto, sem markdown.""",

    "NM/Reasoning_About_Priorities": """Sua tarefa é gerar um array JSON contendo {num_instances} objetos. Cada objeto deve ter as chaves: {propositions}.
**Instrução sobre Papéis:** 'fonte1' e 'fonte2' (ex: "o relatório do meteorologista", "o aplicativo de tempo"), 'p' (uma afirmação completa, ex: "vai chover amanhã").
**Exemplo:** [{{"fonte1": "o relatório do meteorologista", "fonte2": "o aplicativo de tempo", "p": "vai chover amanhã"}}]
**IMPORTANTE:** Forneça APENAS o objeto JSON bruto, sem markdown."""
}

# Mapeamento para aplicar prompts a grupos de regras
pl_dilemmas = ["PL/Constructive_Dilemma", "PL/Destructive_Dilemma", "PL/Bidirectional_Dilemma"]
for rule in pl_dilemmas: PROMPT_BANK[rule] = PROMPT_BANK["PL_DILEMMAS"]

fol_causal_rules = ["FOL/Modus_Ponens_FOL", "FOL/Modus_Tollens_FOL"]
for rule in fol_causal_rules: PROMPT_BANK[rule] = PROMPT_BANK["FOL_CAUSAL"]

fol_alternatives_rules = ["FOL/Disjunctive_Syllogism_FOL"]
for rule in fol_alternatives_rules: PROMPT_BANK[rule] = PROMPT_BANK["FOL_ALTERNATIVES"]

fol_dilemmas_rules = ["FOL/Constructive_Dilemma_FOL", "FOL/Destructive_Dilemma_FOL", "FOL/Bidirectional_Dilemma_FOL"]
for rule in fol_dilemmas_rules: PROMPT_BANK[rule] = PROMPT_BANK["FOL_DILEMMAS"]

nm_generic_rules = ["NM/Default_Reasoning_Disabled_Default", "NM/Default_Reasoning_Open_Domain", "NM/Reasoning_Unknown_Expectations_1", "NM/Reasoning_Unknown_Expectations_2", "NM/Reasoning_Unknown_Expectations_3"]
for rule in nm_generic_rules: PROMPT_BANK[rule] = PROMPT_BANK["NM_GENERIC"]
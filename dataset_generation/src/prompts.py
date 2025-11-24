"""
Este arquivo centraliza os prompts para a ETAPA 1, com foco na geração de
sentenças afirmativas e suas negações naturais.
"""

PROMPT_BANK = {
    # ============================ PL ============================
    "PL/Modus_Ponens": """Sua tarefa é gerar um array JSON contendo {num_instances} objetos.
Cada objeto deve ter as chaves: "p", "not p", "q", "not q".
'not p' deve ser a negação natural de 'p', e 'not q' a negação natural de 'q'.

Definição da Regra: Se p, então q. Sabe-se que p. Portanto, q.

--- EXEMPLO ---
{{
  "p": "Choveu forte durante a noite.",
  "not p": "Não choveu forte durante a noite.",
  "q": "As ruas estão molhadas.",
  "not q": "As ruas não estão molhadas."
}}

**Instruções Finais:**
1. Gere {num_instances} novos exemplos variados.
2. A relação "Se p, então q" deve ser causal e plausível.
3. Forneça APENAS o array JSON bruto, sem markdown.
""",

    "PL/Modus_Tollens": """Sua tarefa é gerar um array JSON contendo {num_instances} objetos.
Cada objeto deve ter as chaves: "p", "not p", "q", "not q".
'not p' deve ser a negação natural de 'p', e 'not q' a negação natural de 'q'.

Definição da Regra: Se p, então q. Sabe-se que não q. Portanto, não p.

--- EXEMPLO ---
{{
  "p": "O alarme tocou.",
  "not p": "O alarme não tocou.",
  "q": "Eu acordei na hora certa.",
  "not q": "Eu não acordei na hora certa."
}}

**Instruções Finais:**
1. Gere {num_instances} novos exemplos variados.
2. A relação "Se p, então q" deve ser causal e plausível.
3. Forneça APENAS o array JSON bruto, sem markdown.
""",

    "PL/Hypothetical_Syllogism": """Sua tarefa é gerar um array JSON contendo {num_instances} objetos.
Cada objeto deve ter as chaves: "p", "not p", "q", "r", "not r".
As sentenças 'not' devem ser a negação natural das suas contrapartes.

Definição da Regra: Se p, então q. Se q, então r. Portanto, se p, então r.

--- EXEMPLO ---
{{
  "p": "O despertador não tocou.",
  "not p": "O despertador tocou.",
  "q": "Eu acordei atrasado.",
  "r": "Eu perdi a reunião importante.",
  "not r": "Eu não perdi a reunião importante."
}}

**Instruções Finais:**
1. Gere {num_instances} novos exemplos com uma cadeia causal p -> q -> r.
2. Forneça APENAS o array JSON bruto, sem markdown.
""",

    "PL/Disjunctive_Syllogism": """Sua tarefa é gerar um array JSON contendo {num_instances} objetos.
Cada objeto deve ter as chaves: "p", "not p", "q", "not q".
'not p' e 'not q' devem ser as negações naturais de 'p' e 'q'.

Definição da Regra: p ou q. Sabe-se que não p. Portanto, q.

--- EXEMPLO ---
{{
  "p": "A chave está na gaveta da cozinha.",
  "not p": "A chave não está na gaveta da cozinha.",
  "q": "A chave está no porta-chaves ao lado da porta.",
  "not q": "A chave não está no porta-chaves ao lado da porta."
}}

**Instruções Finais:**
1. Gere {num_instances} novos exemplos onde 'p' e 'q' são alternativas plausíveis.
2. Forneça APENAS o array JSON bruto, sem markdown.
""",

    "PL/Constructive_Dilemma": """Sua tarefa é gerar um array JSON contendo {num_instances} objetos.
Cada objeto deve ter as chaves: "p", "q", "not q", "r", "s", "not s".
As sentenças 'not' devem ser as negações naturais de suas contrapartes.

Definição da Regra: Se p, então q. Se r, então s. Sabe-se que p ou r. Portanto, q ou s.

--- EXEMPLO ---
{{
  "p": "Eu escolho ir à praia",
  "q": "Eu vou nadar",
  "not q": "Eu não vou nadar",
  "r": "Eu escolho ir à montanha",
  "s": "Eu vou fazer uma trilha",
  "not s": "Eu não vou fazer uma trilha"
}}

**Instruções Finais:**
1. Gere {num_instances} novos exemplos onde (p, q) e (r, s) são alternativas temáticas.
2. Forneça APENAS o array JSON bruto, sem markdown.
""",

    "PL/Destructive_Dilemma": """Sua tarefa é gerar um array JSON contendo {num_instances} objetos.
Cada objeto deve ter as chaves: "p", "not p", "q", "not q", "r", "not r", "s", "not s".
As sentenças 'not' devem ser as negações naturais de suas contrapartes.

Definição da Regra: Se p, então q. Se r, então s. Sabe-se que não q ou não s. Portanto, não p ou não r.

--- EXEMPLO ---
{{
  "p": "Eu vou para o trabalho de carro",
  "not p": "Eu não vou para o trabalho de carro",
  "q": "Eu vou enfrentar o trânsito",
  "not q": "Eu não vou enfrentar o trânsito",
  "r": "Eu vou para o trabalho de transporte público",
  "not r": "Eu não vou para o trabalho de transporte público",
  "s": "Eu posso ler um livro durante o trajeto",
  "not s": "Eu não posso ler um livro durante o trajeto"
}}

**Instruções Finais:**
1. Gere {num_instances} novos exemplos onde (p, q) e (r, s) são alternativas temáticas.
2. Forneça APENAS o array JSON bruto, sem markdown.
""",

    "PL/Bidirectional_Dilemma": """Sua tarefa é gerar um array JSON contendo {num_instances} objetos.
Cada objeto deve ter as chaves: "p", "q", "not q", "r", "not r", "s", "not s".
As sentenças 'not' devem ser as negações naturais de suas contrapartes.

Definição da Regra: Se p, então q. Se r, então s. Sabe-se que p ou não s. Portanto, q ou não r.

--- EXEMPLO ---
{{
  "p": "Eu decido ir ao cinema esta noite",
  "q": "Eu assisto a um filme em tela grande",
  "not q": "Eu não assisto a um filme em tela grande",
  "r": "Eu decido ficar em casa esta noite",
  "not r": "Eu não decido ficar em casa esta noite",
  "s": "Eu assisto a uma série no streaming",
  "not s": "Eu não assisto a uma série no streaming"
}}

**Instruções Finais:**
1. Gere {num_instances} novos exemplos onde (p, q) e (r, s) são alternativas temáticas.
2. Forneça APENAS o array JSON bruto, sem markdown.
""",

    "PL/Commutation": """Sua tarefa é gerar um array JSON contendo {num_instances} objetos.
Cada objeto deve ter as chaves: "p", "q", "not q".
'not q' deve ser a negação natural de 'q'.

Definição da Regra: p ou q. Portanto, q ou p.

--- EXEMPLO ---
{{
  "p": "O prêmio será um carro novo",
  "q": "O prêmio será uma viagem internacional",
  "not q": "O prêmio não será uma viagem internacional"
}}

**Instruções Finais:**
1. Gere {num_instances} novos exemplos onde 'p' e 'q' são alternativas.
2. Forneça APENAS o array JSON bruto, sem markdown.
""",

    "PL/Material_Implication": """Sua tarefa é gerar um array JSON contendo {num_instances} objetos.
Cada objeto deve ter as chaves: "p", "not p", "q", "not q".
As sentenças 'not' devem ser as negações naturais de suas contrapartes.

Definição da Regra: Se p, então q. Portanto, não p ou q.

--- EXEMPLO ---
{{
  "p": "Uma forte geada atingiu as plantações.",
  "not p": "Uma forte geada não atingiu as plantações.",
  "q": "O preço do café no mercado aumentou.",
  "not q": "O preço do café no mercado não aumentou."
}}

**Instruções Finais:**
1. Gere {num_instances} novos exemplos com uma relação causal plausível.
2. Forneça APENAS o array JSON bruto, sem markdown.
"""
}


FALLBACK_PROMPT = """AVISO: NENHUM PROMPT ESPECIALIZADO ENCONTRADO.
Sua tarefa é gerar um array JSON contendo {num_instances} objetos.
Cada objeto deve ter as chaves: {propositions}.
Tente criar sentenças tematicamente conectadas e com relações lógicas plausíveis.
Forneça APENAS o array JSON bruto, sem markdown."""
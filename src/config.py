# src/config.py
"""
Este arquivo contém os templates lógicos para todas as 25 regras de inferência
e padrões de raciocínio do LogicBench, divididos por tipo de lógica:
PL (Lógica Proposicional), FOL (Lógica de Primeira Ordem) e NM (Lógica Não Monotônica).

A estrutura de cada regra define:
- template_context: A estrutura das premissas em linguagem natural, com placeholders.
- bqa_templates: Uma lista de perguntas para o modo de Resposta Binária (BQA),
  incluindo a pergunta correta (geralmente com resposta "Yes") e uma ou mais
  perguntas incorretas (com resposta "No").
"""

LOGIC_RULES_CONFIG = {
    # ==============================================================================
    # 9 Regras para Lógica Proposicional (PL)
    # ==============================================================================
    "PL": {
        "Modus_Ponens": {
            "template_context": "Se {p}, então {q}. Sabe-se que {p}.",
            "bqa_templates": [
                {"question": "Podemos concluir que '{q}'?", "answer": "Yes"},
                {"question": "Podemos concluir que '{not q}'?", "answer": "No"}
            ]
        },
        "Modus_Tollens": {
            "template_context": "Se {p}, então {q}. Sabe-se que {not q}.",
            "bqa_templates": [
                {"question": "Podemos concluir que '{not p}'?", "answer": "Yes"},
                {"question": "Podemos concluir que '{p}'?", "answer": "No"}
            ]
        },
        "Hypothetical_Syllogism": {
            "template_context": "Se {p}, então {q}. Se {q}, então {r}.",
            "bqa_templates": [
                {"question": "Podemos concluir que se {p}, então {r}?", "answer": "Yes"},
                {"question": "Podemos concluir que se {p}, então {not r}?", "answer": "No"}
            ]
        },
        "Disjunctive_Syllogism": {
            "template_context": "Sabe-se que {p} ou {q}. Também se sabe que {not p}.",
            "bqa_templates": [
                {"question": "Podemos concluir que '{q}'?", "answer": "Yes"},
                {"question": "Podemos concluir que '{not q}'?", "answer": "No"}
            ]
        },
        "Constructive_Dilemma": {
            "template_context": "Se {p}, então {q}. Se {r}, então {s}. Sabe-se que {p} ou {r}.",
            "bqa_templates": [
                {"question": "Podemos concluir que '{q} ou {s}'?", "answer": "Yes"},
                {"question": "Podemos concluir que '{not q} ou {not s}'?", "answer": "No"}
            ]
        },
        "Destructive_Dilemma": {
            "template_context": "Se {p}, então {q}. Se {r}, então {s}. Sabe-se que {not q} ou {not s}.",
            "bqa_templates": [
                {"question": "Podemos concluir que '{not p} ou {not r}'?", "answer": "Yes"},
                {"question": "Podemos concluir que '{p} ou {r}'?", "answer": "No"}
            ]
        },
        "Bidirectional_Dilemma": { # Nomeado 'BD' no artigo
            "template_context": "Se {p}, então {q}. Se {r}, então {s}. Sabe-se que {p} ou {not s}.",
            "bqa_templates": [
                {"question": "Podemos concluir que '{q} ou {not r}'?", "answer": "Yes"},
                {"question": "Podemos concluir que '{not q} ou {r}'?", "answer": "No"}
            ]
        },
        "Commutation": { # Nomeado 'CT' no artigo
            "template_context": "Sabe-se que {p} e {q}.",
            "bqa_templates": [
                {"question": "Podemos concluir que '{q} e {p}'?", "answer": "Yes"},
                {"question": "Podemos concluir que '{not q} e {p}'?", "answer": "No"}
            ]
        },
        "Material_Implication": { # Nomeado 'MI' no artigo
            "template_context": "Se {p}, então {q}.",
            "bqa_templates": [
                {"question": "Podemos concluir que '{not p} ou {q}'?", "answer": "Yes"},
                {"question": "Podemos concluir que '{p} ou {not q}'?", "answer": "No"}
            ]
        }
    },
    # ==============================================================================
    # 9 Regras para Lógica de Primeira Ordem (FOL)
    # ==============================================================================
    "FOL": {
        "Universal_Instantiation": { # UI
            "template_context": "Sabe-se que todos os {entidades_plural} são {propriedade}. {a} é um(a) {entidade_singular}.",
            "bqa_templates": [
                {"question": "Podemos concluir que '{a} é {propriedade}'?", "answer": "Yes"},
                {"question": "Podemos concluir que '{a} não é {propriedade}'?", "answer": "No"}
            ]
        },
        "Existential_Generalization": { # EG
             "template_context": "Sabe-se que '{a} é {propriedade}'.",
             "bqa_templates": [
                {"question": "Podemos concluir que existe pelo menos um(a) {entidade_singular} que é {propriedade}?", "answer": "Yes"},
                {"question": "Podemos concluir que nenhum(a) {entidade_singular} é {propriedade}?", "answer": "No"}
            ]
        },
        "Modus_Ponens_FOL": { # MP
            "template_context": "Todos os {entidades_plural} que são {propriedade_p} também são {propriedade_q}. {a} é {propriedade_p}.",
            "bqa_templates": [
                {"question": "Podemos concluir que '{a} é {propriedade_q}'?", "answer": "Yes"},
                {"question": "Podemos concluir que '{a} não é {propriedade_q}'?", "answer": "No"}
            ]
        },
        "Modus_Tollens_FOL": { # MT
            "template_context": "Todos os {entidades_plural} que são {propriedade_p} também são {propriedade_q}. {a} não é {propriedade_q}.",
            "bqa_templates": [
                {"question": "Podemos concluir que '{a} não é {propriedade_p}'?", "answer": "Yes"},
                {"question": "Podemos concluir que '{a} é {propriedade_p}'?", "answer": "No"}
            ]
        },
        "Hypothetical_Syllogism_FOL": { # HS
            "template_context": "Todos os {entidades_plural} que são {propriedade_p} também são {propriedade_q}. Todos os {entidades_plural} que são {propriedade_q} também são {propriedade_r}.",
            "bqa_templates": [
                {"question": "Podemos concluir que todos os {entidades_plural} que são {propriedade_p} também são {propriedade_r}?", "answer": "Yes"},
                {"question": "Podemos concluir que nenhum {entidade_singular} que é {propriedade_p} é {propriedade_r}?", "answer": "No"}
            ]
        },
        "Disjunctive_Syllogism_FOL": { # DS
            "template_context": "Todo {entidade_singular} é {propriedade_p} ou {propriedade_q}. {a} não é {propriedade_p}.",
            "bqa_templates": [
                {"question": "Podemos concluir que '{a} é {propriedade_q}'?", "answer": "Yes"},
                {"question": "Podemos concluir que '{a} não é {propriedade_q}'?", "answer": "No"}
            ]
        },
        "Constructive_Dilemma_FOL": { # CD
            "template_context": "Para todo indivíduo, se ele é {propriedade_p} então ele é {propriedade_q}, e se ele é {propriedade_r} então ele é {propriedade_s}. Sabe-se que {a} é {propriedade_p} ou {propriedade_r}.",
            "bqa_templates": [
                {"question": "Podemos concluir que '{a} é {propriedade_q} ou {propriedade_s}'?", "answer": "Yes"},
                {"question": "Podemos concluir que '{a} não é {propriedade_q} e não é {propriedade_s}'?", "answer": "No"}
            ]
        },
        "Destructive_Dilemma_FOL": { # DD
             "template_context": "Para todo indivíduo, se ele é {propriedade_p} então ele é {propriedade_q}, e se ele é {propriedade_r} então ele é {propriedade_s}. Sabe-se que {a} não é {propriedade_q} ou não é {propriedade_s}.",
             "bqa_templates": [
                {"question": "Podemos concluir que '{a} não é {propriedade_p} ou não é {propriedade_r}'?", "answer": "Yes"},
                {"question": "Podemos concluir que '{a} é {propriedade_p} ou é {propriedade_r}'?", "answer": "No"}
            ]
        },
        "Bidirectional_Dilemma_FOL": { # BD
             "template_context": "Para todo indivíduo, se ele é {propriedade_p} então ele é {propriedade_q}, e se ele é {propriedade_r} então ele é {propriedade_s}. Sabe-se que {a} é {propriedade_p} ou não é {propriedade_s}.",
             "bqa_templates": [
                {"question": "Podemos concluir que '{a} é {propriedade_q} ou não é {propriedade_r}'?", "answer": "Yes"},
                {"question": "Podemos concluir que '{a} não é {propriedade_q} ou é {propriedade_r}'?", "answer": "No"}
            ]
        }
    },
    # ==============================================================================
    # 8 Padrões para Lógica Não Monotônica (NM)
    # ==============================================================================
    "NM": {
        "Default_Reasoning_Irrelevant_Info": { # DRI
            "template_context": "{Coisas} normalmente {propriedade}. {x} é um(a) {Coisa}. {x} também tem uma {propriedade_irrelevante}.",
            "bqa_templates": [
                {"question": "Podemos concluir que '{x} é {propriedade}'?", "answer": "Yes"},
                {"question": "Podemos concluir que '{x} não é {propriedade}'?", "answer": "No"}
            ]
        },
        "Default_Reasoning_Several_Defaults": { # DRS
            "template_context": "{Coisa1} normalmente é {propriedade1}. {Coisa2} normalmente é {propriedade2}. {x} é um(a) {Coisa1} e {Coisa2}, mas não pode ser {propriedade1} e {propriedade2} ao mesmo tempo.",
            "bqa_templates": [
                {"question": "Podemos concluir que '{x} é {propriedade1} ou {propriedade2}'?", "answer": "Yes"},
                {"question": "Podemos concluir que '{x} não é nem {propriedade1} nem {propriedade2}'?", "answer": "No"}
            ]
        },
        "Default_Reasoning_Disabled_Default": { # DRD
            "template_context": "{Coisas} normalmente são {propriedade}. {x} é um(a) {Coisa}, mas sabe-se que {x} é uma exceção a esta regra.",
            "bqa_templates": [
                {"question": "Podemos concluir que '{x} não é {propriedade}'?", "answer": "Yes"},
                {"question": "Podemos concluir que '{x} é {propriedade}'?", "answer": "No"}
            ]
        },
        "Default_Reasoning_Open_Domain": { # DRO
             "template_context": "{Coisas} normalmente são {propriedade}. {x} é um(a) {Coisa} que não é {propriedade}.",
             "bqa_templates": [
                {"question": "Podemos concluir que a regra geral sobre {Coisas} continua válida para outros casos?", "answer": "Yes"},
                {"question": "Podemos concluir que a regra geral sobre {Coisas} foi invalidada?", "answer": "No"}
            ]
        },
        "Reasoning_Unknown_Expectations_1": { # RE1
            "template_context": "{Coisas} são geralmente {propriedade}. Sabe-se que ou {x} ou {y} não é {propriedade}, mas não se sabe qual. {z} é um(a) {Coisa}.",
            "bqa_templates": [
                {"question": "Podemos concluir que '{z} é {propriedade}'?", "answer": "Yes"},
                {"question": "Podemos concluir que '{z} não é {propriedade}'?", "answer": "No"}
            ]
        },
        "Reasoning_Unknown_Expectations_2": { # RE2
            "template_context": "{Coisas} são geralmente {propriedade}. Sabe-se que {x} é uma exceção e não é {propriedade}.",
            "bqa_templates": [
                {"question": "Podemos concluir que a regra geral sobre {Coisas} pode ser aplicada a outros membros da categoria?", "answer": "Yes"},
                {"question": "Podemos concluir que nenhuma {Coisa} é {propriedade}?", "answer": "No"}
            ]
        },
        "Reasoning_Unknown_Expectations_3": { # RE3
            "template_context": "Normalmente, {Coisas} são {propriedade1}. Também, normalmente, {Coisas} são {propriedade2}. Sabe-se que {x} não é {propriedade1}.",
            "bqa_templates": [
                {"question": "Podemos concluir que '{x} é {propriedade2}'?", "answer": "Yes"},
                {"question": "Podemos concluir que '{x} também não é {propriedade2}'?", "answer": "No"}
            ]
        },
        "Reasoning_About_Priorities": { # RAP
            "template_context": "A {fonte1} afirma que {p}. A {fonte2} afirma que {not p}. A {fonte1} é considerada mais confiável do que a {fonte2}.",
            "bqa_templates": [
                {"question": "Podemos concluir que '{p}'?", "answer": "Yes"},
                {"question": "Podemos concluir que '{not p}'?", "answer": "No"}
            ]
        }
    }
}
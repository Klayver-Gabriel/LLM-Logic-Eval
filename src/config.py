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
        "Modus_Tollens": {
            "template_context": "Se {p}, então {q}. Sabe-se que {not q}.",
            "bqa_templates": [
                {"question": ["Podemos concluir que '{not p}'?", "Isso implica que '{not p}'?", "Podemos inferir que '{not p}'?"], "answer": "Sim"},
                {"question": ["Podemos concluir que '{p}'?", "Isso implica que '{p}'?", "Podemos inferir que '{p}'?"], "answer": "Não"}
            ]
        },
        "Modus_Ponens": {
            "template_context": "Se {p}, então {q}. Sabe-se que {p}.",
            "bqa_templates": [
                {"question": ["Podemos concluir que '{q}'?", "Isso implica que '{q}'?", "Podemos inferir que '{q}'?"], "answer": "Sim"},
                {"question": ["Podemos concluir que '{not q}'?", "Isso implica que '{not q}'?", "Podemos inferir que '{not q}'?"], "answer": "Não"}
            ]
        },
        "Hypothetical_Syllogism": {
            "template_context": "Se {p}, então {q}. Se {q}, então {r}.",
            "bqa_templates": [
                {"question": ["Podemos concluir que se {p}, então {r}?", "Isso implica que se {p}, então {r}?", "Podemos inferir que se {p}, então {r}?"], "answer": "Sim"},
                {"question": ["Podemos concluir que se {p}, então {not r}?", "Isso implica que se {p}, então {not r}?"], "answer": "Não"}
            ]
        },
        "Disjunctive_Syllogism": {
            "template_context": "Sabe-se que {p} ou {q}. Também se sabe que {not p}.",
            "bqa_templates": [
                {"question": ["Podemos concluir que '{q}'?", "Isso implica que '{q}'?", "Podemos inferir que '{q}'?"], "answer": "Sim"},
                {"question": ["Podemos concluir que '{not q}'?", "Isso implica que '{not q}'?", "Podemos inferir que '{not q}'?"], "answer": "Não"}
            ]
        },
        "Constructive_Dilemma": {
            "template_context": "Se {p}, então {q}. Se {r}, então {s}. Sabe-se que {p} ou {r}.",
            "bqa_templates": [
                {"question": ["Podemos afirmar que '{q} ou {s}' é sempre verdadeiro?", "A lógica nos permite dizer que '{q} ou {s}'?", "É correto concluir que '{q} ou {s}'?"], "answer": "Sim"},
                {"question": ["Podemos afirmar que '{not q} ou {not s}' é sempre verdadeiro?", "A lógica nos permite dizer que '{not q} ou {not s}'?"], "answer": "Não"}
            ]
        },
        "Destructive_Dilemma": {
            "template_context": "Se {p}, então {q}. Se {r}, então {s}. Sabe-se que {not q} ou {not s}.",
            "bqa_templates": [
                {"question": ["Podemos afirmar que '{not p} ou {not r}' é sempre verdadeiro?", "A lógica nos permite dizer que '{not p} ou {not r}'?", "É correto concluir que '{not p} ou {not r}'?"], "answer": "Sim"},
                {"question": ["Podemos afirmar que '{p} ou {r}' é sempre verdadeiro?", "A lógica nos permite dizer que '{p} ou {r}'?"], "answer": "Não"}
            ]
        },
        "Bidirectional_Dilemma": {
            "template_context": "Se {p}, então {q}. Se {r}, então {s}. Sabe-se que {p} ou {not s}.",
            "bqa_templates": [
                {"question": ["Podemos afirmar que '{q} ou {not r}' é sempre verdadeiro?", "A lógica nos permite dizer que '{q} ou {not r}'?", "É correto concluir que '{q} ou {not r}'?"], "answer": "Sim"},
                {"question": ["Podemos afirmar que '{not q} ou {r}' é sempre verdadeiro?", "A lógica nos permite dizer que '{not q} ou {r}'?"], "answer": "Não"}
            ]
        },
        "Commutation": {
            "template_context": "Sabe-se que {p} e {q}.",
            "bqa_templates": [
                {"question": ["Podemos concluir que '{q} e {p}'?", "Isso implica que '{q} e {p}'?"], "answer": "Sim"},
                {"question": ["Podemos concluir que '{not q} e {p}'?", "Isso implica que '{not q} e {p}'?"], "answer": "Não"}
            ]
        },
        "Material_Implication": {
            "template_context": "Se {p}, então {q}.",
            "bqa_templates": [
                {"question": ["Podemos concluir que '{not p} ou {q}'?", "Isso implica que '{not p} ou {q}'?"], "answer": "Sim"},
                {"question": ["Podemos concluir que '{p} ou {not q}'?", "Isso implica que '{p} ou {not q}'?"], "answer": "Não"}
            ]
        }
    },
    # ==============================================================================
    # 9 Regras para Lógica de Primeira Ordem (FOL)
    # ==============================================================================
    "FOL": {
        "Universal_Instantiation": {
            "template_context": "Sabe-se que todos os {entidades_plural} são {propriedade}. {a} é um(a) {entidade_singular}.",
            "bqa_templates": [
                {"question": ["Podemos concluir que '{a} é {propriedade}'?", "Isso implica que '{a} é {propriedade}'?"], "answer": "Sim"},
                {"question": ["Podemos concluir que '{a} não é {propriedade}'?", "Isso implica que '{a} não é {propriedade}'?"], "answer": "Não"}
            ]
        },
        "Existential_Generalization": {
             "template_context": "Sabe-se que '{a} é {propriedade}'.",
             "bqa_templates": [
                {"question": ["Podemos concluir que existe pelo menos um(a) {entidade_singular} que é {propriedade}?", "Podemos inferir a existência de um(a) {entidade_singular} que é {propriedade}?"], "answer": "Sim"},
                {"question": ["Podemos concluir que nenhum(a) {entidade_singular} é {propriedade}?", "Isso implica que nenhum(a) {entidade_singular} é {propriedade}?"], "answer": "Não"}
            ]
        },
        "Modus_Ponens_FOL": {
            "template_context": "Todos os {entidades_plural} que são {propriedade_p} também são {propriedade_q}. {a} é {propriedade_p}.",
            "bqa_templates": [
                {"question": ["Podemos concluir que '{a} é {propriedade_q}'?", "Isso implica que '{a} é {propriedade_q}'?"], "answer": "Sim"},
                {"question": ["Podemos concluir que '{a} não é {propriedade_q}'?", "Isso implica que '{a} não é {propriedade_q}'?"], "answer": "Não"}
            ]
        },
        "Modus_Tollens_FOL": {
            "template_context": "Todos os {entidades_plural} que são {propriedade_p} também são {propriedade_q}. {a} não é {propriedade_q}.",
            "bqa_templates": [
                {"question": ["Podemos concluir que '{a} não é {propriedade_p}'?", "Isso implica que '{a} não é {propriedade_p}'?"], "answer": "Sim"},
                {"question": ["Podemos concluir que '{a} é {propriedade_p}'?", "Isso implica que '{a} é {propriedade_p}'?"], "answer": "Não"}
            ]
        },
        "Hypothetical_Syllogism_FOL": {
            "template_context": "Todos os {entidades_plural} que são {propriedade_p} também são {propriedade_q}. Todos os {entidades_plural} que são {propriedade_q} também são {propriedade_r}.",
            "bqa_templates": [
                {"question": ["Podemos concluir que todos os {entidades_plural} que são {propriedade_p} também são {propriedade_r}?", "Isso implica que todos os {entidades_plural} que são {propriedade_p} também são {propriedade_r}?"], "answer": "Sim"},
                {"question": ["Podemos concluir que nenhum {entidade_singular} que é {propriedade_p} é {propriedade_r}?", "Isso implica que alguns {entidades_plural} que são {propriedade_p} não são {propriedade_r}?"], "answer": "Não"}
            ]
        },
        "Disjunctive_Syllogism_FOL": {
            "template_context": "Todo {entidade_singular} é {propriedade_p} ou {propriedade_q}. {a} não é {propriedade_p}.",
            "bqa_templates": [
                {"question": ["Podemos concluir que '{a} é {propriedade_q}'?", "Isso implica que '{a} é {propriedade_q}'?"], "answer": "Sim"},
                {"question": ["Podemos concluir que '{a} não é {propriedade_q}'?", "Isso implica que '{a} não é {propriedade_q}'?"], "answer": "Não"}
            ]
        },
        "Constructive_Dilemma_FOL": {
            "template_context": "Para todo indivíduo, se ele é {propriedade_p} então ele é {propriedade_q}, e se ele é {propriedade_r} então ele é {propriedade_s}. Sabe-se que {a} é {propriedade_p} ou {propriedade_r}.",
            "bqa_templates": [
                {"question": ["É correto concluir que '{a} é {propriedade_q} ou {propriedade_s}'?", "Podemos afirmar que '{a} é {propriedade_q} ou {propriedade_s}'?"], "answer": "Sim"},
                {"question": ["É correto concluir que '{a} não é {propriedade_q} e não é {propriedade_s}'?", "Podemos afirmar que '{a} não é {propriedade_q} ou não é {propriedade_s}'?"], "answer": "Não"}
            ]
        },
        "Destructive_Dilemma_FOL": {
             "template_context": "Para todo indivíduo, se ele é {propriedade_p} então ele é {propriedade_q}, e se ele é {propriedade_r} então ele é {propriedade_s}. Sabe-se que {a} não é {propriedade_q} ou não é {propriedade_s}.",
             "bqa_templates": [
                {"question": ["É correto concluir que '{a} não é {propriedade_p} ou não é {propriedade_r}'?", "Podemos afirmar que '{a} não é {propriedade_p} ou não é {propriedade_r}'?"], "answer": "Sim"},
                {"question": ["É correto concluir que '{a} é {propriedade_p} ou é {propriedade_r}'?", "Podemos afirmar que '{a} é {propriedade_p} ou é {propriedade_r}'?"], "answer": "Não"}
            ]
        },
        "Bidirectional_Dilemma_FOL": {
             "template_context": "Para todo indivíduo, se ele é {propriedade_p} então ele é {propriedade_q}, e se ele é {propriedade_r} então ele é {propriedade_s}. Sabe-se que {a} é {propriedade_p} ou não é {propriedade_s}.",
             "bqa_templates": [
                {"question": ["É correto concluir que '{a} é {propriedade_q} ou não é {propriedade_r}'?", "Podemos afirmar que '{a} é {propriedade_q} ou não é {propriedade_r}'?"], "answer": "Sim"},
                {"question": ["É correto concluir que '{a} não é {propriedade_q} ou é {propriedade_r}'?", "Podemos afirmar que '{a} não é {propriedade_q} ou é {propriedade_r}'?"], "answer": "Não"}
            ]
        }
    },
    # ==============================================================================
    # 8 Padrões para Lógica Não Monotônica (NM)
    # ==============================================================================
    "NM": {
        "Default_Reasoning_Irrelevant_Info": {
            "template_context": "{Coisas} normalmente são {propriedade}. {x} é um(a) {Coisa}. {x} também tem uma {propriedade_irrelevante}.",
            "bqa_templates": [
                {"question": ["É razoável concluir que '{x} é {propriedade}'?", "Podemos assumir por padrão que '{x} é {propriedade}'?"], "answer": "Sim"},
                {"question": ["É razoável concluir que '{x} não é {propriedade}'?", "Podemos assumir por padrão que '{x} não é {propriedade}'?"], "answer": "Não"}
            ]
        },
        "Default_Reasoning_Several_Defaults": {
            "template_context": "{Coisa1} normalmente é {propriedade1}. {Coisa2} normalmente é {propriedade2}. {x} é um(a) {Coisa1} e {Coisa2}, mas não pode ser {propriedade1} e {propriedade2} ao mesmo tempo.",
            "bqa_templates": [
                {"question": ["É razoável concluir que '{x} é {propriedade1} ou {propriedade2}'?", "Podemos assumir que '{x} é {propriedade1} ou {propriedade2}'?"], "answer": "Sim"},
                {"question": ["É razoável concluir que '{x} não é nem {propriedade1} nem {propriedade2}'?", "Podemos assumir que '{x} não é nem {propriedade1} nem {propriedade2}'?"], "answer": "Não"}
            ]
        },
        # === CORREÇÃO LÓGICA APLICADA AQUI ===
        "Default_Reasoning_Disabled_Default": {
            "template_context": "{Coisas} normalmente são {propriedade}. {x} é um(a) {Coisa}, mas sabe-se que {x} é uma exceção a esta regra.",
            "bqa_templates": [
                {"question": ["Dado que {x} é uma exceção, é razoável assumir que '{x} é {propriedade}'?", "A regra padrão se aplica a {x}?"], "answer": "Não"},
                {"question": ["O fato de {x} ser uma exceção nos permite concluir com certeza que '{x} não é {propriedade}'?", "Podemos ter certeza que '{x} não é {propriedade}'?"], "answer": "Não"}
            ]
        },
        "Default_Reasoning_Open_Domain": {
             "template_context": "{Coisas} normalmente são {propriedade}. {x} é um(a) {Coisa} que não é {propriedade}.",
             "bqa_templates": [
                {"question": ["Podemos concluir que a regra geral sobre {Coisas} continua válida para outros casos?", "É razoável assumir que a regra geral sobre {Coisas} ainda se aplica?"], "answer": "Sim"},
                {"question": ["Podemos concluir que a regra geral sobre {Coisas} foi invalidada por este caso?", "Este caso único invalida a regra geral sobre {Coisas}?"], "answer": "Não"}
            ]
        },
        "Reasoning_Unknown_Expectations_1": {
            "template_context": "{Coisas} são geralmente {propriedade}. Sabe-se que ou {x} ou {y} não é {propriedade}, mas não se sabe qual. {z} é um(a) {Coisa}.",
            "bqa_templates": [
                {"question": ["É razoável concluir que '{z} é {propriedade}'?", "Podemos assumir que '{z} é {propriedade}'?"], "answer": "Sim"},
                {"question": ["É razoável concluir que '{z} não é {propriedade}'?", "Podemos assumir que '{z} não é {propriedade}'?"], "answer": "Não"}
            ]
        },
        "Reasoning_Unknown_Expectations_2": {
            "template_context": "{Coisas} são geralmente {propriedade}. Sabe-se que {x} é uma exceção e não é {propriedade}.",
            "bqa_templates": [
                {"question": ["Podemos concluir que a regra geral sobre {Coisas} pode ser aplicada a outros membros da categoria?", "A regra geral sobre {Coisas} ainda é útil para outros casos?"], "answer": "Sim"},
                {"question": ["Podemos concluir que nenhuma {Coisa} é {propriedade}?", "A exceção prova que nenhuma outra {Coisa} é {propriedade}?"], "answer": "Não"}
            ]
        },
        "Reasoning_Unknown_Expectations_3": {
            "template_context": "Normalmente, {Coisas} são {propriedade1}. Também, normalmente, {Coisas} são {propriedade2}. Sabe-se que {x} não é {propriedade1}.",
            "bqa_templates": [
                {"question": ["É razoável concluir que '{x} é {propriedade2}'?", "Podemos assumir que '{x} é {propriedade2}'?"], "answer": "Sim"},
                {"question": ["É razoável concluir que '{x} também não é {propriedade2}'?", "Podemos assumir que '{x} também não é {propriedade2}'?"], "answer": "Não"}
            ]
        },
        "Reasoning_About_Priorities": {
            "template_context": "A {fonte1} afirma que {p}. A {fonte2} afirma que {not p}. A {fonte1} é considerada mais confiável do que a {fonte2}.",
            "bqa_templates": [
                {"question": ["Com base na confiabilidade das fontes, podemos concluir que '{p}'?", "É mais provável que '{p}' seja verdade?"], "answer": "Sim"},
                {"question": ["Com base na confiabilidade das fontes, podemos concluir que '{not p}'?", "É mais provável que '{not p}' seja verdade?"], "answer": "Não"}
            ]
        }
    }
}
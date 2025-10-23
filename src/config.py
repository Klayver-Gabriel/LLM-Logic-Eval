# src/config.py (Versão Final, com templates de pergunta 100% alinhados ao LogicBench original)
"""
Este arquivo contém os templates lógicos para todas as 26 regras de inferência
e padrões de raciocínio do LogicBench, divididos por tipo de lógica:
PL (Lógica Proposicional), FOL (Lógica de Primeira Ordem) e NM (Lógica Não Monotônica).
"""
LOGIC_RULES_CONFIG = {
    # ==============================================================================
    # 9 Regras para Lógica Proposicional (PL)
    # ==============================================================================
    "PL": {
        "Modus_Tollens": {
            "template_context": "Se {p}, então {q}. Sabe-se que {not q}.",
            "bqa_templates": [
                {"question": ["Isso implica que '{not p}'?", "Podemos inferir que '{not p}'?"], "answer": "Sim"},
                {"question": ["Isso implica que '{p}'?", "Podemos inferir que '{p}'?"], "answer": "Não"}
            ],
            "mcqa_correct_conclusion": "{not p}"
        },
        "Modus_Ponens": {
            "template_context": "Se {p}, então {q}. Sabe-se que {p}.",
            "bqa_templates": [
                {"question": ["Isso implica que '{q}'?", "Podemos inferir que '{q}'?"], "answer": "Sim"},
                {"question": ["Isso implica que '{not q}'?", "Podemos inferir que '{not q}'?"], "answer": "Não"}
            ],
            "mcqa_correct_conclusion": "{q}"
        },
        "Hypothetical_Syllogism": {
            "template_context": "Se {p}, então {q}. Se {q}, então {r}.",
            "bqa_templates": [
                {"question": ["Se {p}, isso significa que {r}?"], "answer": "Sim"},
                {"question": ["Se {p}, isso significa que {not r}?"], "answer": "Não"},
                {"question": ["Se {not p}, isso significa que {not r}?"], "answer": "Não"},
                {"question": ["Se {not p}, isso significa que {r}?"], "answer": "Não"}
            ],
            "mcqa_correct_conclusion": "Se {p}, então {r}"
        },
        "Disjunctive_Syllogism": {
            "template_context": "Sabe-se que {p} ou {q}. Também se sabe que {not p}.",
            "bqa_templates": [
                {"question": ["Isso implica que '{q}'?"], "answer": "Sim"},
                {"question": ["Isso implica que '{not q}'?"], "answer": "Não"}
            ],
            "mcqa_correct_conclusion": "{q}"
        },
        "Constructive_Dilemma": {
            "template_context": "Se {p}, então {q}. Se {r}, então {s}. Sabe-se que {p} ou {r}.",
            "bqa_templates": [
                {"question": [{"prefix": "Podemos dizer que pelo menos um dos seguintes deve ser sempre verdadeiro? ", "clauses": ["(a) {q}", "(b) {s}"] }], "answer": "Sim"},
                {"question": [{"prefix": "Podemos dizer que pelo menos um dos seguintes deve ser sempre verdadeiro? ", "clauses": ["(a) {not q}", "(b) {not s}"] }], "answer": "Não"},
                {"question": [{"prefix": "Podemos dizer que pelo menos um dos seguintes deve ser sempre verdadeiro? ", "clauses": ["(a) {q}", "(b) {not s}"] }], "answer": "Não"},
                {"question": [{"prefix": "Podemos dizer que pelo menos um dos seguintes deve ser sempre verdadeiro? ", "clauses": ["(a) {not q}", "(b) {s}"] }], "answer": "Não"}
            ],
            "mcqa_correct_conclusion": "{q} ou {s}"
        },
        "Destructive_Dilemma": {
            "template_context": "Se {p}, então {q}. Se {r}, então {s}. Sabe-se que {not q} ou {not s}.",
            "bqa_templates": [
                {"question": [{"prefix": "Podemos dizer que pelo menos um dos seguintes deve ser sempre verdadeiro? ", "clauses": ["(a) {not p}", "(b) {not r}"] }], "answer": "Sim"},
                {"question": [{"prefix": "Podemos dizer que pelo menos um dos seguintes deve ser sempre verdadeiro? ", "clauses": ["(a) {p}", "(b) {r}"] }], "answer": "Não"},
                {"question": [{"prefix": "Podemos dizer que pelo menos um dos seguintes deve ser sempre verdadeiro? ", "clauses": ["(a) {not p}", "(b) {r}"] }], "answer": "Não"},
                {"question": [{"prefix": "Podemos dizer que pelo menos um dos seguintes deve ser sempre verdadeiro? ", "clauses": ["(a) {p}", "(b) {not r}"] }], "answer": "Não"}
            ],
            "mcqa_correct_conclusion": "{not p} ou {not r}"
        },
        "Bidirectional_Dilemma": {
            "template_context": "Se {p}, então {q}. Se {r}, então {s}. Sabe-se que {p} ou {not s}.",
            "bqa_templates": [
                {"question": [{"prefix": "Podemos dizer que pelo menos um dos seguintes deve ser sempre verdadeiro? ", "clauses": ["(a) {q}", "(b) {not r}"] }], "answer": "Sim"},
                {"question": [{"prefix": "Podemos dizer que pelo menos um dos seguintes deve ser sempre verdadeiro? ", "clauses": ["(a) {not q}", "(b) {r}"] }], "answer": "Não"},
                {"question": [{"prefix": "Podemos dizer que pelo menos um dos seguintes deve ser sempre verdadeiro? ", "clauses": ["(a) {q}", "(b) {r}"] }], "answer": "Não"},
                {"question": [{"prefix": "Podemos dizer que pelo menos um dos seguintes deve ser sempre verdadeiro? ", "clauses": ["(a) {not q}", "(b) {not r}"] }], "answer": "Não"}
            ],
            "mcqa_correct_conclusion": "{q} ou {not r}"
        },
        "Commutation": {
            "template_context": "Sabe-se que {p} e {q}.",
            "bqa_templates": [
                {"question": ["Isso implica que '{q} e {p}'?"], "answer": "Sim"},
                {"question": ["Isso implica que '{not q} e {p}'?"], "answer": "Não"}
            ],
            "mcqa_correct_conclusion": "{q} e {p}"
        },
        "Material_Implication": {
            "template_context": "Se {p}, então {q}.",
            "bqa_templates": [
                {"question": ["Isso implica que '{not p} ou {q}'?"], "answer": "Sim"},
                {"question": ["Isso implica que '{p} e {not q}'?"], "answer": "Não"}
            ],
            "mcqa_correct_conclusion": "{not p} ou {q}"
        }
    },
    # ==============================================================================
    # 9 Regras para Lógica de Primeira Ordem (FOL)
    # ==============================================================================
    "FOL": {
        "Universal_Instantiation": {
            "template_context": "Sabe-se que todos os {entidades_plural} são {propriedade}. {a} é um(a) {entidade_singular}.",
            "bqa_templates": [
                {"question": ["Isso implica que '{a} é {propriedade}'?"], "answer": "Sim"},
                {"question": ["Isso implica que '{a} não é {propriedade}'?"], "answer": "Não"}
            ],
            "mcqa_correct_conclusion": "{a} é {propriedade}"
        },
        "Existential_Generalization": {
             "template_context": "Sabe-se que '{a} é {propriedade}'.",
             "bqa_templates": [
                {"question": ["Isso implica que existe pelo menos um(a) {entidade_singular} que é {propriedade}?"], "answer": "Sim"},
                {"question": ["Isso implica que nenhum(a) {entidade_singular} é {propriedade}?"], "answer": "Não"}
            ],
             "mcqa_correct_conclusion": "Existe pelo menos um(a) {entidade_singular} que é {propriedade}"
        },
        "Modus_Ponens_FOL": {
            "template_context": "Todos os {entidades_plural} que são {propriedade_p} também são {propriedade_q}. {a} é {propriedade_p}.",
            "bqa_templates": [
                {"question": ["Isso implica que '{a} é {propriedade_q}'?"], "answer": "Sim"},
                {"question": ["Isso implica que '{a} não é {propriedade_q}'?"], "answer": "Não"}
            ],
            "mcqa_correct_conclusion": "{a} é {propriedade_q}"
        },
        "Modus_Tollens_FOL": {
            "template_context": "Todos os {entidades_plural} que são {propriedade_p} também são {propriedade_q}. {a} não é {propriedade_q}.",
            "bqa_templates": [
                {"question": ["Isso implica que '{a} não é {propriedade_p}'?"], "answer": "Sim"},
                {"question": ["Isso implica que '{a} é {propriedade_p}'?"], "answer": "Não"}
            ],
            "mcqa_correct_conclusion": "{a} não é {propriedade_p}"
        },
        "Hypothetical_Syllogism_FOL": {
            "template_context": "Todos os {entidades_plural} que são {propriedade_p} também são {propriedade_q}. Todos os {entidades_plural} que são {propriedade_q} também são {propriedade_r}.",
            "bqa_templates": [
                {"question": ["Se um(a) {entidade_singular} é {propriedade_p}, isso significa que também é {propriedade_r}?"], "answer": "Sim"},
                {"question": ["Se um(a) {entidade_singular} é {propriedade_p}, isso significa que não é {propriedade_r}?"], "answer": "Não"}
            ],
            "mcqa_correct_conclusion": "Todos os {entidades_plural} que são {propriedade_p} também são {propriedade_r}"
        },
        "Disjunctive_Syllogism_FOL": {
            "template_context": "Todo {entidade_singular} é {propriedade_p} ou {propriedade_q}. {a} não é {propriedade_p}.",
            "bqa_templates": [
                {"question": ["Isso implica que '{a} é {propriedade_q}'?"], "answer": "Sim"},
                {"question": ["Isso implica que '{a} não é {propriedade_q}'?"], "answer": "Não"}
            ],
            "mcqa_correct_conclusion": "{a} é {propriedade_q}"
        },
        "Constructive_Dilemma_FOL": {
            "template_context": "Para todo indivíduo, se ele é {propriedade_p} então ele é {propriedade_q}, e se ele é {propriedade_r} então ele é {propriedade_s}. Sabe-se que {a} é {propriedade_p} ou {propriedade_r}.",
            "bqa_templates": [
                {"question": [{"prefix": "Podemos dizer que pelo menos um dos seguintes deve ser sempre verdadeiro para {a}? ", "clauses": ["(a) é {propriedade_q}", "(b) é {propriedade_s}"] }], "answer": "Sim"},
                {"question": [{"prefix": "Podemos dizer que pelo menos um dos seguintes deve ser sempre verdadeiro para {a}? ", "clauses": ["(a) não é {propriedade_q}", "(b) não é {propriedade_s}"] }], "answer": "Não"},
                {"question": [{"prefix": "Podemos dizer que pelo menos um dos seguintes deve ser sempre verdadeiro para {a}? ", "clauses": ["(a) é {propriedade_q}", "(b) não é {propriedade_s}"] }], "answer": "Não"},
                {"question": [{"prefix": "Podemos dizer que pelo menos um dos seguintes deve ser sempre verdadeiro para {a}? ", "clauses": ["(a) não é {propriedade_q}", "(b) é {propriedade_s}"] }], "answer": "Não"}
            ],
            "mcqa_correct_conclusion": "{a} é {propriedade_q} ou {propriedade_s}"
        },
        "Destructive_Dilemma_FOL": {
             "template_context": "Para todo indivíduo, se ele é {propriedade_p} então ele é {propriedade_q}, e se ele é {propriedade_r} então ele é {propriedade_s}. Sabe-se que {a} não é {propriedade_q} ou não é {propriedade_s}.",
             "bqa_templates": [
                {"question": [{"prefix": "Podemos dizer que pelo menos um dos seguintes deve ser sempre verdadeiro para {a}? ", "clauses": ["(a) não é {propriedade_p}", "(b) não é {propriedade_r}"] }], "answer": "Sim"},
                {"question": [{"prefix": "Podemos dizer que pelo menos um dos seguintes deve ser sempre verdadeiro para {a}? ", "clauses": ["(a) é {propriedade_p}", "(b) é {propriedade_r}"] }], "answer": "Não"},
                {"question": [{"prefix": "Podemos dizer que pelo menos um dos seguintes deve ser sempre verdadeiro para {a}? ", "clauses": ["(a) não é {propriedade_p}", "(b) é {propriedade_r}"] }], "answer": "Não"},
                {"question": [{"prefix": "Podemos dizer que pelo menos um dos seguintes deve ser sempre verdadeiro para {a}? ", "clauses": ["(a) é {propriedade_p}", "(b) não é {propriedade_r}"] }], "answer": "Não"}
            ],
             "mcqa_correct_conclusion": "{a} não é {propriedade_p} ou não é {propriedade_r}"
        },
        "Bidirectional_Dilemma_FOL": {
             "template_context": "Para todo indivíduo, se ele é {propriedade_p} então ele é {propriedade_q}, e se ele é {propriedade_r} então ele é {propriedade_s}. Sabe-se que {a} é {propriedade_p} ou não é {propriedade_s}.",
             "bqa_templates": [
                {"question": [{"prefix": "Podemos dizer que pelo menos um dos seguintes deve ser sempre verdadeiro para {a}? ", "clauses": ["(a) é {propriedade_q}", "(b) não é {propriedade_r}"] }], "answer": "Sim"},
                {"question": [{"prefix": "Podemos dizer que pelo menos um dos seguintes deve ser sempre verdadeiro para {a}? ", "clauses": ["(a) não é {propriedade_q}", "(b) é {propriedade_r}"] }], "answer": "Não"},
                {"question": [{"prefix": "Podemos dizer que pelo menos um dos seguintes deve ser sempre verdadeiro para {a}? ", "clauses": ["(a) é {propriedade_q}", "(b) é {propriedade_r}"] }], "answer": "Não"},
                {"question": [{"prefix": "Podemos dizer que pelo menos um dos seguintes deve ser sempre verdadeiro para {a}? ", "clauses": ["(a) não é {propriedade_q}", "(b) não é {propriedade_r}"] }], "answer": "Não"}
            ],
             "mcqa_correct_conclusion": "{a} é {propriedade_q} ou não é {propriedade_r}"
        }
    },
    # ==============================================================================
    # 8 Padrões para Lógica Não Monotônica (NM)
    # ==============================================================================
    "NM": {
        "Default_Reasoning_Irrelevant_Info": {
            "template_context": "{Coisas} normalmente são {propriedade}. {x} é um(a) {Coisa}. {x} também tem uma {propriedade_irrelevante}.",
            "bqa_templates": [{"question": ["É razoável concluir que '{x} é {propriedade}'?"], "answer": "Sim"}, {"question": ["É razoável concluir que '{x} não é {propriedade}'?"], "answer": "Não"}],
            "mcqa_correct_conclusion": "{x} é {propriedade}"
        },
        "Default_Reasoning_Several_Defaults": {
            "template_context": "{Coisa1} normalmente é {propriedade1}. {Coisa2} normalmente é {propriedade2}. {x} é um(a) {Coisa1} e {Coisa2}, mas não pode ser {propriedade1} e {propriedade2} ao mesmo tempo.",
            "bqa_templates": [{"question": ["É razoável concluir que '{x} é {propriedade1} ou {propriedade2}'?"], "answer": "Sim"}, {"question": ["É razoável concluir que '{x} não é nem {propriedade1} nem {propriedade2}'?"], "answer": "Não"}],
            "mcqa_correct_conclusion": "{x} é {propriedade1} ou {propriedade2}"
        },
        "Default_Reasoning_Disabled_Default": {
            "template_context": "{Coisas} normalmente são {propriedade}. {x} é um(a) {Coisa}, mas sabe-se que {x} é uma exceção a esta regra.",
            "bqa_templates": [{"question": ["A regra padrão se aplica a {x}?"], "answer": "Não"}, {"question": ["Podemos ter certeza que '{x} não é {propriedade}'?"], "answer": "Não"}],
            "mcqa_correct_conclusion": "Não se pode assumir que {x} é {propriedade}"
        },
        "Default_Reasoning_Open_Domain": {
             "template_context": "{Coisas} normalmente são {propriedade}. {x} é um(a) {Coisa} que não é {propriedade}.",
             "bqa_templates": [{"question": ["A regra geral sobre {Coisas} continua válida para outros casos?"], "answer": "Sim"}, {"question": ["Este caso único invalida a regra geral sobre {Coisas}?"], "answer": "Não"}],
             "mcqa_correct_conclusion": "A regra geral sobre {Coisas} continua válida para outros casos"
        },
        "Reasoning_Unknown_Expectations_1": {
            "template_context": "{Coisas} são geralmente {propriedade}. Sabe-se que ou {x} ou {y} não é {propriedade}, mas não se sabe qual. {z} é um(a) {Coisa}.",
            "bqa_templates": [{"question": ["É razoável concluir que '{z} é {propriedade}'?"], "answer": "Sim"}, {"question": ["É razoável concluir que '{z} não é {propriedade}'?"], "answer": "Não"}],
            "mcqa_correct_conclusion": "{z} é {propriedade}"
        },
        "Reasoning_Unknown_Expectations_2": {
            "template_context": "{Coisas} são geralmente {propriedade}. Sabe-se que {x} é uma exceção e não é {propriedade}.",
            "bqa_templates": [{"question": ["A regra geral sobre {Coisas} ainda é útil para outros casos?"], "answer": "Sim"}, {"question": ["A exceção prova que nenhuma outra {Coisa} é {propriedade}?"], "answer": "Não"}],
            "mcqa_correct_conclusion": "A regra geral sobre {Coisas} pode ser aplicada a outros membros da categoria"
        },
        "Reasoning_Unknown_Expectations_3": {
            "template_context": "Normalmente, {Coisas} são {propriedade1}. Também, normalmente, {Coisas} são {propriedade2}. Sabe-se que {x} não é {propriedade1}.",
            "bqa_templates": [{"question": ["É razoável concluir que '{x} é {propriedade2}'?"], "answer": "Sim"}, {"question": ["É razoável concluir que '{x} também não é {propriedade2}'?"], "answer": "Não"}],
            "mcqa_correct_conclusion": "{x} é {propriedade2}"
        },
        "Reasoning_About_Priorities": {
            "template_context": "A {fonte1} afirma que {p}. A {fonte2} afirma que {not p}. A {fonte1} é considerada mais confiável do que a {fonte2}.",
            "bqa_templates": [{"question": ["Com base na confiabilidade das fontes, podemos concluir que '{p}'?"], "answer": "Sim"}, {"question": ["Com base na confiabilidade das fontes, podemos concluir que '{not p}'?"], "answer": "Não"}],
            "mcqa_correct_conclusion": "{p}"
        }
    }
}
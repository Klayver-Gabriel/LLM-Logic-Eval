"""
Este arquivo contém os templates lógicos para todas as 9 regras de inferência em 
PL (Lógica Proposicional).
"""
LOGIC_RULES_CONFIG = {
    # ==============================================================================
    # 9 Regras para Lógica Proposicional (PL)
    # ==============================================================================
    "PL": {
        # MT: ((p → q) ∧ ¬q) ⊢ ¬p
        "Modus_Tollens": {
            "template_context": "Se {p}, então {q}. Sabe-se que {not q}.",
            "bqa_templates": [
                {"question": ["Isso implica que '{not p}'?", "Podemos inferir que '{not p}'?"], "answer": "Sim"},
                {"question": ["Isso implica que '{p}'?", "Podemos inferir que '{p}'?"], "answer": "Não"}
            ],
            "mcqa_correct_conclusion": "{not p}"
        },
        # MP: ((p → q) ∧ p) ⊢ q
        "Modus_Ponens": {
            "template_context": "Se {p}, então {q}. Sabe-se que {p}.",
            "bqa_templates": [
                {"question": ["Isso implica que '{q}'?", "Podemos inferir que '{q}'?"], "answer": "Sim"},
                {"question": ["Isso implica que '{not q}'?", "Podemos inferir que '{not q}'?"], "answer": "Não"}
            ],
            "mcqa_correct_conclusion": "{q}"
        },
        # HS: ((p → q) ∧ (q → r)) ⊢ (p → r)
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
        # DS: ((p ∨ q) ∧ ¬p) ⊢ q
        "Disjunctive_Syllogism": {
            "template_context": "Sabe-se que {p} ou {q}. Também se sabe que {not p}.",
            "bqa_templates": [
                {"question": ["Isso implica que '{q}'?"], "answer": "Sim"},
                {"question": ["Isso implica que '{not q}'?"], "answer": "Não"}
            ],
            "mcqa_correct_conclusion": "{q}"
        },
        # CD: ((p → q) ∧ (r → s) ∧ (p ∨ r)) ⊢ (q ∨ s)
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
        # DD: ((p → q) ∧ (r → s) ∧ (¬q ∨ ¬s)) ⊢ (¬p ∨ ¬r)
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
        # BD: ((p → q) ∧ (r → s) ∧ (p ∨ ¬s)) ⊢ (q ∨ ¬r)
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
        # CT: (p ∨ q) ⊢ (q ∨ p)
        "Commutation": {
            "template_context": "Sabe-se que {p} ou {q}.",
            "bqa_templates": [
                {"question": ["Isso implica que '{q} ou {p}'?"], "answer": "Sim"},
                {"question": ["Isso implica que '{not q} ou {p}'?"], "answer": "Não"}
            ],
            "mcqa_correct_conclusion": "{q} ou {p}"
        },
        # MI: (p → q) ⊢ (¬p ∨ q)
        "Material_Implication": {
            "template_context": "Se {p}, então {q}.",
            "bqa_templates": [
                {"question": ["Isso implica que '{not p} ou {q}'?"], "answer": "Sim"},
                {"question": ["Isso implica que '{p} e {not q}'?"], "answer": "Não"}
            ],
            "mcqa_correct_conclusion": "{not p} ou {q}"
        }
    }
}
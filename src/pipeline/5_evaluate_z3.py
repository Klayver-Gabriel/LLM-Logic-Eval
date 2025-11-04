import json
import os
from z3 import *
from pathlib import Path

def load_jsonl(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return [json.loads(line) for line in f]

def create_z3_solver(context):
    solver = Solver()
    rule = context['rule'].split('/')[1] # Pegar a regra de inferencia
    s = context['sentence_bank']
    
    p = Bool('p')
    q = Bool('q')
    
    # Aplica a regra baseada na regra

    if rule == 'Modus_Tollens':
        solver.add(Implies(p, q))
        solver.add(Not(q))
        
    elif rule == 'Modus_Ponens':
        solver.add(Implies(p, q))  
        solver.add(p)              
        
    elif rule == 'Hypothetical_Syllogism':
        r = Bool('r')
        solver.add(Implies(p, q))  
        solver.add(Implies(q, r))   
        solver.add(Not(Implies(p, r)))  
        
    elif rule == 'Disjunctive_Syllogism':
        solver.add(Or(p, q))  
        solver.add(Not(p))    
        solver.add(Not(q))    
        
    return solver

def evaluate_context(context):
    solver = create_z3_solver(context)
    result = solver.check()
    model = None
    if result == sat:
        model = solver.model()
        model_str = {str(d): str(model[d]) for d in model.decls()}
    else:
        model_str = None
    
    evaluation = {
        'rule': context['rule'],
        'natural_context': context['natural_context'],
        'sentence_bank': context['sentence_bank'],
        'solver_result': str(result),
        'model': model_str
    }
    
    return evaluation

def main():
    base_dir = Path(__file__).parent.parent.parent
    input_file = base_dir / 'artifacts' / 'stage_2b_naturalized_contexts.jsonl'
    output_base = base_dir / 'output' / 'z3_evaluation'
    
    os.makedirs(output_base, exist_ok=True)
    
    contexts = load_jsonl(input_file)
    
    rule_contexts = {}
    for context in contexts:
        rule = context['rule']
        if rule not in rule_contexts:
            rule_contexts[rule] = []
        rule_contexts[rule].append(context)

    for rule, rule_contexts_list in rule_contexts.items():
        rule_name = rule.split('/')[1]
        rule_dir = output_base / rule_name
        os.makedirs(rule_dir, exist_ok=True)
        
        results = []
        for context in rule_contexts_list:
            result = evaluate_context(context)
            results.append(result)
        
        output_file = rule_dir / 'z3_results.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

if __name__ == '__main__':
    main()
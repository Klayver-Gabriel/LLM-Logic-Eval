import google.generativeai as genai
from Formula import *
def criar_formulas():
    formulas = []
    while True:
        print("\nCriação de nova fórmula:")
        tipo = input("Escolha o tipo de fórmula:\n1 - Atom\n2 - Not\n3 - And\n4 - Or\n5 - Implies\nOutro - Sair\n")
        if tipo == "1":
            atom = input("Nome da átomica: ")
            formulas.append(Atom(atom))
        elif tipo == "2":
            atom = input("Nome da átomica para negação: ")
            formulas.append(Not(Atom(atom)))
        elif tipo in ["3", "4", "5"]:
            atom1 = Atom(input("Nome da primeira átomica: "))
            atom2 = Atom(input("Nome da segunda átomica: "))
            if tipo == "3":
                formulas.append(And(atom1, atom2))
            elif tipo == "4":
                formulas.append(Or(atom1, atom2))
            elif tipo == "5":
                formulas.append(Implies(atom1, atom2))
        else:
            print("Processo finalizado.")
            break
        print(f"Fórmula criada: {formulas[-1]}")
    print("\nLista de fórmulas criadas:")
    for i, f in enumerate(formulas, 1):
        print(f"{i}: {f}")
    return formulas

genai.configure(api_key="AIzaSyBrZJhs4wdsD8HMu86pYDUzwO1VgKeE_jE")
model = genai.GenerativeModel("gemini-2.5-flash")

criar_formulas()
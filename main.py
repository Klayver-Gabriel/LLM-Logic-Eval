import google.generativeai as genai
from Formula import *
def cria_formula(formula1,formula2):
    if not isinstance(formula1, Formula):
        formula1 = Atom(str(formula1))
        formula2 = Atom(str(formula2))
    operador = input("Escolha: \n 1 - And \n 2 - Or \n 3 - Implies \n")
    if operador == "1":
        nova_formula = And(formula1,formula2)
    elif operador == "2":
        nova_formula = Or(formula1,formula2)
    elif operador == "3":
        nova_formula = Implies(formula1,formula2)
    return nova_formula
def cria_formula(variavel_logica):
    if not isinstance(variavel_logica, Atom):
        atom = Atom(str(variavel_logica))
    operador = input("Deseja criar a negação desta formula? \n 1 - Sim \n 2 - Não")
    if operador == "1":
        atom = Not(atom)
    return atom


genai.configure(api_key="AIzaSyBrZJhs4wdsD8HMu86pYDUzwO1VgKeE_jE")
model = genai.GenerativeModel("gemini-2.5-flash")


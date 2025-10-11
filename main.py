import google.generativeai as genai
from Formula import *
def cria_formula(formula1,formula2):
    if not isinstance(formula1, Formula):
        formula1 = Atom(str(formula1))
        formula2 = Atom(str(formula2))
    operador = input("Escolha: \n 1 - And \n 2 - Or \n 3 - Implies \n")
    if operador == "1":
        new_formula = And(formula1,formula2)
    elif operador == "2":
        new_formula = Or(formula1,formula2)
    elif operador == "3":
        new_formula = Implies(formula1,formula2)
    return new_formula

genai.configure(api_key="AIzaSyBrZJhs4wdsD8HMu86pYDUzwO1VgKeE_jE")
model = genai.GenerativeModel("gemini-2.5-flash")

premissa1 = cria_formula("José_é_Honesto","Maria_é_honesta")
premissa2 = cria_formula(premissa1,"Carlos_é_honesto")

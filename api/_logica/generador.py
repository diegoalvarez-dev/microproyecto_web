"""
Modulo: generador.py
Genera gramaticas aleatorias "de practica": el estudiante puede
generar un ejercicio, intentar resolverlo a mano (depurar y pasar a
FNC en papel), y despues comparar su resultado con el que produce el
propio depurador (opcion "Ejecutar proceso completo").

La gramatica generada incluye a proposito, con cierta probabilidad,
los distintos casos que se practican en el microproyecto:
    - una variable sin producciones propias (inutil)
    - un simbolo no declarado dentro de alguna produccion (inutil)
    - producciones nulas (epsilon)
    - producciones unitarias (A -> B)
    - producciones de longitud variable (para practicar Chomsky)
"""

import random

LETRAS_VARIABLES = list("ABCDE")   # variables disponibles (hasta 5)
LETRAS_FANTASMA = list("FGH")       # simbolos NO declarados, a proposito
TERMINALES_DISPONIBLES = ["1", "2", "3"]


def generar_gramatica_aleatoria():
    """
    Construye una gramatica aleatoria en el mismo formato JSON que
    espera gramatica_desde_json() (variables, terminales, inicial,
    producciones como listas de listas de simbolos).
    """
    num_variables = random.randint(4, 5)
    variables = LETRAS_VARIABLES[:num_variables]

    num_terminales = random.randint(2, 3)
    terminales = TERMINALES_DISPONIBLES[:num_terminales]

    inicial = variables[0]

    # Con probabilidad, una variable (distinta de la inicial) se deja
    # sin producciones propias, para practicar "variables inutiles".
    variable_sin_producciones = None
    if random.random() < 0.5 and len(variables) > 1:
        variable_sin_producciones = random.choice(variables[1:])

    # Con probabilidad, se usa un simbolo fantasma (no declarado) en
    # alguna produccion, para practicar la deteccion de simbolos no
    # declarados como "inutiles".
    usar_fantasma = random.random() < 0.55
    simbolo_fantasma = random.choice(LETRAS_FANTASMA)

    producciones = {}
    for variable in variables:
        if variable == variable_sin_producciones:
            producciones[variable] = []
            continue

        producciones[variable] = _generar_producciones_de_variable(
            variable, variables, terminales, usar_fantasma, simbolo_fantasma
        )

    return {
        "variables": variables,
        "terminales": terminales,
        "inicial": inicial,
        "producciones": producciones,
    }


def _generar_producciones_de_variable(variable, variables, terminales, usar_fantasma, simbolo_fantasma):
    alfabeto = variables + terminales
    otras_variables = [v for v in variables if v != variable]

    num_producciones = random.randint(2, 4)
    lista = []

    for _ in range(num_producciones):
        dado = random.random()

        if dado < 0.15:
            # Produccion nula
            produccion = []
        elif dado < 0.30 and otras_variables:
            # Produccion unitaria (una sola variable distinta de si misma)
            produccion = [random.choice(otras_variables)]
        else:
            # Produccion "normal" de longitud variable (para practicar
            # tanto depuracion como la conversion a Chomsky)
            longitud = random.randint(1, 3)
            produccion = [random.choice(alfabeto) for _ in range(longitud)]

            # Con cierta probabilidad, se inserta el simbolo fantasma
            # dentro de la produccion (simula un simbolo no declarado)
            if usar_fantasma and random.random() < 0.25:
                posicion = random.randint(0, len(produccion))
                produccion.insert(posicion, simbolo_fantasma)

        if produccion not in lista:
            lista.append(produccion)

    # IMPORTANTE: se garantiza que la variable tenga AL MENOS una
    # produccion compuesta solo de terminales. Sin esto, es posible
    # generar por azar una gramatica donde NINGUNA variable llegue
    # nunca a un terminal puro (todas dependen circularmente unas de
    # otras), y el algoritmo de "variables generadoras" las elimina
    # TODAS, dejando un ejercicio vacio e inutil para practicar. Los
    # casos de "inutil" que SI se quieren practicar (variable sin
    # producciones, simbolo fantasma) siguen intactos: no se tocan.
    longitud_base = random.choice([1, 1, 2])  # mayoria de longitud 1
    produccion_base = [random.choice(terminales) for _ in range(longitud_base)]
    if produccion_base not in lista:
        lista.append(produccion_base)

    return lista

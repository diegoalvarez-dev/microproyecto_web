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

Soporta tres niveles de dificultad (facil, medio, dificil) que
ajustan cuantas variables/terminales se usan y que tan frecuentes son
los casos "especiales" (nulas, unitarias, simbolos fantasma).

IMPORTANTE: se garantiza que el simbolo INICIAL nunca quede anulable
(que no pueda derivar la cadena vacia, ni directa ni indirectamente a
traves de otras variables anulables). Si el inicial fuera anulable, el
proceso de depuracion conserva legitimamente "inicial -> λ" hasta el
final, lo que haria que la Forma Normal de Chomsky resultante del
ejercicio terminara con una produccion nula - justo lo que se quiere
evitar en los ejercicios de practica (todos deben poder resolverse
limpio, sin nulas sobreviviendo hasta la FNC).
"""

import random

LETRAS_VARIABLES = list("ABCDE")   # variables disponibles (hasta 5)
LETRAS_FANTASMA = list("FGH")       # simbolos NO declarados, a proposito
TERMINALES_DISPONIBLES = ["1", "2", "3"]

# Configuracion de cada nivel de dificultad. "medio" conserva los
# mismos valores que tenia el generador original.
NIVELES_DIFICULTAD = {
    "facil": {
        "num_variables": (3, 3),
        "num_terminales": (2, 2),
        "prob_variable_sin_producciones": 0.25,
        "prob_fantasma": 0.25,
        "num_producciones": (2, 3),
        "prob_nula": 0.10,
        "prob_unitaria": 0.15,
        "longitud_normal": (1, 2),
        "prob_insertar_fantasma": 0.15,
    },
    "medio": {
        "num_variables": (4, 5),
        "num_terminales": (2, 3),
        "prob_variable_sin_producciones": 0.5,
        "prob_fantasma": 0.55,
        "num_producciones": (2, 4),
        "prob_nula": 0.15,
        "prob_unitaria": 0.15,
        "longitud_normal": (1, 3),
        "prob_insertar_fantasma": 0.25,
    },
    "dificil": {
        "num_variables": (5, 5),
        "num_terminales": (3, 3),
        "prob_variable_sin_producciones": 0.65,
        "prob_fantasma": 0.75,
        "num_producciones": (3, 5),
        "prob_nula": 0.20,
        "prob_unitaria": 0.20,
        "longitud_normal": (2, 4),
        "prob_insertar_fantasma": 0.35,
    },
}

# Cuantas veces se reintenta generar una gramatica completa cuando el
# simbolo inicial resulta anulable, antes de recurrir al fallback de
# seguridad.
MAX_INTENTOS_SIN_NULA_INICIAL = 40


def generar_gramatica_aleatoria(dificultad="medio"):
    """
    Construye una gramatica aleatoria en el mismo formato JSON que
    espera gramatica_desde_json() (variables, terminales, inicial,
    producciones como listas de listas de simbolos), garantizando
    que el simbolo inicial no sea anulable.

    dificultad: "facil", "medio" o "dificil". Cualquier otro valor
    (o None) cae de vuelta a "medio".
    """
    config = NIVELES_DIFICULTAD.get(dificultad, NIVELES_DIFICULTAD["medio"])

    for _ in range(MAX_INTENTOS_SIN_NULA_INICIAL):
        data = _generar_intento(config)
        anulables = _calcular_anulables(data["producciones"])
        if data["inicial"] not in anulables:
            return data

    # Fallback de seguridad (muy improbable que se llegue aqui con los
    # limites de intentos actuales): se toma el ultimo intento y se
    # eliminan, SOLO de las producciones propias del simbolo inicial,
    # aquellas que lo hacen anulable (vacias, o compuestas unicamente
    # por variables anulables). La produccion base de puros
    # terminales SIEMPRE se genera y nunca es anulable, asi que el
    # inicial queda garantizado con al menos una produccion valida.
    data = _generar_intento(config)
    anulables = _calcular_anulables(data["producciones"])
    inicial = data["inicial"]
    if inicial in anulables:
        data["producciones"][inicial] = [
            p for p in data["producciones"][inicial]
            if len(p) > 0 and not all(s in anulables for s in p)
        ]
    return data


def _generar_intento(config):
    """Genera UNA gramatica aleatoria completa (sin validar anulabilidad del inicial)."""
    num_variables = random.randint(*config["num_variables"])
    variables = LETRAS_VARIABLES[:num_variables]

    num_terminales = random.randint(*config["num_terminales"])
    terminales = TERMINALES_DISPONIBLES[:num_terminales]

    inicial = variables[0]

    # Con probabilidad, una variable (distinta de la inicial) se deja
    # sin producciones propias, para practicar "variables inutiles".
    variable_sin_producciones = None
    if random.random() < config["prob_variable_sin_producciones"] and len(variables) > 1:
        variable_sin_producciones = random.choice(variables[1:])

    # Con probabilidad, se usa un simbolo fantasma (no declarado) en
    # alguna produccion, para practicar la deteccion de simbolos no
    # declarados como "inutiles".
    usar_fantasma = random.random() < config["prob_fantasma"]
    simbolo_fantasma = random.choice(LETRAS_FANTASMA)

    producciones = {}
    for variable in variables:
        if variable == variable_sin_producciones:
            producciones[variable] = []
            continue

        producciones[variable] = _generar_producciones_de_variable(
            variable, variables, terminales, usar_fantasma, simbolo_fantasma, config
        )

    return {
        "variables": variables,
        "terminales": terminales,
        "inicial": inicial,
        "producciones": producciones,
    }


def _calcular_anulables(producciones):
    """
    Calcula el conjunto de variables anulables (las que pueden derivar
    la cadena vacia), con el algoritmo estandar de punto fijo: una
    variable es anulable si tiene una produccion vacia, o una
    produccion compuesta UNICAMENTE por variables que ya son
    anulables. Los terminales y simbolos fantasma nunca entran a este
    conjunto (no son llaves de "producciones"), asi que cualquier
    produccion que contenga alguno nunca aporta anulabilidad.
    """
    anulables = set()
    cambio = True
    while cambio:
        cambio = False
        for variable, lista in producciones.items():
            if variable in anulables:
                continue
            for produccion in lista:
                if len(produccion) == 0 or all(s in anulables for s in produccion):
                    anulables.add(variable)
                    cambio = True
                    break
    return anulables


def _generar_producciones_de_variable(variable, variables, terminales, usar_fantasma, simbolo_fantasma, config):
    alfabeto = variables + terminales
    otras_variables = [v for v in variables if v != variable]

    num_producciones = random.randint(*config["num_producciones"])
    lista = []

    prob_nula = config["prob_nula"]
    prob_unitaria_acumulada = prob_nula + config["prob_unitaria"]

    for _ in range(num_producciones):
        dado = random.random()

        if dado < prob_nula:
            # Produccion nula
            produccion = []
        elif dado < prob_unitaria_acumulada and otras_variables:
            # Produccion unitaria (una sola variable distinta de si misma)
            produccion = [random.choice(otras_variables)]
        else:
            # Produccion "normal" de longitud variable (para practicar
            # tanto depuracion como la conversion a Chomsky)
            longitud = random.randint(*config["longitud_normal"])
            produccion = [random.choice(alfabeto) for _ in range(longitud)]

            # Con cierta probabilidad, se inserta el simbolo fantasma
            # dentro de la produccion (simula un simbolo no declarado)
            if usar_fantasma and random.random() < config["prob_insertar_fantasma"]:
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
    # Ademas, esta produccion de puros terminales NUNCA es anulable,
    # lo que ayuda a que la verificacion de "inicial no anulable" se
    # cumpla rapido en la mayoria de los intentos.
    longitud_base = random.choice([1, 1, 2])  # mayoria de longitud 1
    produccion_base = [random.choice(terminales) for _ in range(longitud_base)]
    if produccion_base not in lista:
        lista.append(produccion_base)

    return lista
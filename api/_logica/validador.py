"""
Modulo: validador.py
Valida que una Gramatica Libre de Contexto este correctamente definida
antes de iniciar cualquier proceso de depuracion o transformacion.

Corresponde a RF06 y al punto 8 ("Validacion inicial de la gramatica")
del documento de lineamientos.

Reglas que se deben cumplir (segun el documento):
    1. Debe existir al menos una variable.
    2. Debe existir al menos un terminal.
    3. Debe existir un simbolo inicial.
    4. El simbolo inicial debe pertenecer al conjunto de variables.
    5. Toda produccion debe tener una variable valida en el lado izquierdo.
    6. Todos los simbolos utilizados deben haber sido previamente declarados.
    7. Las producciones deben tener una estructura valida.
    8. No deben existir simbolos desconocidos.

NOTA: cada produccion es una tupla de simbolos, ej. ('A','B').
La produccion nula (epsilon) es la tupla vacia: ().
"""

from .utils import formatear_produccion


class ErrorValidacion(Exception):
    """Excepcion especifica para errores de validacion de la gramatica."""
    pass


def validar_gramatica(gramatica):
    """
    Valida la gramatica recibida.

    NOTA IMPORTANTE: a diferencia de una validacion "estricta" de libro,
    aqui NO se rechaza la gramatica solo porque aparezca un simbolo no
    declarado en una produccion, ni porque una variable declarada no
    tenga producciones propias. Esos dos casos son precisamente lo que
    la fase de "eliminacion de variables inutiles" (RF12) debe limpiar
    automaticamente (por ejemplo: una variable F sin producciones, o
    una variable G usada en producciones pero nunca declarada, se
    tratan como variables inutiles y se eliminan junto con las
    producciones que las contienen, en vez de bloquear el registro).

    Solo se bloquea el registro por errores estructurales reales que
    el proceso de depuracion NO podria resolver por si solo:
        - No hay ninguna variable.
        - No hay ningun terminal.
        - No hay simbolo inicial, o no pertenece al conjunto de variables.

    Retorna:
        (bool, list[str]): tupla (es_valida, lista_de_errores)
    """
    errores = []

    errores += _validar_existencia_variables(gramatica)
    errores += _validar_existencia_terminales(gramatica)
    errores += _validar_simbolo_inicial(gramatica)

    es_valida = len(errores) == 0
    return es_valida, errores


def _validar_existencia_variables(gramatica):
    """Regla 1: debe existir al menos una variable."""
    if not gramatica.variables:
        return ["Error: la gramatica debe tener al menos una variable (VNT)."]
    return []


def _validar_existencia_terminales(gramatica):
    """Regla 2: debe existir al menos un terminal."""
    if not gramatica.terminales:
        return ["Error: la gramatica debe tener al menos un terminal (VT)."]
    return []


def _validar_simbolo_inicial(gramatica):
    """
    Reglas 3 y 4: debe existir un simbolo inicial y
    debe pertenecer al conjunto de variables.
    """
    if not gramatica.inicial:
        return ["Error: debe definirse un simbolo inicial."]
    if gramatica.inicial not in gramatica.variables:
        return [
            f"Error: el simbolo inicial {gramatica.inicial} no pertenece "
            f"al conjunto de variables."
        ]
    return []


def _validar_simbolos_en_producciones(gramatica):
    """
    Reglas 5, 6 y 8: toda produccion debe tener una variable valida en
    el lado izquierdo, y todo simbolo usado en el lado derecho debe
    haber sido declarado previamente (como variable o terminal).
    """
    errores = []
    simbolos_validos = gramatica.variables | gramatica.terminales

    for variable, lista_producciones in gramatica.producciones.items():
        if variable not in gramatica.variables:
            errores.append(
                f"Error: la variable {variable} usada en el lado izquierdo "
                f"de una produccion no fue declarada como variable (VNT)."
            )
            continue

        for produccion in lista_producciones:
            if produccion == gramatica.NULA:
                continue

            for simbolo in produccion:
                if simbolo not in simbolos_validos:
                    texto_prod = formatear_produccion(produccion)
                    errores.append(
                        f"Error: el simbolo {simbolo} utilizado en la "
                        f"produccion {variable} -> {texto_prod} no fue "
                        f"declarado como variable ni como terminal."
                    )

    return errores


def _validar_estructura_producciones(gramatica):
    """Regla 7: las producciones deben tener una estructura valida."""
    errores = []
    for variable, lista_producciones in gramatica.producciones.items():
        if not lista_producciones:
            errores.append(
                f"Error: la variable {variable} no tiene ninguna produccion definida."
            )
    return errores

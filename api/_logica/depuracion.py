"""
Modulo: depuracion.py
Implementa las 4 fases de depuracion de una Gramatica Libre de Contexto:

    1. Eliminacion de variables inutiles (no generadoras)
    2. Eliminacion de variables inalcanzables
    3. Eliminacion de producciones nulas
    4. Eliminacion de producciones unitarias

NOTA: cada produccion es una tupla de simbolos, ej. ('A','A','B').
La produccion nula (epsilon) es la tupla vacia: ().

IMPORTANTE - Orden de nulas vs unitarias:
    Normalmente se eliminan primero las nulas y luego las unitarias.
    Sin embargo, si existe un CICLO de unitarias entre variables que
    tambien son anulables (ej. A -> B, B -> A, ambas anulables), el
    proceso de eliminar nulas nunca converge. En ese caso se invierte
    el orden: primero unitarias, luego nulas. Ademas, invertir el
    orden puede generar NUEVAS unitarias (ej. autociclos A->A), por
    lo que se hace una limpieza final extra en ese caso.
"""

from itertools import combinations
from .utils import formatear_produccion


# ----------------------------------------------------------------------
# FASE 1: Variables inutiles (no generadoras)
# ----------------------------------------------------------------------

def obtener_variables_generadoras(gramatica):
    """
    Calcula el conjunto de variables generadoras: aquellas que,
    en algun numero finito de derivaciones, pueden producir una
    cadena compuesta unicamente por terminales.
    """
    generadoras = set()
    cambio = True

    while cambio:
        cambio = False
        for variable, lista_producciones in gramatica.producciones.items():
            if variable in generadoras:
                continue
            for produccion in lista_producciones:
                if produccion == gramatica.NULA:
                    generadoras.add(variable)
                    cambio = True
                    break
                if all(
                    (s in gramatica.terminales) or (s in generadoras)
                    for s in produccion
                ):
                    generadoras.add(variable)
                    cambio = True
                    break

    return generadoras


def _incorporar_simbolos_desconocidos(gramatica):
    """
    Busca simbolos usados en alguna produccion que NO esten declarados
    ni como variable ni como terminal (ej. una variable G que aparece
    en A -> GF2 pero nunca se declaro ni tiene su propia produccion).

    Estos simbolos se incorporan como variables SIN producciones
    propias, para que el algoritmo de variables generadoras los
    detecte automaticamente como no generadoras (inutiles) y sean
    eliminados junto con las producciones que los contienen.

    Retorna:
        set[str]: los simbolos desconocidos que se incorporaron (para
        reportarlos en el historial).
    """
    alfabeto_conocido = gramatica.variables | gramatica.terminales
    desconocidos = set()

    for lista_producciones in gramatica.producciones.values():
        for produccion in lista_producciones:
            for simbolo in produccion:
                if simbolo not in alfabeto_conocido:
                    desconocidos.add(simbolo)

    for simbolo in desconocidos:
        gramatica.variables.add(simbolo)
        gramatica.producciones.setdefault(simbolo, [])  # sin producciones propias

    return desconocidos


def eliminar_variables_inutiles(gramatica, historial=None):
    """
    Elimina las variables no generadoras (inutiles). Esto incluye:
        - Variables declaradas sin ninguna produccion propia (ej. F).
        - Simbolos usados en producciones pero nunca declarados
          (ej. G), que se incorporan primero como variables fantasma
          y luego se eliminan por no ser generadoras.

    Parametros:
        gramatica (Gramatica): gramatica a depurar (se modifica una copia).
        historial (Historial, opcional): si se provee, se registra el paso.

    Retorna:
        Gramatica: nueva gramatica sin variables inutiles.
    """
    gramatica_antes = gramatica.copia()
    nueva = gramatica.copia()

    simbolos_incorporados = _incorporar_simbolos_desconocidos(nueva)

    generadoras = obtener_variables_generadoras(nueva)
    inutiles = nueva.variables - generadoras

    for var in inutiles:
        nueva.eliminar_variable(var)

    if historial is not None:
        etiquetas = sorted(inutiles) if inutiles else ["Ninguna"]
        if simbolos_incorporados:
            etiquetas = [
                f"{s} (simbolo no declarado, tratado como inutil)"
                if s in simbolos_incorporados else s
                for s in etiquetas
            ]
        historial.registrar(
            fase="Eliminacion de variables inutiles (no generadoras)",
            gramatica_antes=gramatica_antes,
            elementos_identificados=etiquetas,
            producciones_eliminadas=None,
            producciones_agregadas=[],
            gramatica_despues=nueva.copia(),
        )

    return nueva


# ----------------------------------------------------------------------
# FASE 2: Variables inalcanzables
# ----------------------------------------------------------------------

def obtener_variables_alcanzables(gramatica):
    """Calcula el conjunto de variables alcanzables desde el simbolo inicial."""
    alcanzables = {gramatica.inicial}
    pendientes = [gramatica.inicial]

    while pendientes:
        var = pendientes.pop()
        for produccion in gramatica.producciones.get(var, []):
            for simbolo in produccion:
                if simbolo in gramatica.variables and simbolo not in alcanzables:
                    alcanzables.add(simbolo)
                    pendientes.append(simbolo)

    return alcanzables


def eliminar_variables_inalcanzables(gramatica, historial=None):
    """Elimina las variables que no son alcanzables desde el simbolo inicial."""
    gramatica_antes = gramatica.copia()
    nueva = gramatica.copia()

    alcanzables = obtener_variables_alcanzables(nueva)
    inalcanzables = nueva.variables - alcanzables

    for var in inalcanzables:
        nueva.eliminar_variable(var)

    if historial is not None:
        historial.registrar(
            fase="Eliminacion de variables inalcanzables",
            gramatica_antes=gramatica_antes,
            elementos_identificados=sorted(inalcanzables) if inalcanzables else ["Ninguna"],
            producciones_eliminadas=None,
            producciones_agregadas=[],
            gramatica_despues=nueva.copia(),
        )

    return nueva


# ----------------------------------------------------------------------
# FASE 3: Producciones nulas
# ----------------------------------------------------------------------

def obtener_variables_anulables(gramatica):
    """Calcula el conjunto de variables anulables (pueden derivar en epsilon)."""
    anulables = set()
    cambio = True

    while cambio:
        cambio = False
        for variable, lista_producciones in gramatica.producciones.items():
            if variable in anulables:
                continue
            for produccion in lista_producciones:
                if produccion == gramatica.NULA:
                    anulables.add(variable)
                    cambio = True
                    break
                if produccion and all(s in anulables for s in produccion):
                    anulables.add(variable)
                    cambio = True
                    break

    return anulables


def _generar_combinaciones_sin_anulables(produccion, posiciones_anulables):
    """
    Dada una produccion (tupla de simbolos) y las posiciones (indices)
    de simbolos anulables dentro de ella, genera todas las variantes
    posibles quitando subconjuntos de esas posiciones.

    Retorna:
        set[tuple]: conjunto de variantes (puede incluir la tupla
        vacia () si se quitan TODOS los simbolos).
    """
    variantes = set()
    n = len(posiciones_anulables)

    for r in range(n + 1):
        for combo in combinations(posiciones_anulables, r):
            quitar = set(combo)
            nueva = tuple(
                simbolo for i, simbolo in enumerate(produccion) if i not in quitar
            )
            variantes.add(nueva)

    return variantes


def eliminar_producciones_nulas(gramatica, historial=None):
    """
    Elimina las producciones nulas, generando las combinaciones
    necesarias de producciones donde se omite cada variable anulable.

    Caso especial: si el simbolo inicial es anulable, se conserva
    S -> nula (RNF07).
    """
    gramatica_antes = gramatica.copia()
    nueva = gramatica.copia()

    anulables = obtener_variables_anulables(nueva)
    inicial_es_anulable = nueva.inicial in anulables

    producciones_eliminadas = []
    producciones_agregadas = []

    nuevas_producciones = {}
    for variable, lista_producciones in nueva.producciones.items():
        nuevas_de_variable = []
        for produccion in lista_producciones:
            if produccion == nueva.NULA:
                producciones_eliminadas.append(f"{variable} -> λ")
                continue

            posiciones_anulables = [
                i for i, s in enumerate(produccion) if s in anulables
            ]

            if not posiciones_anulables:
                if produccion not in nuevas_de_variable:
                    nuevas_de_variable.append(produccion)
                continue

            variantes = _generar_combinaciones_sin_anulables(
                produccion, posiciones_anulables
            )

            for variante in variantes:
                if variante == ():
                    continue
                if variante not in nuevas_de_variable:
                    nuevas_de_variable.append(variante)
                    if variante != produccion:
                        producciones_agregadas.append(
                            f"{variable} -> {formatear_produccion(variante)}"
                        )

        nuevas_producciones[variable] = nuevas_de_variable

    nueva.producciones = nuevas_producciones

    if inicial_es_anulable:
        nueva.agregar_produccion(nueva.inicial, nueva.NULA)
        producciones_agregadas.append(f"{nueva.inicial} -> λ (caso especial)")

    if historial is not None:
        historial.registrar(
            fase="Eliminacion de producciones nulas",
            gramatica_antes=gramatica_antes,
            elementos_identificados=sorted(anulables) if anulables else ["Ninguna"],
            producciones_eliminadas=producciones_eliminadas,
            producciones_agregadas=producciones_agregadas,
            gramatica_despues=nueva.copia(),
        )

    return nueva


# ----------------------------------------------------------------------
# FASE 4: Producciones unitarias
# ----------------------------------------------------------------------

def obtener_pares_unitarios(gramatica):
    """Identifica todas las producciones unitarias (A -> B)."""
    pares = []
    for variable, lista_producciones in gramatica.producciones.items():
        for produccion in lista_producciones:
            if len(produccion) == 1 and produccion[0] in gramatica.variables:
                pares.append((variable, produccion[0]))
    return pares


def _cierre_unitario(gramatica, variable):
    """Cierre unitario: variables alcanzables solo via producciones unitarias."""
    cierre = {variable}
    pendientes = [variable]

    while pendientes:
        actual = pendientes.pop()
        for produccion in gramatica.producciones.get(actual, []):
            if len(produccion) == 1 and produccion[0] in gramatica.variables:
                destino = produccion[0]
                if destino not in cierre:
                    cierre.add(destino)
                    pendientes.append(destino)

    return cierre


def eliminar_producciones_unitarias(gramatica, historial=None):
    """Elimina las producciones unitarias usando el cierre unitario de cada variable."""
    gramatica_antes = gramatica.copia()
    nueva = gramatica.copia()

    pares_originales = obtener_pares_unitarios(nueva)
    producciones_eliminadas = [f"{a} -> {b}" for a, b in pares_originales]
    producciones_agregadas = []

    nuevas_producciones = {}
    for variable in nueva.variables:
        cierre = _cierre_unitario(nueva, variable)
        producciones_finales = []

        for var_en_cierre in cierre:
            for produccion in nueva.producciones.get(var_en_cierre, []):
                if len(produccion) == 1 and produccion[0] in nueva.variables:
                    continue  # se descarta, ya esta representada por el cierre
                if produccion == nueva.NULA and var_en_cierre != variable:
                    # El caso especial "nula" (epsilon del simbolo inicial)
                    # NO debe propagarse a otras variables a traves del
                    # cierre unitario; es exclusivo de quien la tenga
                    # como produccion propia.
                    continue
                if produccion not in producciones_finales:
                    producciones_finales.append(produccion)
                    if var_en_cierre != variable:
                        producciones_agregadas.append(
                            f"{variable} -> {formatear_produccion(produccion)}"
                        )

        nuevas_producciones[variable] = producciones_finales

    nueva.producciones = nuevas_producciones

    if historial is not None:
        historial.registrar(
            fase="Eliminacion de producciones unitarias",
            gramatica_antes=gramatica_antes,
            elementos_identificados=(
                [f"{a} -> {b}" for a, b in pares_originales] if pares_originales else ["Ninguna"]
            ),
            producciones_eliminadas=producciones_eliminadas,
            producciones_agregadas=producciones_agregadas,
            gramatica_despues=nueva.copia(),
        )

    return nueva


# ----------------------------------------------------------------------
# Orquestacion: deteccion de orden nulas/unitarias
# ----------------------------------------------------------------------

def existe_ciclo_unitarias_entre_anulables(gramatica):
    """Detecta ciclos de unitarias entre variables anulables (DFS con colores)."""
    anulables = obtener_variables_anulables(gramatica)
    pares = obtener_pares_unitarios(gramatica)

    grafo = {}
    for origen, destino in pares:
        if origen in anulables and destino in anulables:
            grafo.setdefault(origen, set()).add(destino)

    if not grafo:
        return False

    blanco, gris, negro = 0, 1, 2
    color = {v: blanco for v in grafo}
    for vecinos in grafo.values():
        for v in vecinos:
            color.setdefault(v, blanco)

    def dfs(nodo):
        color[nodo] = gris
        for vecino in grafo.get(nodo, []):
            if color[vecino] == gris:
                return True
            if color[vecino] == blanco and dfs(vecino):
                return True
        color[nodo] = negro
        return False

    for nodo in list(color.keys()):
        if color[nodo] == blanco:
            if dfs(nodo):
                return True

    return False


def depurar_gramatica(gramatica, historial=None):
    """
    Ejecuta el proceso completo de depuracion:
        1. Eliminar variables inutiles
        2. Eliminar variables inalcanzables
        3. Decidir orden nulas/unitarias segun si hay ciclo
        4. Eliminar nulas y unitarias en el orden decidido
           (con limpieza extra si se invirtio el orden)
    """
    actual = gramatica.copia()

    actual = eliminar_variables_inutiles(actual, historial)
    actual = eliminar_variables_inalcanzables(actual, historial)

    hay_ciclo = existe_ciclo_unitarias_entre_anulables(actual)

    if hay_ciclo:
        actual = eliminar_producciones_unitarias(actual, historial)
        actual = eliminar_producciones_nulas(actual, historial)
        if obtener_pares_unitarios(actual):
            actual = eliminar_producciones_unitarias(actual, historial)
    else:
        actual = eliminar_producciones_nulas(actual, historial)
        actual = eliminar_producciones_unitarias(actual, historial)

    return actual

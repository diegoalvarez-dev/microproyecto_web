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

    Se devuelve como LISTA (no set) para preservar un orden
    deterministico: primero r=0 (la produccion original, sin quitar
    nada), luego r=1,2,3... (quitando progresivamente mas simbolos
    anulables). Con un set, Python no garantiza ningun orden
    consistente, lo que desordenaba el resultado final.

    Retorna:
        list[tuple]: lista de variantes, sin duplicados (puede incluir
        la tupla vacia () si se quitan TODOS los simbolos).
    """
    variantes = []
    n = len(posiciones_anulables)

    for r in range(n + 1):
        for combo in combinations(posiciones_anulables, r):
            quitar = set(combo)
            nueva = tuple(
                simbolo for i, simbolo in enumerate(produccion) if i not in quitar
            )
            if nueva not in variantes:
                variantes.append(nueva)

    return variantes


def eliminar_producciones_nulas(gramatica, historial=None, _nivel_reintento=0):
    """
    Elimina las producciones nulas, UNA VARIABLE ANULABLE A LA VEZ.

    La produccion nula se elimina de TODAS las variables, SIN
    excepcion (incluida la variable inicial: no se conserva ningun
    "S -> lambda" como caso especial).

    DETECCION DE CICLOS QUE EMERGEN A MITAD DE PROCESO:
    Un ciclo de unitarias entre variables anulables (ej. A tiene la
    produccion B, B tiene la produccion A, ambas anulables) puede no
    existir al PRINCIPIO de este proceso, sino aparecer recien a
    mitad de camino (ej. "BB" se reduce a "B" al quitar una nula, y
    ESO crea la unitaria A->B que, combinada con B->A ya existente,
    forma el ciclo). Por eso no basta con revisar si hay ciclo una
    sola vez al inicio: hay que vigilarlo durante todo el proceso.

    La señal de que hay un ciclo es: una variable que YA fue
    procesada (se le quito su lambda propia) vuelve a necesitar
    procesarse OTRA VEZ (le resurgio una lambda nueva). Si eso pasa,
    se detiene el barrido de nulas en ese punto, se ejecuta UNA
    pasada de eliminacion de unitarias (que fusiona las producciones
    de A y B, rompiendo la dependencia mutua), y se vuelve a intentar
    eliminar nulas desde ese nuevo estado. Esto se repite hasta que
    ya no queden nulas o hasta un limite de seguridad.
    """
    LIMITE_REPROCESOS = 1
    LIMITE_REINTENTOS_GLOBALES = 8

    nueva = gramatica.copia()

    veces_procesada = {}
    pendientes = [v for v in nueva.producciones if nueva.NULA in nueva.producciones[v]]
    ciclo_detectado = False

    while pendientes:
        variable = pendientes.pop(0)
        if nueva.NULA not in nueva.producciones.get(variable, []):
            continue

        veces_procesada[variable] = veces_procesada.get(variable, 0) + 1

        gramatica_antes = nueva.copia()
        nueva.producciones[variable] = [p for p in nueva.producciones[variable] if p != nueva.NULA]

        producciones_eliminadas = [f"{variable} -> λ"]
        producciones_agregadas = []
        nuevos_pendientes = []

        nuevas_producciones = {}
        for var_afectada, lista in nueva.producciones.items():
            original = set(lista)
            nuevas_de_var = []

            for produccion in lista:
                if variable not in produccion:
                    if produccion not in nuevas_de_var:
                        nuevas_de_var.append(produccion)
                    continue

                posiciones = [i for i, s in enumerate(produccion) if s == variable]
                variantes = _generar_combinaciones_sin_anulables(produccion, posiciones)

                for variante in variantes:
                    if variante == nueva.NULA and var_afectada == variable:
                        continue
                    if variante not in nuevas_de_var:
                        nuevas_de_var.append(variante)

            for p in nuevas_de_var:
                if p in original:
                    continue
                if p == nueva.NULA:
                    producciones_agregadas.append(f"{var_afectada} -> λ")
                    if var_afectada not in pendientes and var_afectada not in nuevos_pendientes:
                        if veces_procesada.get(var_afectada, 0) >= LIMITE_REPROCESOS:
                            # Esta variable ya se proceso antes y esta
                            # a punto de necesitar OTRA vez: es un
                            # ciclo real (dependencia mutua tipo
                            # unitaria) que puede haber emergido recien
                            # a mitad de este proceso.
                            ciclo_detectado = True
                        else:
                            nuevos_pendientes.append(var_afectada)
                else:
                    producciones_agregadas.append(
                        f"{var_afectada} -> {formatear_produccion(p)}"
                    )

            nuevas_producciones[var_afectada] = nuevas_de_var

        nueva.producciones = nuevas_producciones
        pendientes = pendientes + nuevos_pendientes

        if historial is not None:
            historial.registrar(
                fase=f"Eliminación de producción nula: {variable} → λ",
                gramatica_antes=gramatica_antes,
                elementos_identificados=[variable],
                producciones_eliminadas=producciones_eliminadas,
                producciones_agregadas=producciones_agregadas,
                gramatica_despues=nueva.copia(),
            )

        if ciclo_detectado:
            break

    if ciclo_detectado and _nivel_reintento < LIMITE_REINTENTOS_GLOBALES:
        # Se rompe el ciclo fusionando las producciones unitarias
        # implicadas, y se reintenta eliminar las nulas restantes
        # desde este nuevo estado (recalculando todo desde cero).
        nueva = eliminar_producciones_unitarias(nueva, historial)
        return eliminar_producciones_nulas(
            nueva, historial,
            _nivel_reintento=_nivel_reintento + 1,
        )

    return nueva


# ----------------------------------------------------------------------
# FASE 4: Producciones unitarias
# ----------------------------------------------------------------------

def obtener_pares_unitarios(gramatica):
    """Identifica todas las producciones unitarias ACTUALES (A -> B)."""
    pares = []
    for variable, lista_producciones in gramatica.producciones.items():
        for produccion in lista_producciones:
            if len(produccion) == 1 and produccion[0] in gramatica.variables:
                pares.append((variable, produccion[0]))
    return pares


def eliminar_producciones_unitarias(gramatica, historial=None):
    """
    Elimina las producciones unitarias, UNA VARIABLE ORIGEN A LA VEZ
    (un paso de historial por variable que tenga alguna unitaria
    directa), sustituyendo cada "variable -> destino" por las
    producciones NO unitarias que "destino" tiene EN ESE MOMENTO (el
    estado actual de la gramatica cuando le toca el turno a
    "variable") — SIN seguir la cadena mas alla de ese nivel.

    Ejemplo: B -> D, D -> E. Al turno de B (que ocurre antes que el
    de D, siguiendo el orden de las variables), D todavia tiene su
    propia unitaria "D -> E" sin resolver, asi que a B solo se le
    copian las producciones NO unitarias que D YA tenia en ese
    momento (ej. D -> EA / 2), sin llegar hasta E. Cuando mas
    adelante le toque el turno a D, D si se resuelve usando las
    producciones de E — pero eso NO vuelve a tocar a B despues (no
    hay ningun paso de "actualizacion").

    Si varias unitarias parten de la MISMA variable origen (ej.
    A -> B y A -> C), se resuelven JUNTAS en un solo paso.
    """
    nueva = gramatica.copia()

    for variable in list(nueva.producciones.keys()):
        lista_actual = nueva.producciones.get(variable, [])
        unitarias_directas = [
            p for p in lista_actual if len(p) == 1 and p[0] in nueva.variables
        ]
        if not unitarias_directas:
            continue

        gramatica_antes = nueva.copia()
        destinos_directos = []
        for p in unitarias_directas:
            if p[0] not in destinos_directos:
                destinos_directos.append(p[0])

        nueva_lista = [p for p in lista_actual if p not in unitarias_directas]
        producciones_agregadas = []

        for destino in destinos_directos:
            for produccion in nueva.producciones.get(destino, []):
                if len(produccion) == 1 and produccion[0] in nueva.variables:
                    continue  # unitaria propia de "destino": se resuelve en SU turno
                if produccion == nueva.NULA and destino != variable:
                    continue  # una nula no se propaga entre variables distintas
                if produccion not in nueva_lista:
                    nueva_lista.append(produccion)
                    producciones_agregadas.append(
                        f"{variable} -> {formatear_produccion(produccion)}"
                    )

        nueva.producciones[variable] = nueva_lista

        if historial is not None:
            historial.registrar(
                fase=f"Eliminación de producción(es) unitaria(s) de {variable}",
                gramatica_antes=gramatica_antes,
                elementos_identificados=[f"{variable} -> {d}" for d in destinos_directos],
                producciones_eliminadas=[f"{variable} -> {d}" for d in destinos_directos],
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
        3. Eliminar producciones nulas (variable por variable; esta
           funcion se encarga internamente de detectar y romper
           cualquier ciclo con unitarias que surja, incluso si
           aparece a mitad de proceso).
        4. Limpieza final de producciones unitarias (por si queda
           alguna que no haya sido parte de un ciclo con nulas).
    """
    actual = gramatica.copia()

    actual = eliminar_variables_inutiles(actual, historial)
    actual = eliminar_variables_inalcanzables(actual, historial)
    actual = eliminar_producciones_nulas(actual, historial)
    actual = eliminar_producciones_unitarias(actual, historial)

    return actual
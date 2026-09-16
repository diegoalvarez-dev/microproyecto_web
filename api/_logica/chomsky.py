"""
Modulo: chomsky.py
Convierte una gramatica ya depurada a su equivalente en
Forma Normal de Chomsky (FNC).

Una GLC esta en FNC cuando toda produccion tiene una de estas formas:
    A -> BC   (dos variables)
    A -> a    (un terminal)

NOTA: cada produccion es una tupla de simbolos, ej. ('A','A','B').

Pasos:
    1. Sustitucion de terminales: si una produccion tiene longitud > 1
       y contiene un terminal, ese terminal se reemplaza por una
       variable auxiliar nueva (Xn -> terminal). Se REUTILIZA la
       misma variable auxiliar cada vez que aparece el mismo terminal.
    2. Reduccion de producciones largas: si una produccion tiene mas
       de 2 simbolos, se introducen variables auxiliares nuevas
       (X1, X2, X3...) para dejarla en forma binaria. Por decision
       del equipo (pendiente de confirmar con la ingeniera), NO se
       reutilizan variables auxiliares en este paso aunque dos
       producciones generen el mismo par de simbolos.
"""

from .utils import formatear_produccion


class GeneradorVariables:
    """Genera nombres de variables auxiliares nuevos (X1, X2, X3, ...)."""

    def __init__(self, variables_existentes):
        self.usadas = set(variables_existentes)
        self.contador = 1

    def nueva_variable(self):
        """Devuelve un nuevo nombre de variable auxiliar (ej. 'X1')."""
        nombre = f"X{self.contador}"
        while nombre in self.usadas:
            self.contador += 1
            nombre = f"X{self.contador}"
        self.usadas.add(nombre)
        self.contador += 1
        return nombre


def sustituir_terminales(gramatica, historial=None):
    """
    Fase 1 de FNC: reemplaza cada terminal, en producciones de
    longitud > 1, por una variable auxiliar que produce unicamente
    ese terminal (Xn -> terminal). Se reutiliza la misma variable
    para el mismo terminal en todas las producciones.
    """
    gramatica_antes = gramatica.copia()
    nueva = gramatica.copia()
    generador = GeneradorVariables(nueva.variables)

    mapa_terminal_variable = {}
    producciones_eliminadas = []
    producciones_agregadas = []

    nuevas_producciones = {}
    for variable, lista_producciones in nueva.producciones.items():
        nueva_lista = []
        for produccion in lista_producciones:
            if produccion == nueva.NULA or len(produccion) <= 1:
                nueva_lista.append(produccion)
                continue

            hubo_cambio = False
            nuevos_simbolos = []
            for simbolo in produccion:
                if simbolo in nueva.terminales:
                    if simbolo not in mapa_terminal_variable:
                        var_nueva = generador.nueva_variable()
                        mapa_terminal_variable[simbolo] = var_nueva
                    nuevos_simbolos.append(mapa_terminal_variable[simbolo])
                    hubo_cambio = True
                else:
                    nuevos_simbolos.append(simbolo)

            produccion_nueva = tuple(nuevos_simbolos)
            if hubo_cambio:
                producciones_eliminadas.append(
                    f"{variable} -> {formatear_produccion(produccion)}"
                )
                producciones_agregadas.append(
                    f"{variable} -> {formatear_produccion(produccion_nueva)}"
                )
            nueva_lista.append(produccion_nueva)

        nuevas_producciones[variable] = nueva_lista

    nueva.producciones = nuevas_producciones

    for terminal, var_nueva in mapa_terminal_variable.items():
        nueva.variables.add(var_nueva)
        nueva.producciones[var_nueva] = [(terminal,)]
        producciones_agregadas.append(f"{var_nueva} -> {terminal}")

    if historial is not None:
        historial.registrar(
            fase="Sustitucion de terminales en producciones largas",
            gramatica_antes=gramatica_antes,
            elementos_identificados=(
                [f"{t} => {v}" for t, v in mapa_terminal_variable.items()]
                if mapa_terminal_variable else ["Ninguna"]
            ),
            producciones_eliminadas=producciones_eliminadas,
            producciones_agregadas=producciones_agregadas,
            gramatica_despues=nueva.copia(),
        )

    return nueva


def binarizar_producciones(gramatica, historial=None):
    """
    Fase 2 de FNC: descompone producciones de mas de 2 simbolos en
    producciones binarias.

    METODO (igual al proceso manual): se toma el PRIMER simbolo y se
    empareja con una variable auxiliar nueva que representa "todo el
    resto". Esa variable nueva se numera INMEDIATAMENTE (X2, X3...,
    en orden creciente segun se van necesitando), y luego, si ese
    "resto" todavia tiene mas de 2 simbolos, se vuelve a aplicar el
    mismo proceso sobre el resto (peelando el siguiente simbolo),
    creando la siguiente variable auxiliar.

    Ejemplo (igual al tuyo): C -> DCDC2
        resto tras la D = CDC2 (4 simbolos) -> se crea X2 = CDC2
        C -> D X2
        resto tras la C (dentro de X2) = DC2 (3 simbolos) -> se crea X3 = DC2
        X2 -> C X3
        resto tras la D (dentro de X3) = C2 (2 simbolos, ya binario)
        X3 -> D X4
        X4 -> C 2
    """
    gramatica_antes = gramatica.copia()
    nueva = gramatica.copia()
    generador = GeneradorVariables(nueva.variables)

    producciones_eliminadas = []
    producciones_agregadas = []
    definiciones_nuevas = {}  # variable_auxiliar -> tupla binaria que la define
    detalle_producciones = []  # desglose por produccion, para la vista estilo cuaderno

    def construir_cadena(simbolos, registro_local):
        """
        Reduce una lista de simbolos (longitud >= 2) a una produccion
        binaria valida, creando variables auxiliares nuevas en el
        MISMO orden en que se van necesitando (peelando desde el
        primer simbolo hacia la derecha, recursivamente).
        `registro_local` acumula (nombre, definicion) de las variables
        nuevas creadas SOLO para esta produccion en particular, en
        orden de creacion (para mostrarlas con "chulo" en la interfaz).
        """
        if len(simbolos) == 2:
            return tuple(simbolos)

        primer_simbolo = simbolos[0]
        resto = simbolos[1:]

        nueva_var = generador.nueva_variable()
        definicion_resto = construir_cadena(resto, registro_local)
        definiciones_nuevas[nueva_var] = definicion_resto
        registro_local.append((nueva_var, definicion_resto))
        producciones_agregadas.append(
            f"{nueva_var} -> {formatear_produccion(definicion_resto)}"
        )

        return (primer_simbolo, nueva_var)

    nuevas_producciones = {}
    for variable, lista_producciones in nueva.producciones.items():
        nueva_lista = []
        for produccion in lista_producciones:
            if produccion == nueva.NULA or len(produccion) <= 2:
                # Ya cumple FNC tal cual (Vt, Vnt, o cualquier pareja
                # VtVnt/VntVnt/VtVt/VntVt): se "encierra en circulo",
                # va directo a las producciones de la variable.
                nueva_lista.append(produccion)
                detalle_producciones.append({
                    "variable": variable,
                    "original": formatear_produccion(produccion),
                    "yaEraValida": True,
                    "resultado": formatear_produccion(produccion),
                    "variablesNuevas": [],
                })
                continue

            registro_local = []
            resultado = construir_cadena(list(produccion), registro_local)

            # Reordenar por numero (X1, X2, X3...) para que la vista
            # las muestre de arriba hacia abajo en orden creciente,
            # tal como en el cuaderno (la recursion las completa en
            # orden inverso, pero se numeran en orden ascendente).
            registro_local.sort(key=lambda item: int(item[0][1:]))

            producciones_eliminadas.append(
                f"{variable} -> {formatear_produccion(produccion)}"
            )
            producciones_agregadas.append(
                f"{variable} -> {formatear_produccion(resultado)}"
            )
            nueva_lista.append(resultado)

            detalle_producciones.append({
                "variable": variable,
                "original": formatear_produccion(produccion),
                "yaEraValida": False,
                "resultado": formatear_produccion(resultado),
                "variablesNuevas": [
                    {"nombre": n, "valor": formatear_produccion(v)}
                    for n, v in registro_local
                ],
            })

        nuevas_producciones[variable] = nueva_lista


    nueva.producciones = nuevas_producciones

    for var_nueva, definicion in definiciones_nuevas.items():
        nueva.variables.add(var_nueva)
        nueva.producciones[var_nueva] = [definicion]

    if historial is not None:
        historial.registrar(
            fase="Reduccion de producciones largas (binarizacion)",
            gramatica_antes=gramatica_antes,
            elementos_identificados=(
                [f"{v} -> {formatear_produccion(p)}" for v, p in definiciones_nuevas.items()]
                if definiciones_nuevas else ["Ninguna"]
            ),
            producciones_eliminadas=producciones_eliminadas,
            producciones_agregadas=producciones_agregadas,
            gramatica_despues=nueva.copia(),
            detalle=detalle_producciones,
        )

    return nueva


def convertir_a_fnc(gramatica, historial=None):
    """
    Ejecuta el proceso de conversion a FNC.

    NOTA IMPORTANTE (segun la forma de trabajo de la clase, confirmar
    con la ingeniera si hace falta): NO se hace un paso separado de
    "sustitucion de terminales". Las combinaciones VtVnt, VntVt y
    VtVt se consideran validas directamente en una produccion binaria
    (ej. B1 = variable B + terminal 1 ya esta bien asi, sin crear una
    variable auxiliar aparte solo para el terminal). Por eso el unico
    paso necesario es la binarizacion.
    """
    actual = gramatica.copia()
    actual = binarizar_producciones(actual, historial)
    return actual


def validar_fnc(gramatica):
    """
    Verifica que la gramatica cumpla con la FNC tal como la maneja
    la clase: toda produccion debe tener como maximo 2 simbolos,
    en cualquier combinacion (VtVnt, VntVnt, VtVt, VntVt, Vt, Vnt).
    RNF12.

    Se permite como unica excepcion S -> nula (S = simbolo inicial).

    Retorna:
        (bool, list[str]): (es_fnc_valida, lista_de_producciones_invalidas)
    """
    invalidas = []
    alfabeto_valido = gramatica.variables | gramatica.terminales

    for variable, lista_producciones in gramatica.producciones.items():
        for produccion in lista_producciones:
            texto = formatear_produccion(produccion)

            if produccion == gramatica.NULA:
                if variable == gramatica.inicial:
                    continue
                invalidas.append(f"{variable} -> {texto} (nula no permitida aqui)")
                continue

            if len(produccion) > 2:
                invalidas.append(f"{variable} -> {texto} (longitud > 2)")
                continue

            for simbolo in produccion:
                if simbolo not in alfabeto_valido:
                    invalidas.append(
                        f"{variable} -> {texto} (simbolo '{simbolo}' no declarado)"
                    )
                    break

    return len(invalidas) == 0, invalidas

"""
Modulo: utils.py
Funciones auxiliares de apoyo: formateo de gramaticas y producciones
para impresion, parseo de entrada de usuario (texto -> tuplas de
simbolos), etc.

IMPORTANTE sobre representacion:
    Cada produccion se representa internamente como una TUPLA de
    simbolos, ej. ('A','A','B'). La produccion nula (epsilon) es la
    tupla vacia: ().
    Esto evita el problema de leer caracter por caracter una vez
    aparecen variables auxiliares de mas de un caracter (X1, X2...).
"""


def tokenizar_produccion(texto, alfabeto):
    """
    Convierte el string de una produccion en una lista de SIMBOLOS
    (tokens), reconociendo nombres de variables de mas de un caracter
    (como las auxiliares de Chomsky: X1, X2, X10...).

    Estrategia: en cada posicion se busca la coincidencia de MAYOR
    longitud dentro del alfabeto conocido. Si ningun simbolo conocido
    coincide, se toma 1 solo caracter (permite detectar simbolos no
    declarados durante la validacion).

    Parametros:
        texto (str): la produccion en texto plano (ej. "AX1").
        alfabeto (set[str]): simbolos validos conocidos (variables + terminales).

    Retorna:
        list[str]: lista de simbolos, ej. ["A", "X1"].
    """
    if texto == "":
        return []

    simbolos = []
    i = 0
    n = len(texto)
    max_longitud = max((len(s) for s in alfabeto), default=1)

    while i < n:
        encontrado = False
        for longitud in range(min(max_longitud, n - i), 0, -1):
            candidato = texto[i:i + longitud]
            if candidato in alfabeto:
                simbolos.append(candidato)
                i += longitud
                encontrado = True
                break
        if not encontrado:
            simbolos.append(texto[i])
            i += 1

    return simbolos


def formatear_produccion(produccion):
    """
    Convierte una produccion (tupla de simbolos) en texto legible.
    La tupla vacia (produccion nula/epsilon) se muestra con el
    simbolo lambda (λ). El usuario sigue ESCRIBIENDO la palabra
    "nula" al ingresar producciones (ver parsear_producciones); esto
    solo cambia como se MUESTRA en pantalla.

    Ejemplo: ('A','A','B') -> "AAB"   |   () -> "λ"
    """
    if produccion == ():
        return "λ"
    return "".join(produccion)


def formatear_gramatica(gramatica):
    """
    Convierte una Gramatica en un string legible, por ejemplo:

        G = ({A, B, C}, A, {1, 2}, P)
        A -> AAB / AA / CA / 1 / 2
        B -> BA / CABB / 1
        C -> CAB / BA / 1 / 2

    Retorna:
        str: representacion formateada de la gramatica.
    """
    variables_ordenadas = sorted(gramatica.variables)
    terminales_ordenados = sorted(gramatica.terminales)

    lineas = []
    lineas.append(
        "G = ({%s}, %s, {%s}, P)" % (
            ", ".join(variables_ordenadas),
            gramatica.inicial,
            ", ".join(terminales_ordenados),
        )
    )

    orden_variables = [gramatica.inicial] + [
        v for v in variables_ordenadas if v != gramatica.inicial
    ]

    for var in orden_variables:
        producciones = gramatica.producciones.get(var, [])
        if producciones:
            textos = [formatear_produccion(p) for p in producciones]
            lineas.append(f"{var} -> " + " / ".join(textos))
        else:
            lineas.append(f"{var} -> (sin producciones)")

    return "\n".join(lineas)


def parsear_producciones(texto_producciones, alfabeto=None):
    """
    Convierte texto ingresado por el usuario (ej. "AAB/AA/CA/1/2/nula")
    en una lista de tuplas de simbolos: [('A','A','B'), ('A','A'), ...,  ()]

    Si se provee 'alfabeto' (conjunto de simbolos validos conocidos,
    ej. cuando ya existen variables auxiliares de mas de un caracter),
    se usa tokenizar_produccion() para reconocer simbolos multi-caracter.
    Si no se provee, se asume que cada caracter individual es un simbolo
    (caso normal: entrada inicial del usuario con variables/terminales
    de una sola letra).

    Retorna:
        list[tuple[str, ...]]: lista de producciones (tuplas), sin duplicados.
    """
    producciones = []
    partes = texto_producciones.split("/")
    for parte in partes:
        p = parte.strip()
        if not p:
            continue
        if p.lower() == "nula":
            tupla = ()
        elif alfabeto:
            tupla = tuple(tokenizar_produccion(p, alfabeto))
        else:
            tupla = tuple(p)  # cada caracter = un simbolo

        if tupla not in producciones:
            producciones.append(tupla)

    return producciones


def imprimir_separador(titulo=""):
    """Imprime una linea separadora en consola, opcionalmente con titulo."""
    ancho = 70
    if titulo:
        print("\n" + "=" * ancho)
        print(titulo.center(ancho))
        print("=" * ancho)
    else:
        print("-" * ancho)

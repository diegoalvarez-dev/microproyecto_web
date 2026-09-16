"""
Modulo: gramatica.py
Define la clase Gramatica, que representa formalmente una
Gramatica Libre de Contexto G = (V, T, P, S)

    V (variables)   -> conjunto de variables o simbolos no terminales (VNT)
    T (terminales)  -> conjunto de simbolos terminales (VT)
    P (producciones)-> diccionario {variable: [lista de producciones]}
    S (inicial)     -> simbolo inicial (Vi)

IMPORTANTE sobre la representacion interna:
    Cada produccion se guarda como una TUPLA de simbolos, por ejemplo
    la produccion "AAB" se guarda como ('A', 'A', 'B'), y NO como el
    string "AAB". Esto es necesario porque las variables auxiliares
    que se crean en el proceso de Forma Normal de Chomsky (X1, X2,
    X3...) tienen MAS DE UN CARACTER, entonces no se pueden tratar
    como texto plano (leerlo caracter por caracter rompe todo en
    cuanto aparece una variable de mas de una letra).

    La produccion nula (epsilon) se representa como la tupla vacia:
    Gramatica.NULA = ()
"""

import copy


class Gramatica:
    """
    Representa una Gramatica Libre de Contexto.

    Atributos:
        variables (set[str]): conjunto de variables no terminales (VNT)
        terminales (set[str]): conjunto de simbolos terminales (VT)
        inicial (str): variable inicial (Vi)
        producciones (dict[str, list[tuple[str, ...]]]): reglas de
            produccion. Cada clave es una variable, cada valor es una
            lista de TUPLAS de simbolos (una tupla por produccion).
            La produccion nula se representa con la tupla vacia ().

    Ejemplo:
        variables = {"A", "B", "C"}
        terminales = {"1", "2"}
        inicial = "A"
        producciones = {
            "A": [("A","A","B"), ("A","A"), ("C","A"), ("1",), ("2",)],
            "B": [("B","A"), ("C","A","B","B"), ("1",)],
            "C": [("C","A","B"), ("B","A"), ("1",), ("2",)],
        }
    """

    # Tupla vacia = produccion nula (cadena vacia / epsilon)
    NULA = ()

    def __init__(self, variables, terminales, inicial, producciones):
        self.variables = set(variables)
        self.terminales = set(terminales)
        self.inicial = inicial
        # Se guarda una copia profunda para que cada Gramatica sea independiente
        self.producciones = copy.deepcopy(producciones)

    # ------------------------------------------------------------------
    # Utilidades basicas
    # ------------------------------------------------------------------

    def copia(self):
        """Devuelve una copia independiente (deep copy) de la gramatica."""
        return Gramatica(
            self.variables,
            self.terminales,
            self.inicial,
            self.producciones,
        )

    def agregar_produccion(self, variable, produccion):
        """
        Agrega una produccion a una variable, evitando duplicados (RNF08).
        'produccion' debe ser una tupla de simbolos, ej. ('A','B').
        """
        if variable not in self.producciones:
            self.producciones[variable] = []
        if produccion not in self.producciones[variable]:
            self.producciones[variable].append(produccion)

    def eliminar_produccion(self, variable, produccion):
        """Elimina una produccion especifica (tupla) de una variable si existe."""
        if variable in self.producciones and produccion in self.producciones[variable]:
            self.producciones[variable].remove(produccion)

    def eliminar_variable(self, variable):
        """
        Elimina una variable por completo:
            - la quita del conjunto de variables
            - elimina todas sus producciones
            - elimina cualquier produccion de OTRAS variables que la contenga
        """
        self.variables.discard(variable)

        if variable in self.producciones:
            del self.producciones[variable]

        for var in list(self.producciones.keys()):
            self.producciones[var] = [
                p for p in self.producciones[var]
                if variable not in p
            ]

    def todas_las_producciones(self):
        """
        Genera pares (variable, produccion) para recorrer facilmente
        todas las producciones de la gramatica.
        """
        for var, lista in self.producciones.items():
            for p in lista:
                yield var, p

    def __str__(self):
        """Representacion legible de la gramatica en formato A -> p1/p2/.../pn"""
        from .utils import formatear_gramatica
        return formatear_gramatica(self)

    def __repr__(self):
        return self.__str__()

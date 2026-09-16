"""
Modulo: adaptador.py
Convierte entre los objetos Python (Gramatica, PasoHistorial) usados
por la logica del proyecto, y estructuras JSON simples que se pueden
enviar/recibir por HTTP hacia el frontend en React.

Formato JSON de una gramatica:
{
  "variables": ["A", "B", "C"],
  "terminales": ["1", "2"],
  "inicial": "A",
  "producciones": {
      "A": [["A","A","B"], ["1"], []],   // [] representa la produccion nula
      "B": [["B","A"], ["1"]],
      "C": [["1"], ["2"]]
  }
}
"""

from .gramatica import Gramatica
from .utils import formatear_produccion


def gramatica_desde_json(data):
    """Construye un objeto Gramatica a partir de un dict JSON."""
    variables = set(data.get("variables", []))
    terminales = set(data.get("terminales", []))
    inicial = data.get("inicial", "")

    producciones = {}
    for variable, lista in data.get("producciones", {}).items():
        producciones[variable] = [tuple(p) for p in lista]

    return Gramatica(variables, terminales, inicial, producciones)


def gramatica_a_json(gramatica):
    """Convierte un objeto Gramatica a un dict serializable como JSON."""
    producciones = {}
    for variable, lista in gramatica.producciones.items():
        producciones[variable] = [list(p) for p in lista]

    return {
        "variables": sorted(gramatica.variables),
        "terminales": sorted(gramatica.terminales),
        "inicial": gramatica.inicial,
        "producciones": producciones,
        "texto": str(gramatica),  # representacion legible, lista para mostrar
    }


def paso_a_json(paso):
    """Convierte un PasoHistorial a un dict serializable como JSON."""
    return {
        "fase": paso.fase,
        "gramaticaAntes": gramatica_a_json(paso.gramatica_antes),
        "elementosIdentificados": paso.elementos_identificados or [],
        "produccionesEliminadas": paso.producciones_eliminadas or [],
        "produccionesAgregadas": paso.producciones_agregadas or [],
        "gramaticaDespues": gramatica_a_json(paso.gramatica_despues),
    }


def historial_a_json(historial):
    """Convierte un Historial completo (lista de pasos) a una lista JSON."""
    return [paso_a_json(p) for p in historial.pasos]

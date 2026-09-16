"""
Modulo: historial.py
Registra y muestra el historial completo de transformaciones
aplicadas a la gramatica (RF18, RF19, RNF10).

Cada paso guarda:
    - Nombre de la fase (ej. "Eliminacion de variables inutiles")
    - Gramatica antes de la transformacion
    - Elementos identificados (ej. variables inutiles encontradas)
    - Producciones eliminadas
    - Producciones agregadas
    - Gramatica resultante despues de la transformacion
"""


class PasoHistorial:
    """Representa un unico paso/fase del proceso de transformacion."""

    def __init__(self, fase, gramatica_antes, elementos_identificados,
                 producciones_eliminadas, producciones_agregadas, gramatica_despues):
        self.fase = fase
        self.gramatica_antes = gramatica_antes
        self.elementos_identificados = elementos_identificados
        self.producciones_eliminadas = producciones_eliminadas
        self.producciones_agregadas = producciones_agregadas
        self.gramatica_despues = gramatica_despues

    def __str__(self):
        """Formatea el paso para impresion en consola (RF18)."""
        lineas = []
        lineas.append(f">> FASE: {self.fase}")
        lineas.append("")
        lineas.append("Gramatica ANTES:")
        lineas.append(str(self.gramatica_antes))
        lineas.append("")

        if self.elementos_identificados:
            lineas.append("Elementos identificados: " + ", ".join(self.elementos_identificados))

        if self.producciones_eliminadas:
            lineas.append("Producciones eliminadas: " + ", ".join(self.producciones_eliminadas))
        elif self.producciones_eliminadas is not None:
            lineas.append("Producciones eliminadas: Ninguna")

        if self.producciones_agregadas:
            lineas.append("Producciones agregadas: " + ", ".join(self.producciones_agregadas))
        else:
            lineas.append("Producciones agregadas: Ninguna")

        lineas.append("")
        lineas.append("Gramatica DESPUES:")
        lineas.append(str(self.gramatica_despues))

        return "\n".join(lineas)


class Historial:
    """Contiene y administra la lista completa de pasos realizados."""

    def __init__(self):
        self.pasos = []

    def registrar(self, fase, gramatica_antes, elementos_identificados,
                  producciones_eliminadas, producciones_agregadas, gramatica_despues):
        """Crea y agrega un nuevo PasoHistorial a la lista."""
        paso = PasoHistorial(
            fase=fase,
            gramatica_antes=gramatica_antes,
            elementos_identificados=elementos_identificados,
            producciones_eliminadas=producciones_eliminadas,
            producciones_agregadas=producciones_agregadas,
            gramatica_despues=gramatica_despues,
        )
        self.pasos.append(paso)
        return paso

    def mostrar_todo(self):
        """Imprime en consola todos los pasos registrados, en orden."""
        if not self.pasos:
            print("(El historial esta vacio. Aun no se ha ejecutado ningun proceso.)")
            return

        for i, paso in enumerate(self.pasos, 1):
            print("\n" + "=" * 70)
            print(f"PASO {i}".center(70))
            print("=" * 70)
            print(paso)

    def limpiar(self):
        """Reinicia el historial (util para RF20 - reiniciar proceso)."""
        self.pasos = []

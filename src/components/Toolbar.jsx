/**
 * Barra de herramientas con una accion por cada fase del proceso
 * (equivalente a las opciones 3-9 del menu de consola original).
 */
export default function Toolbar({ acciones, cargando, faseActiva }) {
  const botones = [
    { id: "validar", etiqueta: "Validar" },
    { id: "inutiles", etiqueta: "Eliminar inútiles" },
    { id: "inalcanzables", etiqueta: "Eliminar inalcanzables" },
    { id: "nulas", etiqueta: "Eliminar nulas" },
    { id: "unitarias", etiqueta: "Eliminar unitarias" },
    { id: "chomsky", etiqueta: "Convertir a FNC" },
  ];

  return (
    <div className="flex flex-wrap gap-2">
      {botones.map((b) => (
        <button
          key={b.id}
          onClick={() => acciones[b.id]()}
          disabled={cargando}
          className={
            "rounded-md border px-3 py-1.5 text-sm font-medium transition disabled:cursor-not-allowed disabled:opacity-40 " +
            (faseActiva === b.id
              ? "border-amber bg-amber/10 text-amber"
              : "border-blueprint-line bg-blueprint-deep text-paper/80 hover:border-blueprint-mist hover:text-paper")
          }
        >
          {cargando && faseActiva === b.id ? "..." : b.etiqueta}
        </button>
      ))}

      <button
        onClick={() => acciones.completo()}
        disabled={cargando}
        className="rounded-md bg-amber px-3 py-1.5 text-sm font-semibold text-blueprint-deep transition hover:bg-amber-dim disabled:cursor-not-allowed disabled:opacity-40"
      >
        {cargando && faseActiva === "completo" ? "Procesando..." : "Ejecutar proceso completo"}
      </button>

      <button
        onClick={() => acciones.reiniciar()}
        className="ml-auto rounded-md border border-coral/40 px-3 py-1.5 text-sm font-medium text-coral/90 transition hover:border-coral hover:bg-coral/10"
      >
        Nueva gramática
      </button>
    </div>
  );
}

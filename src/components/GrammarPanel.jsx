/**
 * Muestra la gramatica actual en formato "esquema tecnico": lista de
 * V, T, S y las producciones en fuente monoespaciada, tal como se
 * verian en el tablero de un curso de teoria de la computacion.
 */
export default function GrammarPanel({ gramatica, titulo = "Gramática actual", sigma }) {
  if (!gramatica) return null;

  const { variables, terminales, inicial, producciones, texto } = gramatica;

  return (
    <div className="rounded-lg border border-blueprint-line bg-blueprint-panel/60 p-5">
      <div className="mb-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <h3 className="font-mono text-xs uppercase tracking-wide text-blueprint-mist">
            {titulo}
          </h3>
          {sigma != null && (
            <span className="rounded border border-amber/40 bg-amber/10 px-1.5 py-0.5 font-mono text-[11px] font-semibold text-amber">
              Σ{sigma}
            </span>
          )}
        </div>
        <span className="font-mono text-xs text-paper/40">
          G = ({variables.join(", ")}, {inicial}, {"{"}
          {terminales.join(", ")}
          {"}"}, P)
        </span>
      </div>

      <div className="grid gap-2 font-mono text-sm">
        {Object.keys(producciones)
          .sort((a, b) => (a === inicial ? -1 : b === inicial ? 1 : a.localeCompare(b)))
          .map((variable) => (
            <div key={variable} className="flex flex-wrap items-baseline gap-x-2">
              <span
                className={
                  "font-semibold " +
                  (variable === inicial ? "text-amber" : "text-blueprint-mist")
                }
              >
                {variable} →
              </span>
              <span className="text-paper/90">
                {producciones[variable].length === 0
                  ? "(sin producciones)"
                  : producciones[variable]
                      .map((p) => (p.length === 0 ? "λ" : p.join("")))
                      .join(" / ")}
              </span>
            </div>
          ))}
      </div>
    </div>
  );
}

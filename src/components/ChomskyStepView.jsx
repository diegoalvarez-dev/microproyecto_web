/**
 * Reproduce la forma en que se trabaja el proceso de Chomsky en el
 * cuaderno: por cada variable, se listan sus producciones originales
 * y cómo terminan. Las que ya van dentro de la variable (porque ya
 * cumplen FNC, o porque son el resultado final tras binarizar) se
 * marcan con un círculo ⭕. Las variables auxiliares nuevas (X1, X2...)
 * se marcan con un chulo ✓, en el mismo orden en que se crean.
 */

function Circulo() {
  return (
    <span className="inline-flex h-5 w-5 shrink-0 items-center justify-center rounded-full border-2 border-amber text-[10px] font-bold text-amber">
      {" "}
    </span>
  );
}

function Chulo() {
  return (
    <span className="inline-flex h-5 w-5 shrink-0 items-center justify-center text-emerald-400">
      ✓
    </span>
  );
}

function agruparPorVariable(detalle) {
  const grupos = [];
  const indice = {};
  for (const item of detalle) {
    if (!(item.variable in indice)) {
      indice[item.variable] = grupos.length;
      grupos.push({ variable: item.variable, items: [] });
    }
    grupos[indice[item.variable]].items.push(item);
  }
  return grupos;
}

export default function ChomskyStepView({ detalle }) {
  if (!detalle || detalle.length === 0) return null;

  const grupos = agruparPorVariable(detalle);

  return (
    <div className="flex flex-col gap-5 rounded-lg border border-blueprint-line bg-blueprint-panel/40 p-4">
      <div className="flex items-center justify-between">
        <h4 className="font-mono text-xs uppercase tracking-wide text-blueprint-mist">
          Proceso de Chomsky, paso a paso
        </h4>
        <div className="flex items-center gap-3 text-[11px] text-paper/50">
          <span className="inline-flex items-center gap-1">
            <Circulo /> va en la variable
          </span>
          <span className="inline-flex items-center gap-1">
            <Chulo /> variable nueva
          </span>
        </div>
      </div>

      {grupos.map((grupo) => (
        <div key={grupo.variable} className="flex flex-col gap-2">
          <p className="font-mono text-sm font-semibold text-blueprint-mist">
            {grupo.variable}
          </p>
          <div className="flex flex-col gap-1.5 pl-1">
            {grupo.items.map((item, i) => (
              <div key={i} className="flex flex-col gap-1">
                <div className="flex flex-wrap items-center gap-2 font-mono text-sm">
                  {!item.yaEraValida && (
                    <>
                      <span className="text-paper/40">
                        {grupo.variable} → {item.original}
                      </span>
                      <span className="text-paper/30">⇒</span>
                    </>
                  )}
                  <Circulo />
                  <span className="text-paper">
                    {grupo.variable} → {item.resultado}
                  </span>
                  {item.yaEraValida && (
                    <span className="text-[11px] text-paper/40">(ya en FNC)</span>
                  )}
                </div>

                {item.variablesNuevas.length > 0 && (
                  <div className="ml-6 flex flex-col gap-1 border-l border-blueprint-line pl-3">
                    {item.variablesNuevas.map((v) => (
                      <div
                        key={v.nombre}
                        className="flex items-center gap-2 font-mono text-sm text-emerald-300"
                      >
                        <Chulo />
                        <span>
                          {v.nombre} → {v.valor}
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

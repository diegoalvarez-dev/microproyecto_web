import ChomskyStepView from "./ChomskyStepView.jsx";

function listaProducciones(producciones) {
  const filas = [];
  for (const variable of Object.keys(producciones)) {
    const texto = producciones[variable]
      .map((p) => (p.length === 0 ? "λ" : p.join("")))
      .join(" / ");
    filas.push({ variable, texto });
  }
  return filas;
}

function Chip({ children, tono = "neutro" }) {
  const tonos = {
    neutro: "border-blueprint-line bg-blueprint-deep text-paper/70",
    agregada: "border-emerald-700/50 bg-emerald-950/40 text-emerald-300",
    eliminada: "border-coral/40 bg-coral/10 text-coral/90",
    identificado: "border-amber/40 bg-amber/10 text-amber",
  };
  return (
    <span className={`rounded border px-2 py-0.5 font-mono text-xs ${tonos[tono]}`}>
      {children}
    </span>
  );
}

function EtiquetaSigma({ sigmaAntes, sigmaDespues }) {
  if (sigmaAntes == null || sigmaDespues == null) return null;
  const cambio = sigmaAntes !== sigmaDespues;
  return (
    <span className="font-mono text-xs text-blueprint-mist">
      Σ{sigmaAntes} {cambio ? `→ Σ${sigmaDespues}` : "(sin cambios)"}
    </span>
  );
}

function PasoCard({ paso, numero }) {
  const esChomsky = Boolean(paso.detalleChomsky && paso.detalleChomsky.length > 0);

  return (
    <div className="rounded-lg border border-blueprint-line bg-blueprint-panel/40 p-4">
      <div className="mb-3 flex flex-wrap items-center gap-2">
        <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-amber font-mono text-xs font-bold text-blueprint-deep">
          {numero}
        </span>
        <h4 className="text-sm font-semibold text-paper">{paso.fase}</h4>
        <span className="ml-auto">
          <EtiquetaSigma sigmaAntes={paso.sigmaAntes} sigmaDespues={paso.sigmaDespues} />
        </span>
      </div>

      {esChomsky ? (
        <ChomskyStepView detalle={paso.detalleChomsky} />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <p className="mb-1.5 font-mono text-[11px] uppercase tracking-wide text-paper/40">
              Antes
            </p>
            <div className="space-y-0.5 font-mono text-xs text-paper/70">
              {listaProducciones(paso.gramaticaAntes.producciones).map((f) => (
                <div key={f.variable}>
                  <span className="text-blueprint-mist">{f.variable}</span> → {f.texto}
                </div>
              ))}
            </div>
          </div>
          <div>
            <p className="mb-1.5 font-mono text-[11px] uppercase tracking-wide text-paper/40">
              Después
            </p>
            <div className="space-y-0.5 font-mono text-xs text-paper/90">
              {listaProducciones(paso.gramaticaDespues.producciones).map((f) => (
                <div key={f.variable}>
                  <span className="text-blueprint-mist">{f.variable}</span> → {f.texto}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {!esChomsky && (paso.elementosIdentificados?.length > 0 ||
        paso.produccionesEliminadas?.length > 0 ||
        paso.produccionesAgregadas?.length > 0) && (
        <div className="mt-3 flex flex-col gap-1.5 border-t border-blueprint-line pt-3">
          {paso.elementosIdentificados?.length > 0 && (
            <div className="flex flex-wrap items-center gap-1.5">
              <span className="text-xs text-paper/40">Identificado:</span>
              {paso.elementosIdentificados.map((e, i) => (
                <Chip key={i} tono="identificado">{e}</Chip>
              ))}
            </div>
          )}
          {paso.produccionesEliminadas?.length > 0 && (
            <div className="flex flex-wrap items-center gap-1.5">
              <span className="text-xs text-paper/40">Eliminadas:</span>
              {paso.produccionesEliminadas.map((e, i) => (
                <Chip key={i} tono="eliminada">{e}</Chip>
              ))}
            </div>
          )}
          {paso.produccionesAgregadas?.length > 0 && (
            <div className="flex flex-wrap items-center gap-1.5">
              <span className="text-xs text-paper/40">Agregadas:</span>
              {paso.produccionesAgregadas.map((e, i) => (
                <Chip key={i} tono="agregada">{e}</Chip>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default function HistorialTimeline({ pasos }) {
  if (!pasos || pasos.length === 0) return null;

  return (
    <div className="flex flex-col gap-3">
      <h3 className="font-mono text-xs uppercase tracking-wide text-blueprint-mist">
        Historial de transformaciones
      </h3>
      {pasos.map((paso, i) => (
        <PasoCard key={i} paso={paso} numero={i + 1} />
      ))}
    </div>
  );
}

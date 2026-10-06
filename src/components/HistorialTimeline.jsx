import ChomskyStepView from "./ChomskyStepView.jsx";
import { formatearEncabezadoG } from "../lib/gramaticaUtils.js";

function listaProducciones(producciones) {
  const filas = [];
  for (const variable of Object.keys(producciones)) {
    const items = producciones[variable].map((p) =>
      p.length === 0 ? "λ" : p.join("")
    );
    filas.push({ variable, items });
  }
  return filas;
}

function esProduccionAgregada(variable, texto, produccionesAgregadas) {
  if (!produccionesAgregadas || produccionesAgregadas.length === 0) return false;
  const firma = `${variable} -> ${texto}`;
  return produccionesAgregadas.includes(firma);
}

/**
 * Determina a que tipo de fase pertenece un paso, a partir del texto
 * de paso.fase (ej. "Eliminación de producción nula: A → λ"), para
 * decidir COMO se debe interpretar paso.elementosIdentificados: a
 * veces es una variable completa, a veces una produccion puntual, a
 * veces un simbolo suelto que puede aparecer dentro de producciones
 * de cualquier variable.
 */
function obtenerTipoFase(fase) {
  if (!fase) return null;
  const f = fase.toLowerCase();
  if (f.includes("nula")) return "nulas";
  if (f.includes("unitaria")) return "unitarias";
  if (f.includes("inalcanzable")) return "inalcanzables";
  if (f.includes("inutil") || f.includes("inútil")) return "inutiles";
  return null;
}

/** Extrae el simbolo real de un identificado tipo "G (simbolo no declarado, tratado como inutil)" -> "G" */
function extraerSimbolo(identificado) {
  const match = identificado.match(/^([^\s(]+)/);
  return match ? match[1] : identificado;
}

/**
 * Decide si la FILA COMPLETA de una variable (su nombre y todas sus
 * producciones) debe marcarse en amarillo: solo aplica cuando la
 * variable misma fue identificada como inutil (sin producciones
 * propias) o como inalcanzable.
 */
function filaCompletaMarcada(variable, paso) {
  const identificados = paso.elementosIdentificados;
  if (!identificados || identificados.length === 0) return false;
  const tipo = obtenerTipoFase(paso.fase);
  if (tipo === "inalcanzables") return identificados.includes(variable);
  if (tipo === "inutiles") return identificados.includes(variable);
  return false;
}

/**
 * Decide si UNA producción puntual (dentro de una fila que no se
 * marco completa) debe pintarse en amarillo.
 */
function produccionMarcada(variable, texto, paso) {
  const identificados = paso.elementosIdentificados;
  if (!identificados || identificados.length === 0) return false;
  const tipo = obtenerTipoFase(paso.fase);

  if (tipo === "nulas") {
    // Solo la produccion vacia (lambda) de la variable identificada
    return texto === "λ" && identificados.includes(variable);
  }

  if (tipo === "unitarias") {
    // Las identificadas ya vienen como "Variable -> produccion"
    return identificados.includes(`${variable} -> ${texto}`);
  }

  if (tipo === "inutiles") {
    // Simbolos no declarados: se marca cualquier produccion, de
    // cualquier variable, que contenga ese simbolo dentro de si.
    return identificados.some((id) => {
      if (id === variable) return false; // eso ya se maneja como fila completa
      const simbolo = extraerSimbolo(id);
      return texto.includes(simbolo);
    });
  }

  // Fallback por si el texto de la fase no calza con ninguno de los
  // casos anteriores: intenta igualar la produccion puntual directa.
  return identificados.includes(`${variable} -> ${texto}`);
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
            <p className="mb-2 font-mono text-[11px] text-paper/40">
              {formatearEncabezadoG(paso.gramaticaAntes)}
            </p>
            <div className="space-y-0.5 font-mono text-xs text-paper/70">
              {listaProducciones(paso.gramaticaAntes.producciones).map((f) => {
                const filaCompleta = filaCompletaMarcada(f.variable, paso);
                return (
                  <div key={f.variable}>
                    <span
                      className={
                        filaCompleta ? "text-amber font-semibold" : "text-blueprint-mist"
                      }
                    >
                      {f.variable}
                    </span>{" "}
                    →{" "}
                    {f.items.map((texto, i) => {
                      const marcar = filaCompleta || produccionMarcada(f.variable, texto, paso);
                      return (
                        <span key={i}>
                          <span className={marcar ? "text-amber font-semibold" : ""}>
                            {texto}
                          </span>
                          {i < f.items.length - 1 ? " / " : ""}
                        </span>
                      );
                    })}
                  </div>
                );
              })}
            </div>
          </div>
          <div>
            <p className="mb-1.5 font-mono text-[11px] uppercase tracking-wide text-paper/40">
              Después
            </p>
            <p className="mb-2 font-mono text-[11px] text-paper/40">
              {formatearEncabezadoG(paso.gramaticaDespues)}
            </p>
            <div className="space-y-0.5 font-mono text-xs text-paper/90">
              {listaProducciones(paso.gramaticaDespues.producciones).map((f) => (
                <div key={f.variable}>
                  <span className="text-blueprint-mist">{f.variable}</span> →{" "}
                  {f.items.map((texto, i) => {
                    const nueva = esProduccionAgregada(
                      f.variable,
                      texto,
                      paso.produccionesAgregadas
                    );
                    return (
                      <span key={i}>
                        <span className={nueva ? "text-emerald-400 font-semibold" : ""}>
                          {texto}
                        </span>
                        {i < f.items.length - 1 ? " / " : ""}
                      </span>
                    );
                  })}
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
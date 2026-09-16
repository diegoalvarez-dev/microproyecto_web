import { useState } from "react";
import { parsearSimbolos, parsearProducciones } from "../lib/gramaticaUtils.js";

/**
 * Formulario de ingreso de la gramatica: variables, terminales,
 * simbolo inicial, y un campo de producciones por cada variable
 * declarada (se generan dinamicamente a medida que se escriben
 * las variables).
 */
export default function GrammarForm({ onRegistrar, onGenerar, cargando, generando }) {
  const [variablesTexto, setVariablesTexto] = useState("");
  const [terminalesTexto, setTerminalesTexto] = useState("");
  const [inicial, setInicial] = useState("");
  const [produccionesTexto, setProduccionesTexto] = useState({});

  const variables = parsearSimbolos(variablesTexto);
  const terminales = parsearSimbolos(terminalesTexto);

  function actualizarProduccion(variable, texto) {
    setProduccionesTexto((prev) => ({ ...prev, [variable]: texto }));
  }

  function limpiarCampos() {
    setVariablesTexto("");
    setTerminalesTexto("");
    setInicial("");
    setProduccionesTexto({});
  }

  function manejarEnvio(e) {
    e.preventDefault();

    const producciones = {};
    for (const v of variables) {
      producciones[v] = parsearProducciones(produccionesTexto[v] || "");
    }

    onRegistrar({
      variables,
      terminales,
      inicial: inicial.trim(),
      producciones,
    });
  }

  const listo =
    variables.length > 0 && terminales.length > 0 && inicial.trim() !== "";

  return (
    <>
      <div className="flex flex-col gap-2 rounded-lg border border-dashed border-amber/40 bg-amber/5 p-4">
        <span className="font-mono text-xs uppercase tracking-wide text-amber">
          Modo práctica
        </span>
        <p className="text-sm text-paper/70">
          Genera una gramática aleatoria, resuélvela a mano y compara tu
          respuesta con el "Proceso completo".
        </p>
        <button
          type="button"
          onClick={onGenerar}
          disabled={generando}
          className="mt-1 self-start rounded-md border border-amber/50 px-3 py-1.5 text-sm font-medium text-amber transition hover:bg-amber/10 disabled:cursor-not-allowed disabled:opacity-40"
        >
          {generando ? "Generando..." : "Generar ejercicio aleatorio"}
        </button>
      </div>

      <form
        onSubmit={manejarEnvio}
        className="flex flex-col gap-5 rounded-lg border border-blueprint-line bg-blueprint-panel/60 p-5"
      >
      <div>
        <h2 className="font-mono text-xs uppercase tracking-wide text-blueprint-mist">
          G = (V, T, S, P)
        </h2>
        <p className="mt-1 text-sm text-paper/70">
          Registra los componentes de tu Gramática Libre de Contexto.
        </p>
      </div>

      <Campo etiqueta="Variables (VNT)" ayuda="ej. A B C  ó  A,B,C">
        <input
          value={variablesTexto}
          onChange={(e) => setVariablesTexto(e.target.value)}
          placeholder="A B C"
          className="campo-input"
        />
      </Campo>

      <Campo etiqueta="Terminales (VT)" ayuda="ej. 1 2  ó  1,2">
        <input
          value={terminalesTexto}
          onChange={(e) => setTerminalesTexto(e.target.value)}
          placeholder="1 2"
          className="campo-input"
        />
      </Campo>

      <Campo etiqueta="Símbolo inicial">
        <input
          value={inicial}
          onChange={(e) => setInicial(e.target.value)}
          placeholder="A"
          className="campo-input w-24"
        />
      </Campo>

      {variables.length > 0 && (
        <div className="flex flex-col gap-3 border-t border-blueprint-line pt-4">
          <span className="font-mono text-xs uppercase tracking-wide text-blueprint-mist">
            Producciones
          </span>
          {variables.map((v) => (
            <div key={v} className="flex items-center gap-3">
              <span className="w-6 shrink-0 font-mono text-sm font-semibold text-amber">
                {v} →
              </span>
              <input
                value={produccionesTexto[v] || ""}
                onChange={(e) => actualizarProduccion(v, e.target.value)}
                placeholder="AAB/AA/CA/1/2/nula"
                className="campo-input font-mono text-sm"
              />
            </div>
          ))}
        </div>
      )}

        <button
          type="submit"
          disabled={!listo || cargando}
          className="mt-2 rounded-md bg-amber px-4 py-2 text-sm font-semibold text-blueprint-deep transition hover:bg-amber-dim disabled:cursor-not-allowed disabled:opacity-40"
        >
          {cargando ? "Registrando..." : "Registrar gramática"}
        </button>

        <button
          type="button"
          onClick={limpiarCampos}
          className="rounded-md border border-blueprint-line px-4 py-2 text-sm font-medium text-paper/60 transition hover:border-coral/50 hover:text-coral/80"
        >
          Limpiar campos
        </button>
      </form>
    </>
  );
}

function Campo({ etiqueta, ayuda, children }) {
  return (
    <label className="flex flex-col gap-1.5">
      <span className="text-sm font-medium text-paper/90">{etiqueta}</span>
      {children}
      {ayuda && <span className="text-xs text-paper/40">{ayuda}</span>}
    </label>
  );
}

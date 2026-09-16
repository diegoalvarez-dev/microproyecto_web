import { useState } from "react";
import GrammarForm from "./components/GrammarForm.jsx";
import GrammarPanel from "./components/GrammarPanel.jsx";
import Toolbar from "./components/Toolbar.jsx";
import HistorialTimeline from "./components/HistorialTimeline.jsx";
import ErrorBanner from "./components/ErrorBanner.jsx";
import { api } from "./lib/gramaticaUtils.js";

export default function App() {
  const [gramaticaOriginal, setGramaticaOriginal] = useState(null);
  const [gramaticaActual, setGramaticaActual] = useState(null);
  const [pasos, setPasos] = useState([]);
  const [errorInfo, setErrorInfo] = useState(null);
  const [cargando, setCargando] = useState(false);
  const [generando, setGenerando] = useState(false);
  const [faseActiva, setFaseActiva] = useState(null);
  const [resultadoFnc, setResultadoFnc] = useState(null);

  async function registrarGramatica(gramaticaJson) {
    setCargando(true);
    setErrorInfo(null);
    try {
      const resp = await api.validar(gramaticaJson);
      setGramaticaOriginal(resp.gramatica);
      setGramaticaActual(resp.gramatica);
      setPasos([]);
      setResultadoFnc(null);
      if (!resp.valida) {
        setErrorInfo({
          mensaje: "La gramática tiene errores. Corrígelos y vuelve a registrarla.",
          errores: resp.errores,
        });
      }
    } catch (e) {
      setErrorInfo({ mensaje: e.message, errores: e.errores });
    } finally {
      setCargando(false);
    }
  }

  async function ejecutarFase(nombreFase, llamada, { esFinal = false } = {}) {
    if (!gramaticaActual) return;
    setCargando(true);
    setFaseActiva(nombreFase);
    setErrorInfo(null);
    try {
      const resp = await llamada(gramaticaActual);

      if (nombreFase === "validar") {
        setErrorInfo(
          resp.valida
            ? null
            : { mensaje: "La gramática tiene errores:", errores: resp.errores }
        );
        setCargando(false);
        setFaseActiva(null);
        return;
      }

      setGramaticaActual(resp.gramatica);

      if (resp.paso) {
        setPasos((prev) => [...prev, resp.paso]);
      }
      if (resp.pasos) {
        setPasos((prev) => [...prev, ...resp.pasos]);
      }
      if (esFinal) {
        setResultadoFnc({
          valida: resp.esFncValida,
          invalidas: resp.produccionesInvalidas,
        });
      }
    } catch (e) {
      setErrorInfo({ mensaje: e.message, errores: e.errores });
    } finally {
      setCargando(false);
      setFaseActiva(null);
    }
  }

  async function generarEjercicio() {
    setGenerando(true);
    setErrorInfo(null);
    try {
      const resp = await api.generar();
      setGramaticaOriginal(resp.gramatica);
      setGramaticaActual(resp.gramatica);
      setPasos([]);
      setResultadoFnc(null);
    } catch (e) {
      setErrorInfo({ mensaje: e.message });
    } finally {
      setGenerando(false);
    }
  }

  function reiniciar() {
    setGramaticaOriginal(null);
    setGramaticaActual(null);
    setPasos([]);
    setErrorInfo(null);
    setResultadoFnc(null);
  }

  const acciones = {
    validar: () => ejecutarFase("validar", api.validar),
    inutiles: () => ejecutarFase("inutiles", api.inutiles),
    inalcanzables: () => ejecutarFase("inalcanzables", api.inalcanzables),
    nulas: () => ejecutarFase("nulas", api.nulas),
    unitarias: () => ejecutarFase("unitarias", api.unitarias),
    chomsky: () => ejecutarFase("chomsky", api.chomsky, { esFinal: true }),
    completo: () => ejecutarFase("completo", api.completo, { esFinal: true }),
    reiniciar,
  };

  return (
    <div className="min-h-screen">
      <header className="border-b border-blueprint-line/60 px-6 py-5">
        <div className="mx-auto flex max-w-6xl items-center justify-between">
          <div>
            <p className="font-mono text-xs uppercase tracking-wide text-blueprint-mist">
              Teoría de la Computación · Microproyecto 1
            </p>
            <h1 className="mt-1 text-xl font-semibold">
              Depurador de Gramáticas → Forma Normal de Chomsky
            </h1>
          </div>
        </div>
      </header>

      <main className="mx-auto grid max-w-6xl grid-cols-1 gap-6 px-6 py-8 lg:grid-cols-[360px_1fr]">
        {/* Columna izquierda: formulario de ingreso */}
        <div className="flex flex-col gap-4">
          <GrammarForm
            onRegistrar={registrarGramatica}
            onGenerar={generarEjercicio}
            cargando={cargando}
            generando={generando}
          />

          {gramaticaOriginal && (
            <GrammarPanel gramatica={gramaticaOriginal} titulo="Gramática original" />
          )}
        </div>

        {/* Columna derecha: proceso y resultados */}
        <div className="flex flex-col gap-5">
          {!gramaticaActual ? (
            <EstadoVacio />
          ) : (
            <>
              <Toolbar acciones={acciones} cargando={cargando} faseActiva={faseActiva} />

              <ErrorBanner mensaje={errorInfo?.mensaje} errores={errorInfo?.errores} />

              {resultadoFnc && (
                <div
                  className={
                    "rounded-lg border p-4 text-sm font-medium " +
                    (resultadoFnc.valida
                      ? "border-emerald-700/50 bg-emerald-950/30 text-emerald-300"
                      : "border-coral/40 bg-coral/10 text-coral")
                  }
                >
                  {resultadoFnc.valida
                    ? "✓ La gramática resultante cumple con la Forma Normal de Chomsky."
                    : "⚠ La gramática resultante NO cumple estrictamente la FNC."}
                  {!resultadoFnc.valida && resultadoFnc.invalidas?.length > 0 && (
                    <ul className="mt-2 list-inside list-disc font-mono text-xs">
                      {resultadoFnc.invalidas.map((inv, i) => (
                        <li key={i}>{inv}</li>
                      ))}
                    </ul>
                  )}
                </div>
              )}

              <GrammarPanel gramatica={gramaticaActual} titulo="Gramática actual" />

              <HistorialTimeline pasos={pasos} />
            </>
          )}
        </div>
      </main>
    </div>
  );
}

function EstadoVacio() {
  return (
    <div className="flex h-64 flex-col items-center justify-center rounded-lg border border-dashed border-blueprint-line text-center">
      <p className="font-mono text-sm text-paper/40">
        Registra una gramática para comenzar el proceso de depuración.
      </p>
    </div>
  );
}

export default function ErrorBanner({ mensaje, errores }) {
  if (!mensaje && (!errores || errores.length === 0)) return null;

  return (
    <div className="rounded-lg border border-coral/40 bg-coral/10 p-4">
      <p className="text-sm font-semibold text-coral">
        {mensaje || "La gramática tiene errores"}
      </p>
      {errores && errores.length > 0 && (
        <ul className="mt-2 list-inside list-disc space-y-1 text-sm text-coral/90">
          {errores.map((e, i) => (
            <li key={i}>{e}</li>
          ))}
        </ul>
      )}
    </div>
  );
}

// Utilidades del lado del cliente: parseo de texto de producciones
// y llamadas a la API. Replica en JS el mismo formato que usa
// utils.parsear_producciones() en Python: "AAB/AA/CA/1/2/nula"

/**
 * Convierte "AAB/AA/CA/1/2/nula" en [["A","A","B"],["A","A"],["C","A"],["1"],["2"],[]]
 * Cada caracter se trata como un simbolo individual (variables y
 * terminales de una sola letra, tal como se ingresan inicialmente).
 */
export function parsearProducciones(texto) {
  const partes = texto.split("/");
  const resultado = [];
  for (const parteCruda of partes) {
    const parte = parteCruda.trim();
    if (!parte) continue;
    const tupla = parte.toLowerCase() === "nula" ? [] : Array.from(parte);
    const yaExiste = resultado.some(
      (t) => t.length === tupla.length && t.every((s, i) => s === tupla[i])
    );
    if (!yaExiste) resultado.push(tupla);
  }
  return resultado;
}

/**
 * Convierte una tupla de simbolos de vuelta a texto legible, ej.
 * ["A","B"] -> "AB". La produccion nula (epsilon) se muestra con el
 * simbolo lambda (λ); el usuario sigue ESCRIBIENDO "nula" al ingresar
 * producciones, esto solo cambia como se ve en pantalla.
 */
export function formatearProduccion(tupla) {
  if (!tupla || tupla.length === 0) return "λ";
  return tupla.join("");
}

/** Convierte "A, B, C" o "A B C" en ["A","B","C"] */
export function parsearSimbolos(texto) {
  return texto
    .split(/[\s,]+/)
    .map((s) => s.trim())
    .filter(Boolean);
}

const API_BASE = "/api";

async function llamarApi(endpoint, gramaticaJson) {
  const res = await fetch(`${API_BASE}/${endpoint}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(gramaticaJson),
  });
  const data = await res.json();
  if (!res.ok) {
    const err = new Error(data.error || "Error en la peticion");
    err.errores = data.errores || [];
    throw err;
  }
  return data;
}

async function llamarApiGet(endpoint) {
  const res = await fetch(`${API_BASE}/${endpoint}`);
  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.error || "Error en la peticion");
  }
  return data;
}

export const api = {
  validar: (g) => llamarApi("validar", g),
  inutiles: (g) => llamarApi("inutiles", g),
  inalcanzables: (g) => llamarApi("inalcanzables", g),
  nulas: (g) => llamarApi("nulas", g),
  unitarias: (g) => llamarApi("unitarias", g),
  chomsky: (g) => llamarApi("chomsky", g),
  completo: (g) => llamarApi("completo", g),
  generar: () => llamarApiGet("generar"),
};

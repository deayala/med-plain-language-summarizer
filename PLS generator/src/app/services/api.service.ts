import { Injectable } from '@angular/core';
import { SummaryResponse } from '../models/summary';

/** Respuesta del clasificador PLS / NON PLS */
export interface ClassifyResponse {
  label: 'PLS' | 'NON_PLS';  // etiqueta de la clase
  score: number;             // confianza (0 a 1)
}

@Injectable({ providedIn: 'root' })
export class ApiService {

  // 🔎 NUEVO: mock del clasificador
  async classify(text: string): Promise<ClassifyResponse> {
    const clean = (text || '').toLowerCase();

    // Heurística súper simple solo para DEMO:
    // si el texto menciona "plain language" o "resumen en lenguaje sencillo"
    // lo tratamos como PLS, en caso contrario NON_PLS.
    const looksLikePls =
      clean.includes('plain language summary') ||
      clean.includes('resumen en lenguaje sencillo') ||
      clean.includes('plain-language summary') ||
      clean.length < 400; // textos muy cortos los podemos asumir como PLS para pruebas

    return {
      label: looksLikePls ? 'PLS' : 'NON_PLS',
      score: 0.9 // confianza fija de demo
    };
  }

  // ✅ EXISTENTE: mock de resumen (no lo tocamos)
  async summarize(text: string): Promise<SummaryResponse> {
    const summary =
      (text || '')
        .replace(/\s+/g, ' ')
        .split('.')
        .slice(0, 3)
        .join('. ')
        .trim() ||
      'Resumen de ejemplo (reemplazar con backend).';

    // Guardar en historial (máx 20)
    try {
      const list = JSON.parse(localStorage.getItem('pls_history') || '[]');
      list.unshift({
        id: String(Date.now()),
        label: (summary || text).slice(0, 24),
        text
      });
      localStorage.setItem('pls_history', JSON.stringify(list.slice(0, 20)));
    } catch {}

    return {
      summary,
      metrics: {
        contentPrecision: 92,
        readability: 92,
        overall: 90,
        labelPrecision: 'Alta',
        labelReadability: 'Fácil de leer · Nivel de Grado 8',
        labelOverall: 'A+'
      }
    };
  }
}


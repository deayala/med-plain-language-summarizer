
import { Injectable } from '@angular/core';
import { SummaryResponse } from '../models/summary';

@Injectable({ providedIn: 'root' })
export class ApiService {
  // TODO: reemplazar por HttpClient cuando el backend esté listo
  async summarize(text: string): Promise<SummaryResponse> {
    const summary = (text || '').replace(/\s+/g, ' ').split('.').slice(0, 3).join('. ').trim()
                    || 'Resumen de ejemplo (reemplazar con backend).';

    // Guardar en historial (máx 20)
    try {
      const list = JSON.parse(localStorage.getItem('pls_history') || '[]');
      list.unshift({ id: String(Date.now()), label: (summary || text).slice(0, 24), text });
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

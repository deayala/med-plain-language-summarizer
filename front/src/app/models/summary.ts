export interface SummaryResponse {
  summary: string;
  metrics: {
    contentPrecision: number;    // 0..100 (BERTScore/AlignScore normalizado)
    readability: number;         // 0..100 (FRE normalizado)
    overall: number;             // 0..100 (promedio legibilidad)
    labelPrecision: 'Alta'|'Media'|'Baja';
    labelReadability: string;    // "Fácil de leer · Nivel de Grado 8"
    labelOverall: string;        // "A+" / "Excelente" / etc.
  }
}


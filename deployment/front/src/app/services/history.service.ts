import { Injectable, signal } from '@angular/core';
import { HistoryEntry, HistoryEntryInput } from '../models/history';

const STORAGE_KEY = 'pls_history';
const HISTORY_LIMIT = 20;

@Injectable({ providedIn: 'root' })
export class HistoryService {
  readonly items = signal<HistoryEntry[]>(this.readFromStorage());

  add(input: HistoryEntryInput): HistoryEntry {
    const entry: HistoryEntry = {
      id: crypto.randomUUID ? crypto.randomUUID() : String(Date.now()),
      createdAt: new Date().toISOString(),
      label: input.label,
      source: input.source,
      summary: input.summary,
      readability: input.readability,
      classificationLabel: input.classificationLabel,
      classificationScore: input.classificationScore,
      alignScore: null,
      alignScoreModel: null
    };
    this.items.update(list => {
      const next = [entry, ...list].slice(0, HISTORY_LIMIT);
      this.persist(next);
      return next;
    });
    return entry;
  }

  updateAlignScore(id: string, alignScore: number, model: string | null) {
    this.items.update(list => {
      const next = list.map(item =>
        item.id === id ? { ...item, alignScore, alignScoreModel: model } : item
      );
      this.persist(next);
      return next;
    });
  }

  remove(id: string) {
    this.items.update(list => {
      const next = list.filter(item => item.id !== id);
      this.persist(next);
      return next;
    });
  }

  getById(id: string): HistoryEntry | undefined {
    return this.items().find(item => item.id === id);
  }

  private readFromStorage(): HistoryEntry[] {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return [];
      const parsed = JSON.parse(raw);
      if (!Array.isArray(parsed)) return [];
      return parsed
        .map(item => this.normalize(item))
        .filter((item): item is HistoryEntry => Boolean(item));
    } catch {
      return [];
    }
  }

  private normalize(data: any): HistoryEntry | null {
    if (!data || typeof data !== 'object') return null;
    const id = typeof data.id === 'string' ? data.id : String(Date.now());
    const createdAt = typeof data.createdAt === 'string' ? data.createdAt : new Date().toISOString();
    const label = typeof data.label === 'string' ? data.label : 'Resumen';
    const source = typeof data.source === 'string' ? data.source : (data.text ?? '');
    const summary = typeof data.summary === 'string' ? data.summary : '';
    const readability = data.readability ?? null;
    const classificationLabel =
      data.classificationLabel === 'PLS' || data.classificationLabel === 'NON_PLS'
        ? data.classificationLabel
        : 'NON_PLS';
    const classificationScore =
      typeof data.classificationScore === 'number' ? data.classificationScore : null;
    const alignScore = typeof data.alignScore === 'number' ? data.alignScore : null;
    const alignScoreModel = typeof data.alignScoreModel === 'string' ? data.alignScoreModel : null;

    return {
      id,
      createdAt,
      label,
      source,
      summary,
      readability,
      classificationLabel,
      classificationScore,
      alignScore,
      alignScoreModel
    };
  }

  private persist(list: HistoryEntry[]) {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(list));
    } catch {
      // ignorar problemas de almacenamiento
    }
  }
}

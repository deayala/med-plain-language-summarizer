import { ReadabilityBreakdown } from './summary';

export type HistoryClassification = 'PLS' | 'NON_PLS';

export interface HistoryEntry {
  id: string;
  createdAt: string; // ISO local timestamp
  label: string;
  source: string;
  summary: string;
  readability: ReadabilityBreakdown | null;
  classificationLabel: HistoryClassification;
  classificationScore: number | null;
  alignScore: number | null;
  alignScoreModel: string | null;
}

export interface HistoryEntryInput {
  label: string;
  source: string;
  summary: string;
  readability: ReadabilityBreakdown | null;
  classificationLabel: HistoryClassification;
  classificationScore: number | null;
}

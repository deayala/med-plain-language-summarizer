import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { firstValueFrom } from 'rxjs';
import { SummaryResponse } from '../models/summary';
import { environment } from '../../environments/environment';

export interface ClassifyResponse {
  text: string;
  label: 'pls' | 'non_pls';
  score: number;
  threshold: number;
}

@Injectable({ providedIn: 'root' })
export class ApiService {
  private readonly baseUrl: string;

  constructor(private http: HttpClient) {
    this.baseUrl = this.resolveBaseUrl(environment.apiBaseUrl);
  }

  classify(text: string): Promise<ClassifyResponse> {
    return firstValueFrom(
      this.http.post<ClassifyResponse>(this.endpoint('/classify'), { text: text.trim() })
    );
  }

  async summarize(article: string): Promise<SummaryResponse> {
    const response = await firstValueFrom(
      this.http.post<SummaryResponse>(this.endpoint('/summarize'), { article: article.trim() })
    );
    this.persistHistory(article, response.summary);
    return response;
  }

  private endpoint(path: string): string {
    const normalized = path.startsWith('/') ? path : `/${path}`;
    return `${this.baseUrl}${normalized}`;
  }

  private resolveBaseUrl(raw: string): string {
    const trimmed = (raw || '').trim();
    if (!trimmed) {
      return `${window.location.origin}/api/v1`;
    }
    if (/^https?:\/\//i.test(trimmed)) {
      return trimmed.replace(/\/+$/, '');
    }
    const prefix = trimmed.startsWith('/') ? trimmed : `/${trimmed}`;
    return `${window.location.origin}${prefix}`.replace(/\/+$/, '');
  }

  private persistHistory(source: string, summary: string) {
    try {
      const list = JSON.parse(localStorage.getItem('pls_history') || '[]');
      list.unshift({
        id: String(Date.now()),
        label: (summary || source).slice(0, 48),
        text: source
      });
      localStorage.setItem('pls_history', JSON.stringify(list.slice(0, 20)));
    } catch {
      // ignore history failures
    }
  }
}

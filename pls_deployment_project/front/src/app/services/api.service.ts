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

export interface AlignScoreResponse {
  align_score: number;
  model_name: string;
  device: string;
  batch_size: number;
}

@Injectable({ providedIn: 'root' })
export class ApiService {
  private readonly baseUrl: string;
  private readonly alignUrl: string;

  constructor(private http: HttpClient) {
    this.baseUrl = this.resolveBaseUrl(environment.apiBaseUrl, 8080, '/api/v1');
    this.alignUrl = this.resolveBaseUrl(environment.alignApiBaseUrl, 8081, '');
  }

  classify(text: string): Promise<ClassifyResponse> {
    return firstValueFrom(
      this.http.post<ClassifyResponse>(this.endpoint('/classify'), { text: text.trim() })
    );
  }

  async summarize(article: string): Promise<SummaryResponse> {
    return firstValueFrom(
      this.http.post<SummaryResponse>(this.endpoint('/summarize'), { article: article.trim() })
    );
  }

  alignScore(technicalText: string, generation: string): Promise<AlignScoreResponse> {
    return firstValueFrom(
      this.http.post<AlignScoreResponse>(this.alignEndpoint('/align'), {
        technical_text: technicalText.trim(),
        generation: generation.trim()
      })
    );
  }

  private endpoint(path: string): string {
    const normalized = path.startsWith('/') ? path : `/${path}`;
    return `${this.baseUrl}${normalized}`;
  }

  private alignEndpoint(path: string): string {
    const normalized = path.startsWith('/') ? path : `/${path}`;
    return `${this.alignUrl}${normalized}`;
  }

  private resolveBaseUrl(raw: string, fallbackPort: number, defaultPath: string): string {
    const trimmed = (raw || '').trim();
    const baseOrigin = this.originWithoutPort();
    const normalizedPath = defaultPath ? (defaultPath.startsWith('/') ? defaultPath : `/${defaultPath}`) : '';

    if (!trimmed) {
      return `${baseOrigin}:${fallbackPort}${normalizedPath}`.replace(/\/+$/, '');
    }
    if (/^https?:\/\//i.test(trimmed)) {
      return trimmed.replace(/\/+$/, '');
    }
    if (trimmed.startsWith(':')) {
      const slashIndex = trimmed.indexOf('/', 1);
      const port = slashIndex === -1 ? trimmed.slice(1) : trimmed.slice(1, slashIndex);
      const rest = slashIndex === -1 ? '' : trimmed.slice(slashIndex);
      return `${baseOrigin}:${port}${rest}`.replace(/\/+$/, '');
    }
    const prefix = trimmed.startsWith('/') ? trimmed : `/${trimmed}`;
    return `${baseOrigin}${prefix}`.replace(/\/+$/, '');
  }

  private originWithoutPort(): string {
    const { protocol, hostname } = window.location;
    return `${protocol}//${hostname}`;
  }
}

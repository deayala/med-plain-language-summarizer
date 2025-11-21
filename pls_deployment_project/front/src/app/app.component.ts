import { Component, ViewEncapsulation } from '@angular/core';
import { CommonModule } from '@angular/common';

import { SidebarComponent } from './components/sidebar/sidebar.component';
import { UploadComponent } from './components/upload/upload.component';
import { SummaryComponent } from './components/summary/summary.component';
import { ApiService } from './services/api.service';
import { SummaryResponse } from './models/summary';

@Component({
  selector: 'app-root',
  standalone: true,
  encapsulation: ViewEncapsulation.None,
  imports: [
    CommonModule,
    SidebarComponent,
    UploadComponent,
    SummaryComponent
  ],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent {

  // ====== Texto original / resumen ======
  original = '';
  summary  = '';

  // ====== Clasificador PLS / NON_PLS ======
  classificationLabel: 'PLS' | 'NON_PLS' | null = null;
  classificationScore: number | null = null;
  classificationMessage = '';
  isClassifying = false;
  isSummarizing = false;

  // ====== Factualidad ======
  factualityInitial   = 0;
  factualityGenerated = 0;

  // ====== BERTScore ======
  bertInitial   = 0;
  bertGenerated = 0;
  alignScoreGenerated: number | null = null;
  alignScoreModel: string | null = null;
  isAlignScoring = false;

  // ====== Densidad del texto ======
  wordsInitial    = 0;
  wordsGenerated  = 0;
  charsInitial    = 0;
  charsGenerated  = 0;

  // ====== Readability ======
  readabilityInitial   = 0;
  readabilityGenerated = 0;
  readabilityValue = 0;
  readabilityLabel = 'Sin datos – Agrega un texto para evaluarlo';

  constructor(private api: ApiService) {}

  // ================================================
  // 🔥 MÉTODO PRINCIPAL: CLASIFICAR Y GENERAR
  // ================================================
  async generate() {
    const payload = this.original.trim();
    if (!payload) {
      return;
    }

    this.summary = '';
    this.classificationLabel = null;
    this.classificationScore = null;
    this.classificationMessage = '';
    this.isSummarizing = false;
    this.isClassifying = true;

    try {
      const cls = await this.api.classify(payload);
      this.classificationLabel = cls.label === 'pls' ? 'PLS' : 'NON_PLS';
      this.classificationScore = cls.score;
    } catch (error) {
      console.error('Classification failed', error);
      this.classificationMessage = 'No se pudo clasificar el texto. Intenta nuevamente.';
      this.isClassifying = false;
      return;
    }

    this.isClassifying = false;

    if (this.classificationLabel === 'PLS') {
      this.summary = '';
      this.alignScoreGenerated = null;
      this.alignScoreModel = null;
      this.isAlignScoring = false;
      return;
    }

    this.isSummarizing = true;
    try {
      const result = await this.api.summarize(payload);
      this.applySummary(result);
      this.isSummarizing = false; // hide PLS spinner once summary is ready
      await this.applyAlignScore(payload, result.summary);
    } catch (error) {
      console.error('Summarization failed', error);
      this.classificationMessage =
        'Ocurrió un problema al generar el resumen. Por favor intenta nuevamente.';
      this.summary = '';
    } finally {
      this.isSummarizing = false;
    }
  }

  resetSummary() {
    this.original = '';
    this.summary = '';
    this.classificationLabel = null;
    this.classificationScore = null;
    this.classificationMessage = '';
    this.isClassifying = false;
    this.isSummarizing = false;

    this.factualityInitial = 0;
    this.factualityGenerated = 0;
    this.bertInitial = 0;
    this.bertGenerated = 0;
    this.alignScoreGenerated = null;
    this.alignScoreModel = null;
    this.isAlignScoring = false;
    this.wordsInitial = 0;
    this.wordsGenerated = 0;
    this.charsInitial = 0;
    this.charsGenerated = 0;
    this.readabilityInitial = 0;
    this.readabilityGenerated = 0;
    this.readabilityValue = 0;
    this.readabilityLabel = 'Sin datos – Agrega un texto para evaluarlo';
  }

  private applySummary(response: SummaryResponse) {
    this.summary = response.summary;

    const source = response.readability?.source;
    const generated = response.readability?.generated;

    this.wordsInitial = this.countWords(this.original);
    this.wordsGenerated = this.countWords(response.summary);
    this.charsInitial = this.original.length;
    this.charsGenerated = response.summary.length;

    this.factualityInitial = 100;
    this.factualityGenerated = this.percentFrom(generated?.number_recall ?? 1);

    this.readabilityInitial = source?.flesch_reading_ease ?? 0;
    this.readabilityGenerated = generated?.flesch_reading_ease ?? 0;
    this.readabilityValue = this.percentFrom(this.readabilityGenerated / 100);
    this.readabilityLabel = this.describeReadability(this.readabilityGenerated);

    this.alignScoreGenerated = null;
    this.alignScoreModel = null;
    this.isAlignScoring = false;
  }

  private async applyAlignScore(source: string, summary: string): Promise<void> {
    const technical = source.trim();
    const generation = summary.trim();
    if (!technical || !generation) {
      this.alignScoreGenerated = null;
      return;
    }
    this.isAlignScoring = true;
    try {
      const response = await this.api.alignScore(technical, generation);
      this.alignScoreGenerated = response.align_score;
      this.alignScoreModel = response.model_name;
    } catch (error) {
      console.error('AlignScore failed', error);
      this.alignScoreGenerated = null;
    } finally {
      this.isAlignScoring = false;
    }
  }

  private countWords(text: string): number {
    const clean = text.trim();
    return clean ? clean.split(/\s+/).length : 0;
  }

  private percentFrom(value: number): number {
    const score = this.unitScore(value);
    return Math.round(score * 100);
  }

  private unitScore(value: number): number {
    if (!Number.isFinite(value)) {
      return 0;
    }
    return Math.max(0, Math.min(1, value));
  }

  private describeReadability(score: number): string {
    if (!Number.isFinite(score)) {
      return 'Sin datos – Agrega un texto para evaluarlo';
    }
    if (score >= 90) {
      return 'Muy fácil – Nivel de Grado 5 o menos';
    }
    if (score >= 70) {
      return 'Fácil – Nivel de Grado 7';
    }
    if (score >= 60) {
      return 'Bastante fácil – Nivel de Grado 8-9';
    }
    if (score >= 50) {
      return 'Aceptable – Nivel de Bachillerato';
    }
    if (score >= 30) {
      return 'Difícil – Nivel universitario';
    }
    return 'Muy difícil – Nivel académico avanzado';
  }
}

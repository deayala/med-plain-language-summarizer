import { Component, ViewEncapsulation } from '@angular/core';
import { CommonModule } from '@angular/common';

import { SidebarComponent } from './components/sidebar/sidebar.component';
import { UploadComponent } from './components/upload/upload.component';
import { SummaryComponent } from './components/summary/summary.component';
import { ApiService } from './services/api.service';

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
  factualityInitial   = 92;
  factualityGenerated = 96;

  // ====== BERTScore ======
  bertInitial   = 0.844;
  bertGenerated = 0.871;

  // ====== Densidad del texto ======
  wordsInitial    = 2925;
  wordsGenerated  = 159;
  charsInitial    = 4550;
  charsGenerated  = 990;

  // ====== Readability ======
  readabilityInitial   = 34.25;
  readabilityGenerated = 50.21;
  readabilityValue = 92;
  readabilityLabel = 'Fácil de leer – Nivel de Grado 8';

  constructor(private api: ApiService) {}

  // ================================================
  // 🔥 MÉTODO PRINCIPAL: CLASIFICAR Y GENERAR
  // ================================================
  async generate() {
    if (!this.original?.trim()) return;

    this.classificationMessage = '';
    this.isClassifying = true;
    this.isSummarizing = false;

    // 1️⃣ CLASIFICAR PRIMERO
    const cls = await this.api.classify(this.original);
    this.classificationLabel = cls.label;
    this.classificationScore = cls.score;
    this.isClassifying = false;

    // ----- SI ES PLS: NO GENERAR RESUMEN -----
    if (cls.label === 'PLS') {
      this.summary = '';
      this.classificationMessage =
        'Este texto ya es un Plain Language Summary (PLS). No es necesario generar un resumen.';
      return;
    }

    // 2️⃣ SI ES NON_PLS → GENERAR EL RESUMEN
    this.isSummarizing = true;

    const res = await this.api.summarize(this.original);
    this.summary = res.summary;

    // (Tus valores actuales siguen mock, no pasa nada)
    this.factualityInitial   = 92;
    this.factualityGenerated = 96;

    this.bertInitial   = 0.844;
    this.bertGenerated = 0.871;

    this.wordsInitial   = 2925;
    this.wordsGenerated = 159;
    this.charsInitial   = 4550;
    this.charsGenerated = 990;

    this.readabilityInitial   = 34.25;
    this.readabilityGenerated = 50.21;
    this.readabilityValue     = 92;
    this.readabilityLabel     = 'Fácil de leer – Nivel de Grado 8';

    this.isSummarizing = false;
  }

resetSummary() {
  this.original = '';
  this.summary = '';
  this.classificationLabel = null;
  this.classificationScore = null;
  this.classificationMessage = '';
  this.isClassifying = false;
  this.isSummarizing = false;

  this.factualityInitial   = 0;
  this.factualityGenerated = 0;
  this.bertInitial   = 0;
  this.bertGenerated = 0;
  this.wordsInitial   = 0;
  this.wordsGenerated = 0;
  this.charsInitial   = 0;
  this.charsGenerated = 0;
  this.readabilityInitial   = 0;
  this.readabilityGenerated = 0;
  this.readabilityValue     = 0;
}

}

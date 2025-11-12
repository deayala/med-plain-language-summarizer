import { Component, ViewEncapsulation } from '@angular/core';
import { SidebarComponent } from './components/sidebar/sidebar.component';
import { UploadComponent } from './components/upload/upload.component';
import { SummaryComponent } from './components/summary/summary.component';
import { MetricsComponent } from './components/metrics/metrics.component';
import { ApiService } from './services/api.service';

@Component({
  encapsulation: ViewEncapsulation.None,
  selector: 'app-root',
  standalone: true,
  imports: [SidebarComponent, UploadComponent, SummaryComponent, MetricsComponent],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss'],
  // ⬇️ reemplaza por esto:
  styles: [`
    .page {
      display: grid;
      grid-template-columns: 300px 1fr;  /* NAV | CONTENIDO */
      gap: 20px;
      padding: 20px;
      align-items: start;               /* alinea arriba */
      min-height: calc(100vh - 60px);
    }
    .content { display: flex; flex-direction: column; gap: 24px; }
    .compare { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
  `]
})
export class AppComponent {
  original = '';
  summary  = '';

  precision = 0;
  readability = 0;
  overall = 0;
  labelPrecision = '';
  labelReadability = '';
  labelOverall = '';

  constructor(private api: ApiService) {
    window.addEventListener('historySelected', (e: any) => { this.original = e.detail; });
  }

  async generate() {
    const res = await this.api.summarize(this.original);
    this.summary = res.summary;
    this.precision = res.metrics.contentPrecision;
    this.readability = res.metrics.readability;
    this.overall = res.metrics.overall;
    this.labelPrecision = res.metrics.labelPrecision;
    this.labelReadability = res.metrics.labelReadability;
    this.labelOverall = res.metrics.labelOverall;
  }
ngOnInit(){
  this.precision = 92;
  this.readability = 92;
  this.overall = 90;
  this.labelPrecision = 'Alta';
  this.labelReadability = 'Fácil de leer · Nivel de Grado 8';
  this.labelOverall = 'A+';
}  
}

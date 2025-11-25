import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-metrics',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './metrics.component.html',
  styleUrls: ['./metrics.component.scss']
})
export class MetricsComponent {
  /** Título de la tarjeta */
  @Input() title = '';

  /** 0..100 (para barra y gauge) */
  @Input() value = 0;

  /** Texto corto de apoyo (p.e. "Alta", "Fácil de leer · Grado 8", "A+") */
  @Input() note = '';

  /** bar | gauge | badge */
  @Input() variant: 'bar' | 'gauge' | 'badge' = 'bar';

  /** Colorea según valor (solo gauge) */
  @Input() colored = true;

  // ---- Cálculo del gauge (SVG) ----
  readonly r = 28;
  get circumference() { return 2 * Math.PI * this.r; }
  get dashOffset() { return this.circumference * (100 - Math.min(Math.max(this.value, 0), 100)) / 100; }

  // ---- Colores semáforo para gauge ----
  get ringColor(): string {
    if (!this.colored) return '#94a3b8';       // gris
    if (this.value >= 85) return '#16a34a';    // verde
    if (this.value >= 60) return '#f59e0b';    // amarillo
    return '#ef4444';                           // rojo
  }
}

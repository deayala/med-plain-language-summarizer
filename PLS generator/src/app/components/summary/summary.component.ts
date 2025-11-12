import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-summary',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './summary.component.html',
  styleUrls: ['./summary.component.scss']
})
export class SummaryComponent {
  @Input() title = '';
  @Input() text = '';
  @Input() isSummary = false;

  copy() {
    navigator.clipboard.writeText(this.text || '');
  }

  download() {
    const blob = new Blob([this.text || ''], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'resumen.txt';
    link.click();
    URL.revokeObjectURL(url);
  }
}


import { Component, EventEmitter, Input, Output } from '@angular/core';

@Component({
  selector: 'app-upload',
  standalone: true,
  templateUrl: './upload.component.html',
  styleUrls: ['./upload.component.scss']
})
export class UploadComponent {
  @Input() text = '';
  @Output() textChange = new EventEmitter<string>();
  @Output() generate = new EventEmitter<void>();

  onFile(e: Event){
    const input = e.target as HTMLInputElement;
    const f = input.files && input.files[0];
    if(!f) return;

    if (f.type === 'text/plain') {
      const reader = new FileReader();
      reader.onload = () => this.textChange.emit(String(reader.result || ''));
      reader.readAsText(f, 'utf-8');
    } else {
      alert('Por ahora solo .txt; el PDF se parseará en backend.');
    }
  }
}

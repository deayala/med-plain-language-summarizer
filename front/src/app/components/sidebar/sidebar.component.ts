import { Component, signal } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './sidebar.component.html',
  styleUrls: ['./sidebar.component.scss']
})
export class SidebarComponent {
  open = signal(true);
  history = signal<any[]>([]);

  toggle() { this.open.set(!this.open()); }
  select(item: any) { window.dispatchEvent(new CustomEvent('historySelected', { detail: item })); }
  remove(item: any) {
    const next = this.history().filter(h => h.id !== item.id);
    this.history.set(next);
    localStorage.setItem('pls_history', JSON.stringify(next));
  }
}

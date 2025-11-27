import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HistoryService } from '../../services/history.service';
import { HistoryEntry } from '../../models/history';

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './sidebar.component.html',
  styleUrls: ['./sidebar.component.scss']
})
export class SidebarComponent {
  open = true;

  constructor(public history: HistoryService) {}

  toggle() { this.open = !this.open; }
  select(item: HistoryEntry) {
    window.dispatchEvent(new CustomEvent('historySelected', { detail: item }));
  }
  remove(item: HistoryEntry) {
    this.history.remove(item.id);
  }
  trackById(_index: number, item: HistoryEntry) {
    return item.id;
  }
}

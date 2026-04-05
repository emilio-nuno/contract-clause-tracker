import { Component, OnInit, inject } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { DatePipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatSelectModule } from '@angular/material/select';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTooltipModule } from '@angular/material/tooltip';

import { ApiService, ContractDetail as ContractDetailData, SentenceOut, ClauseOut } from '../../services/api';

@Component({
  selector: 'app-contract-detail',
  templateUrl: './contract-detail.html',
  styleUrl: './contract-detail.css',
  imports: [
    DatePipe,
    FormsModule,
    MatToolbarModule,
    MatButtonModule,
    MatIconModule,
    MatSelectModule,
    MatFormFieldModule,
    MatProgressSpinnerModule,
    MatTooltipModule,
  ],
})
export class ContractDetail implements OnInit {
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private api = inject(ApiService);

  contract: ContractDetailData | null = null;
  clauses: ClauseOut[] = [];
  loading = true;
  error = false;
  editingSentenceId: string | null = null;

  private clauseNameToId = new Map<string, string>();

  ngOnInit() {
    const id = this.route.snapshot.paramMap.get('id')!;
    this.api.getClauses().subscribe(c => {
      this.clauses = c;
      this.clauseNameToId = new Map(c.map(clause => [clause.name, clause.id]));
    });
    this.api.getContract(id).subscribe({
      next: (c: ContractDetailData) => { this.contract = c; this.loading = false; },
      error: () => { this.loading = false; this.error = true; },
    });
  }

  back() {
    this.router.navigate(['/']);
  }

  startEdit(sentenceId: string, event: Event) {
    event.stopPropagation();
    this.editingSentenceId = sentenceId;
  }

  applyLabel(sentence: SentenceOut, clauseId: string | null) {
    this.api.updateSentenceLabel(sentence.id, clauseId).subscribe(updated => {
      sentence.label_name = updated.label_name;
      sentence.label_color = updated.label_color;
      this.editingSentenceId = null;
    });
  }

  cancelEdit(event: Event) {
    event.stopPropagation();
    this.editingSentenceId = null;
  }

  clauseIdForSentence(sentence: SentenceOut): string | null {
    if (!sentence.label_name) return null;
    return this.clauseNameToId.get(sentence.label_name) ?? null;
  }
}

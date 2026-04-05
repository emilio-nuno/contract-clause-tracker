import { Component, OnInit, inject } from '@angular/core';
import { Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatTableModule } from '@angular/material/table';
import { MatDialog } from '@angular/material/dialog';
import { DatePipe } from '@angular/common';

import { ApiService, ContractSummary, ClauseOut } from '../../services/api';
import { UploadDialog } from './upload-dialog/upload-dialog';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.css',
  imports: [
    FormsModule,
    MatToolbarModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatButtonModule,
    MatIconModule,
    MatTableModule,
    DatePipe,
  ],
})
export class Dashboard implements OnInit {
  private api = inject(ApiService);
  private router = inject(Router);
  private dialog = inject(MatDialog);

  contracts: ContractSummary[] = [];
  clauses: ClauseOut[] = [];
  search = '';
  selectedClauseId = '';

  readonly columns = ['filename', 'uploaded_at'];

  ngOnInit() {
    this.load();
    this.api.getClauses().subscribe(c => (this.clauses = c));
  }

  load() {
    this.api
      .getContracts(this.search || undefined, this.selectedClauseId || undefined)
      .subscribe(c => (this.contracts = c));
  }

  openUpload() {
    this.dialog.open(UploadDialog, { width: '440px' }).afterClosed().subscribe(uploaded => {
      if (uploaded) this.load();
    });
  }

  openContract(id: string) {
    this.router.navigate(['/contracts', id]);
  }
}

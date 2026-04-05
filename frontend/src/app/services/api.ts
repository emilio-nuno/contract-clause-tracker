import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface ContractSummary {
  id: string;
  filename: string;
  uploaded_at: string;
}

export interface SentenceOut {
  id: string;
  text: string;
  position: number;
  label_name: string | null;
  label_color: string | null;
}

export interface ContractDetail {
  id: string;
  filename: string;
  uploaded_at: string;
  sentences: SentenceOut[];
}

export interface ClauseOut {
  id: string;
  name: string;
  description: string | null;
  color: string | null;
}

const BASE = 'http://localhost:8000';

@Injectable({ providedIn: 'root' })
export class ApiService {
  private http = inject(HttpClient);

  getContracts(search?: string, clauseId?: string): Observable<ContractSummary[]> {
    let params = new HttpParams();
    if (search) params = params.set('search', search);
    if (clauseId) params = params.set('clause_id', clauseId);
    return this.http.get<ContractSummary[]>(`${BASE}/contracts/`, { params });
  }

  getContract(id: string): Observable<ContractDetail> {
    return this.http.get<ContractDetail>(`${BASE}/contracts/${id}`);
  }

  uploadContract(file: File): Observable<ContractDetail> {
    const form = new FormData();
    form.append('file', file);
    return this.http.post<ContractDetail>(`${BASE}/contracts/`, form);
  }

  getClauses(): Observable<ClauseOut[]> {
    return this.http.get<ClauseOut[]>(`${BASE}/clauses/`);
  }

  updateSentenceLabel(sentenceId: string, clauseId: string | null): Observable<SentenceOut> {
    return this.http.patch<SentenceOut>(`${BASE}/sentences/${sentenceId}`, { clause_id: clauseId });
  }
}

import { Routes } from '@angular/router';
import { Dashboard } from './pages/dashboard/dashboard';
import { ContractDetail } from './pages/contract-detail/contract-detail';

export const routes: Routes = [
  { path: '', component: Dashboard },
  { path: 'contracts/:id', component: ContractDetail },
  { path: '**', redirectTo: '' },
];

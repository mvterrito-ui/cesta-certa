import { Routes } from '@angular/router';

import { somenteVisitante } from './core/guards';
import { Login } from './pages/login/login';

export const routes: Routes = [
  {
    path: 'login',
    component: Login,
    canActivate: [somenteVisitante],
    title: 'Entrar – Cesta Certa',
  },
  { path: '**', redirectTo: 'login' },
];

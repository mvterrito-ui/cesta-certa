import { Routes } from '@angular/router';

import { exigeLogin, somenteVisitante } from './core/guards';
import { Busca } from './pages/busca/busca';
import { Familia } from './pages/familia/familia';
import { Login } from './pages/login/login';
import { Resultado } from './pages/resultado/resultado';

export const routes: Routes = [
  {
    path: 'login',
    component: Login,
    canActivate: [somenteVisitante],
    title: 'Entrar – Cesta Certa',
  },
  {
    path: '',
    canActivate: [exigeLogin],
    children: [
      { path: 'busca', component: Busca, title: 'Buscar família – Cesta Certa' },
      { path: 'familias/:id', component: Familia, title: 'Família – Cesta Certa' },
      { path: 'resultado', component: Resultado, title: 'Resultado – Cesta Certa' },
      { path: '', pathMatch: 'full', redirectTo: 'busca' },
    ],
  },
  { path: '**', redirectTo: 'busca' },
];

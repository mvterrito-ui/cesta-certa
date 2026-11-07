import { Routes } from '@angular/router';

import { exigeLogin, somenteCoordenacao, somenteVisitante } from './core/guards';
import { Busca } from './pages/busca/busca';
import { Cadastro } from './pages/cadastro/cadastro';
import { Familia } from './pages/familia/familia';
import { Login } from './pages/login/login';
import { Relatorio } from './pages/relatorio/relatorio';
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
      { path: 'familias/nova', component: Cadastro, title: 'Nova família – Cesta Certa' },
      { path: 'familias/:id', component: Familia, title: 'Família – Cesta Certa' },
      { path: 'resultado', component: Resultado, title: 'Resultado – Cesta Certa' },
      {
        path: 'relatorio',
        component: Relatorio,
        canActivate: [somenteCoordenacao],
        title: 'Relatório mensal – Cesta Certa',
      },
      { path: '', pathMatch: 'full', redirectTo: 'busca' },
    ],
  },
  { path: '**', redirectTo: 'busca' },
];

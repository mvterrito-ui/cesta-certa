import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';

import { AuthService } from './auth.service';

export const exigeLogin: CanActivateFn = () => {
  const auth = inject(AuthService);
  return auth.autenticado() || inject(Router).createUrlTree(['/login']);
};

export const somenteVisitante: CanActivateFn = () => {
  const auth = inject(AuthService);
  return !auth.autenticado() || inject(Router).createUrlTree(['/busca']);
};

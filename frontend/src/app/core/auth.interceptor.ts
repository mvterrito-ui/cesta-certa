import { HttpErrorResponse, HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { catchError, throwError } from 'rxjs';

import { environment } from '../../environments/environment';
import { AuthService } from './auth.service';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const auth = inject(AuthService);
  const token = auth.token();
  // O token só é enviado para a nossa API, nunca para outros domínios.
  const paraApi = req.url.startsWith(environment.apiUrl);
  const requisicao =
    token && paraApi ? req.clone({ setHeaders: { Authorization: `Bearer ${token}` } }) : req;

  return next(requisicao).pipe(
    catchError((erro: unknown) => {
      const ehLogin = req.url.endsWith('/auth/login');
      if (erro instanceof HttpErrorResponse && erro.status === 401 && paraApi && !ehLogin) {
        auth.encerrarSessaoLocal();
      }
      return throwError(() => erro);
    }),
  );
};

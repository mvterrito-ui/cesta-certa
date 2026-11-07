import { HttpClient, provideHttpClient, withInterceptors } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';

import { environment } from '../../environments/environment';
import { authInterceptor } from './auth.interceptor';
import { AuthService } from './auth.service';

describe('authInterceptor', () => {
  let http: HttpClient;
  let backend: HttpTestingController;
  let auth: AuthService;

  beforeEach(() => {
    sessionStorage.clear();
    TestBed.configureTestingModule({
      providers: [
        provideRouter([{ path: 'login', children: [] }]),
        provideHttpClient(withInterceptors([authInterceptor])),
        provideHttpClientTesting(),
      ],
    });
    http = TestBed.inject(HttpClient);
    backend = TestBed.inject(HttpTestingController);
    auth = TestBed.inject(AuthService);
  });

  afterEach(() => backend.verify());

  function entrarComToken(token: string) {
    auth.entrar('juliana@teste.org.br', 'senha').subscribe();
    backend.expectOne(`${environment.apiUrl}/auth/login`).flush({
      access_token: token,
      token_type: 'bearer',
      usuario: { id: 1, nome: 'Juliana', email: 'juliana@teste.org.br', perfil: 'voluntario' },
    });
  }

  it('envia o token para a API', () => {
    entrarComToken('abc');
    http.get(`${environment.apiUrl}/familias`).subscribe();
    const req = backend.expectOne(`${environment.apiUrl}/familias`);
    expect(req.request.headers.get('Authorization')).toBe('Bearer abc');
    req.flush([]);
  });

  it('não envia o token para outros domínios', () => {
    entrarComToken('abc');
    http.get('https://outro-site.com/dados').subscribe();
    const req = backend.expectOne('https://outro-site.com/dados');
    expect(req.request.headers.has('Authorization')).toBe(false);
    req.flush({});
  });

  it('encerra a sessão quando a API responde 401', () => {
    entrarComToken('expirado');
    expect(auth.autenticado()).toBe(true);
    http.get(`${environment.apiUrl}/familias`).subscribe({ error: () => {} });
    backend
      .expectOne(`${environment.apiUrl}/familias`)
      .flush({}, { status: 401, statusText: 'Unauthorized' });
    expect(auth.autenticado()).toBe(false);
  });
});

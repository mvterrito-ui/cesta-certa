import { HttpClient } from '@angular/common/http';
import { Injectable, computed, inject, signal } from '@angular/core';
import { Router } from '@angular/router';
import { Observable, tap } from 'rxjs';

import { environment } from '../../environments/environment';
import { RespostaLogin, Usuario } from './modelos';

const CHAVE_SESSAO = 'cesta-certa.sessao';

interface Sessao {
  token: string;
  usuario: Usuario;
}

function lerSessao(): Sessao | null {
  try {
    const bruto = sessionStorage.getItem(CHAVE_SESSAO);
    return bruto ? (JSON.parse(bruto) as Sessao) : null;
  } catch {
    return null;
  }
}

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly http = inject(HttpClient);
  private readonly router = inject(Router);
  // sessionStorage: a sessão termina quando o navegador é fechado (RNF01).
  private readonly sessao = signal<Sessao | null>(lerSessao());

  readonly usuario = computed(() => this.sessao()?.usuario ?? null);
  readonly autenticado = computed(() => this.sessao() !== null);
  readonly ehAdministrador = computed(() => this.usuario()?.perfil === 'administrador');

  token(): string | null {
    return this.sessao()?.token ?? null;
  }

  entrar(email: string, senha: string): Observable<RespostaLogin> {
    return this.http
      .post<RespostaLogin>(`${environment.apiUrl}/auth/login`, { email, senha })
      .pipe(
        tap((resposta) => this.salvar({ token: resposta.access_token, usuario: resposta.usuario })),
      );
  }

  sair(): void {
    if (this.token()) {
      // Invalida o token no servidor; a tela não espera a resposta.
      this.http.post(`${environment.apiUrl}/auth/logout`, {}).subscribe({ error: () => {} });
    }
    this.encerrarSessaoLocal();
  }

  encerrarSessaoLocal(): void {
    this.salvar(null);
    this.router.navigate(['/login']);
  }

  private salvar(sessao: Sessao | null): void {
    this.sessao.set(sessao);
    try {
      if (sessao) {
        sessionStorage.setItem(CHAVE_SESSAO, JSON.stringify(sessao));
      } else {
        sessionStorage.removeItem(CHAVE_SESSAO);
      }
    } catch {
      // Navegador sem armazenamento: a sessão vale só enquanto a aba estiver aberta.
    }
  }
}

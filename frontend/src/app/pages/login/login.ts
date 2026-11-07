import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';
import { NonNullableFormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router } from '@angular/router';

import { mensagemDeErro } from '../../core/api.service';
import { AuthService } from '../../core/auth.service';
import { Icone } from '../../shared/icone';

@Component({
  selector: 'app-login',
  imports: [ReactiveFormsModule, Icone],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="tela">
      <header class="barra">
        <div class="marca"><app-icone nome="cesta" [tamanho]="22" /> Cesta Certa</div>
      </header>
      <main class="conteudo">
        <h1>Entrar</h1>
        <form [formGroup]="form" (ngSubmit)="entrar()" novalidate>
          <label class="rotulo" for="email">E-mail</label>
          <div class="campo">
            <input id="email" type="email" formControlName="email" autocomplete="username" />
          </div>

          <label class="rotulo espaco" for="senha">Senha</label>
          <div class="campo">
            <input
              id="senha"
              type="password"
              formControlName="senha"
              autocomplete="current-password"
            />
          </div>

          @if (erro(); as mensagem) {
            <p class="mensagem-erro" role="alert">{{ mensagem }}</p>
          }

          <button type="submit" class="btn btn-principal espaco" [disabled]="enviando()">
            {{ enviando() ? 'Entrando...' : 'Entrar' }}
          </button>
        </form>
      </main>
    </div>
  `,
})
export class Login {
  private readonly auth = inject(AuthService);
  private readonly router = inject(Router);

  protected readonly form = inject(NonNullableFormBuilder).group({
    email: ['', [Validators.required, Validators.email]],
    senha: ['', Validators.required],
  });
  protected readonly enviando = signal(false);
  protected readonly erro = signal('');

  entrar(): void {
    if (this.form.invalid) {
      this.erro.set('Preencha o e-mail e a senha.');
      return;
    }
    const { email, senha } = this.form.getRawValue();
    this.enviando.set(true);
    this.erro.set('');
    this.auth.entrar(email.trim(), senha).subscribe({
      next: () => this.router.navigate(['/busca']),
      error: (e) => {
        this.erro.set(mensagemDeErro(e));
        this.enviando.set(false);
      },
    });
  }
}

import { HttpErrorResponse } from '@angular/common/http';
import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';
import {
  AbstractControl,
  NonNullableFormBuilder,
  ReactiveFormsModule,
  ValidationErrors,
  Validators,
} from '@angular/forms';
import { Router, RouterLink } from '@angular/router';

import { ApiService, mensagemDeErro } from '../../core/api.service';
import { cpfValido, formatarCpfDigitado, somenteDigitos } from '../../core/formatos';
import { Icone } from '../../shared/icone';

function validadorCpf(controle: AbstractControl): ValidationErrors | null {
  return !controle.value || cpfValido(controle.value) ? null : { cpf: true };
}

type Campo = 'nome_responsavel' | 'documento_responsavel' | 'endereco' | 'numero_integrantes';

const MENSAGENS: Record<Campo, string> = {
  nome_responsavel: 'Informe o nome completo do responsável.',
  documento_responsavel: 'CPF inválido. Confira os 11 números.',
  endereco: 'Informe o endereço.',
  numero_integrantes: 'Informe quantas pessoas moram na casa (1 a 30).',
};

/** Cadastro de família (RF01). Coleta apenas o necessário (LGPD). */
@Component({
  selector: 'app-cadastro',
  imports: [ReactiveFormsModule, RouterLink, Icone],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="tela">
      <header class="barra">
        <a class="btn-barra btn-voltar" routerLink="/busca"><app-icone nome="voltar" /> Voltar</a>
        <span class="esp"></span>
        <div class="marca">Nova família</div>
        <span class="esp"></span><span class="espaco-voltar"></span>
      </header>
      <main class="conteudo">
        <form id="form-cadastro" [formGroup]="form" (ngSubmit)="salvar()" novalidate>
          <label class="rotulo" for="nome">Nome do responsável</label>
          <div class="campo" [class.invalido]="mostrarErro('nome_responsavel')">
            <input
              id="nome"
              formControlName="nome_responsavel"
              autocomplete="off"
              [attr.aria-invalid]="mostrarErro('nome_responsavel')"
              aria-describedby="erro-nome"
            />
          </div>
          @if (mostrarErro('nome_responsavel')) {
            <p class="erro-campo" id="erro-nome">{{ mensagem('nome_responsavel') }}</p>
          }

          <label class="rotulo espaco" for="cpf">CPF do responsável</label>
          <div class="campo" [class.invalido]="mostrarErro('documento_responsavel')">
            <input
              id="cpf"
              formControlName="documento_responsavel"
              inputmode="numeric"
              autocomplete="off"
              placeholder="000.000.000-00"
              (input)="formatarCpf()"
              [attr.aria-invalid]="mostrarErro('documento_responsavel')"
              aria-describedby="erro-cpf ajuda-cpf"
            />
          </div>
          <div class="ajuda" id="ajuda-cpf">Usado só para evitar cadastro repetido.</div>
          @if (mostrarErro('documento_responsavel')) {
            <p class="erro-campo" id="erro-cpf">{{ mensagem('documento_responsavel') }}</p>
          }

          <label class="rotulo espaco" for="pessoas">Pessoas na família</label>
          <div class="campo campo-curto" [class.invalido]="mostrarErro('numero_integrantes')">
            <input
              id="pessoas"
              type="number"
              inputmode="numeric"
              min="1"
              max="30"
              formControlName="numero_integrantes"
              [attr.aria-invalid]="mostrarErro('numero_integrantes')"
              aria-describedby="erro-pessoas"
            />
          </div>
          @if (mostrarErro('numero_integrantes')) {
            <p class="erro-campo" id="erro-pessoas">{{ mensagem('numero_integrantes') }}</p>
          }

          <label class="rotulo espaco" for="endereco">Endereço</label>
          <div class="campo" [class.invalido]="mostrarErro('endereco')">
            <input
              id="endereco"
              formControlName="endereco"
              autocomplete="off"
              [attr.aria-invalid]="mostrarErro('endereco')"
              aria-describedby="erro-endereco"
            />
          </div>
          @if (mostrarErro('endereco')) {
            <p class="erro-campo" id="erro-endereco">{{ mensagem('endereco') }}</p>
          }

          <label class="rotulo espaco" for="telefone">Telefone (opcional)</label>
          <div class="campo">
            <input
              id="telefone"
              type="tel"
              inputmode="tel"
              formControlName="telefone"
              autocomplete="off"
            />
          </div>

          @if (erroGeral(); as erro) {
            <p class="mensagem-erro" role="alert">{{ erro }}</p>
          }
        </form>
      </main>
      <div class="rodape">
        <button
          type="submit"
          form="form-cadastro"
          class="btn btn-principal"
          [disabled]="salvando()"
        >
          {{ salvando() ? 'Salvando...' : 'Salvar família' }}
        </button>
      </div>
    </div>
  `,
})
export class Cadastro {
  private readonly api = inject(ApiService);
  private readonly router = inject(Router);

  protected readonly form = inject(NonNullableFormBuilder).group({
    nome_responsavel: [
      '',
      [Validators.required, Validators.minLength(3), Validators.maxLength(120)],
    ],
    documento_responsavel: ['', [Validators.required, validadorCpf]],
    numero_integrantes: [1, [Validators.required, Validators.min(1), Validators.max(30)]],
    endereco: ['', [Validators.required, Validators.minLength(3), Validators.maxLength(200)]],
    telefone: ['', Validators.maxLength(15)],
  });
  protected readonly salvando = signal(false);
  protected readonly erroGeral = signal('');
  private readonly errosServidor = signal<Partial<Record<Campo, string>>>({});
  private readonly tentouEnviar = signal(false);

  protected mostrarErro(campo: Campo): boolean {
    const controle = this.form.controls[campo];
    return (
      Boolean(this.errosServidor()[campo]) ||
      (controle.invalid && (controle.touched || this.tentouEnviar()))
    );
  }

  protected mensagem(campo: Campo): string {
    return this.errosServidor()[campo] ?? MENSAGENS[campo];
  }

  protected formatarCpf(): void {
    const controle = this.form.controls.documento_responsavel;
    controle.setValue(formatarCpfDigitado(controle.value), { emitEvent: false });
  }

  salvar(): void {
    this.tentouEnviar.set(true);
    this.errosServidor.set({});
    this.erroGeral.set('');
    if (this.form.invalid) {
      this.erroGeral.set('Confira os campos destacados.');
      return;
    }
    const dados = this.form.getRawValue();
    this.salvando.set(true);
    this.api
      .cadastrarFamilia({
        ...dados,
        documento_responsavel: somenteDigitos(dados.documento_responsavel),
        telefone: dados.telefone.trim() || null,
      })
      .subscribe({
        next: (familia) => this.router.navigate(['/familias', familia.id], { replaceUrl: true }),
        error: (e: unknown) => {
          this.salvando.set(false);
          if (e instanceof HttpErrorResponse && e.status === 422 && Array.isArray(e.error?.erros)) {
            const porCampo: Partial<Record<Campo, string>> = {};
            for (const item of e.error.erros as { campo: Campo; mensagem: string }[]) {
              porCampo[item.campo] = item.mensagem;
            }
            this.errosServidor.set(porCampo);
          }
          this.erroGeral.set(mensagemDeErro(e));
        },
      });
  }
}

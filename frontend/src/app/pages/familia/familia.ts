import { HttpErrorResponse } from '@angular/common/http';
import {
  ChangeDetectionStrategy,
  Component,
  OnInit,
  inject,
  input,
  numberAttribute,
  signal,
} from '@angular/core';
import { Router, RouterLink } from '@angular/router';

import { ApiService, mensagemDeErro } from '../../core/api.service';
import { diaMesLocal } from '../../core/formatos';
import { BloqueioEntrega, FamiliaDetalhe, ResultadoEntrega } from '../../core/modelos';
import { Icone } from '../../shared/icone';

/** Tela 2 – Família e registro de entrega (RF02). */
@Component({
  selector: 'app-familia',
  imports: [RouterLink, Icone],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="tela">
      <header class="barra">
        <a class="btn-barra btn-voltar" routerLink="/busca"><app-icone nome="voltar" /> Voltar</a>
        <span class="esp"></span>
        <div class="marca">Família</div>
        <span class="esp"></span><span class="espaco-voltar"></span>
      </header>
      <main class="conteudo">
        @if (familia(); as f) {
          <section class="ficha" aria-label="Dados da família">
            <h1 class="nome">{{ f.nome_responsavel }}</h1>
            <div class="dado">
              <app-icone nome="pessoas" [tamanho]="20" class="cinza" />
              {{ f.numero_integrantes }} pessoas na família
            </div>
            <div class="dado">
              <app-icone nome="documento" [tamanho]="20" class="cinza" /> CPF {{ f.cpf }}
            </div>
            <div class="dado">
              <app-icone nome="casa" [tamanho]="20" class="cinza" /> {{ f.endereco }}
            </div>
          </section>

          <h2>Últimas entregas</h2>
          <ul class="lista-entregas">
            @for (entrega of f.entregas; track entrega.id) {
              <li>
                <span>Cesta em {{ diaMesLocal(entrega.data_entrega) }}</span>
                <span class="quem">por {{ entrega.registrado_por }}</span>
              </li>
            } @empty {
              <li><span>Nenhuma entrega registrada</span></li>
            }
          </ul>
        } @else if (!erro()) {
          <p role="status">Carregando...</p>
        }

        @if (erro(); as mensagem) {
          <p class="mensagem-erro" role="alert">{{ mensagem }}</p>
        }
      </main>

      @if (familia()) {
        <div class="rodape">
          <p class="aviso-conferir">Confira o nome antes de registrar.</p>
          <button
            type="button"
            class="btn btn-principal"
            [disabled]="registrando()"
            (click)="registrar()"
          >
            @if (registrando()) {
              Registrando...
            } @else {
              <app-icone nome="cesta" [tamanho]="22" /> Registrar entrega
            }
          </button>
        </div>
      }
    </div>
  `,
})
export class Familia implements OnInit {
  private readonly api = inject(ApiService);
  private readonly router = inject(Router);
  protected readonly diaMesLocal = diaMesLocal;

  /** Vem da rota /familias/:id (withComponentInputBinding). */
  readonly id = input.required({ transform: numberAttribute });

  protected readonly familia = signal<FamiliaDetalhe | null>(null);
  protected readonly registrando = signal(false);
  protected readonly erro = signal('');

  ngOnInit(): void {
    this.api.obterFamilia(this.id()).subscribe({
      next: (familia) => this.familia.set(familia),
      error: (e) => this.erro.set(mensagemDeErro(e)),
    });
  }

  registrar(): void {
    const familia = this.familia();
    // O botão fica desativado durante o envio para evitar toque duplo.
    if (!familia || this.registrando()) {
      return;
    }
    this.registrando.set(true);
    this.erro.set('');
    this.api.registrarEntrega(familia.id).subscribe({
      next: (entrega) =>
        this.irParaResultado({
          tipo: 'sucesso',
          nome: entrega.nome_responsavel,
          dataEntrega: entrega.data_entrega,
        }),
      error: (e: unknown) => {
        if (e instanceof HttpErrorResponse && e.status === 409 && e.error?.proxima_entrega) {
          const bloqueio = e.error as BloqueioEntrega;
          this.irParaResultado({
            tipo: 'aviso',
            nome: familia.nome_responsavel,
            ultimaEntrega: bloqueio.ultima_entrega,
            proximaEntrega: bloqueio.proxima_entrega,
          });
          return;
        }
        this.erro.set(mensagemDeErro(e));
        this.registrando.set(false);
      },
    });
  }

  private irParaResultado(resultado: ResultadoEntrega): void {
    this.router.navigate(['/resultado'], { state: { resultado }, replaceUrl: true });
  }
}

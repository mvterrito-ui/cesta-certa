import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { FormControl, ReactiveFormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { Subject, catchError, debounceTime, distinctUntilChanged, map, of, switchMap } from 'rxjs';

import { ApiService, mensagemDeErro } from '../../core/api.service';
import { AuthService } from '../../core/auth.service';
import { diaMes, somenteDigitos } from '../../core/formatos';
import { FamiliaResumo } from '../../core/modelos';
import { BarraTopo } from '../../shared/barra-topo';
import { Icone } from '../../shared/icone';

type EstadoBusca =
  | { tipo: 'inicial' }
  | { tipo: 'carregando' }
  | { tipo: 'resultado'; familias: FamiliaResumo[] }
  | { tipo: 'erro'; mensagem: string };

/** Tela 1 – Buscar família. */
@Component({
  selector: 'app-busca',
  imports: [ReactiveFormsModule, RouterLink, BarraTopo, Icone],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="tela">
      <app-barra-topo />
      <main class="conteudo">
        @if (auth.ehAdministrador()) {
          <a class="btn btn-secundario btn-atalho" routerLink="/relatorio">
            <app-icone nome="grafico" /> Relatório do mês
          </a>
        }
        <h1>Buscar família</h1>
        <label class="rotulo" for="busca">Nome ou CPF do responsável</label>
        <div class="campo">
          <app-icone nome="lupa" class="cinza" />
          <input
            id="busca"
            type="search"
            [formControl]="termo"
            autocomplete="off"
            enterkeyhint="search"
            aria-describedby="ajuda-busca"
          />
        </div>
        <div class="ajuda" id="ajuda-busca">Digite pelo menos 3 letras ou o CPF completo.</div>

        <div class="contagem" role="status" aria-live="polite">
          @switch (estado().tipo) {
            @case ('carregando') {
              Buscando...
            }
            @case ('resultado') {
              {{ textoContagem() }}
            }
          }
        </div>

        @switch (estado().tipo) {
          @case ('resultado') {
            @for (familia of familias(); track familia.id) {
              <a class="cartao" [routerLink]="['/familias', familia.id]">
                <span class="info">
                  <span class="nome">{{ familia.nome_responsavel }}</span
                  ><br />
                  <span class="linha"
                    >{{ familia.numero_integrantes }} pessoas · CPF {{ familia.cpf }}</span
                  ><br />
                  <span class="ultima">
                    {{
                      familia.ultima_entrega
                        ? 'Última cesta: ' + diaMes(familia.ultima_entrega)
                        : 'Nenhuma cesta registrada'
                    }}
                  </span>
                </span>
                <app-icone nome="seta" class="seta" />
              </a>
            } @empty {
              <p class="vazio">Nenhuma família encontrada. Confira o nome ou cadastre a família.</p>
            }
          }
          @case ('erro') {
            <p class="mensagem-erro" role="alert">{{ mensagemErro() }}</p>
          }
        }
      </main>
      <div class="rodape">
        <a class="btn btn-secundario" routerLink="/familias/nova">
          <app-icone nome="mais" [tamanho]="22" /> Cadastrar nova família
        </a>
      </div>
    </div>
  `,
})
export class Busca {
  private readonly api = inject(ApiService);
  protected readonly auth = inject(AuthService);
  protected readonly diaMes = diaMes;

  protected readonly termo = new FormControl(this.api.ultimaBusca(), { nonNullable: true });
  protected readonly estado = signal<EstadoBusca>({ tipo: 'inicial' });
  private readonly pesquisas = new Subject<string>();

  constructor() {
    this.pesquisas
      .pipe(
        distinctUntilChanged(),
        switchMap((termo) => {
          if (!this.termoValido(termo)) {
            return of<EstadoBusca>({ tipo: 'inicial' });
          }
          this.estado.set({ tipo: 'carregando' });
          return this.api.buscarFamilias(termo).pipe(
            map((familias): EstadoBusca => ({ tipo: 'resultado', familias })),
            catchError((e) => of<EstadoBusca>({ tipo: 'erro', mensagem: mensagemDeErro(e) })),
          );
        }),
        takeUntilDestroyed(),
      )
      .subscribe((estado) => this.estado.set(estado));

    this.termo.valueChanges
      .pipe(debounceTime(300), takeUntilDestroyed())
      .subscribe((termo) => this.pesquisar(termo));

    if (this.termo.value) {
      this.pesquisar(this.termo.value);
    }
  }

  pesquisar(valor: string): void {
    const termo = valor.trim();
    this.api.ultimaBusca.set(termo);
    this.pesquisas.next(termo);
  }

  protected familias(): FamiliaResumo[] {
    const estado = this.estado();
    return estado.tipo === 'resultado' ? estado.familias : [];
  }

  protected mensagemErro(): string {
    const estado = this.estado();
    return estado.tipo === 'erro' ? estado.mensagem : '';
  }

  protected textoContagem(): string {
    const total = this.familias().length;
    if (total === 0) {
      return '';
    }
    return total === 1 ? '1 família encontrada' : `${total} famílias encontradas`;
  }

  private termoValido(termo: string): boolean {
    const digitos = somenteDigitos(termo);
    if (/^[\d.\-\s]+$/.test(termo)) {
      return digitos.length === 11;
    }
    return termo.length >= 3;
  }
}

import { ChangeDetectionStrategy, Component, OnInit, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';

import { ApiService, mensagemDeErro } from '../../core/api.service';
import { RelatorioMensal } from '../../core/modelos';
import { Icone } from '../../shared/icone';

/** "2026-11" do mês atual no horário de Londrina. */
export function mesAtual(agora = new Date()): string {
  const partes = new Intl.DateTimeFormat('en-CA', {
    timeZone: 'America/Sao_Paulo',
    year: 'numeric',
    month: '2-digit',
  }).formatToParts(agora);
  const valor = (tipo: string) => partes.find((p) => p.type === tipo)?.value ?? '';
  return `${valor('year')}-${valor('month')}`;
}

/** Relatório mensal da coordenação (RF04). */
@Component({
  selector: 'app-relatorio',
  imports: [RouterLink, Icone],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="tela">
      <header class="barra">
        <a class="btn-barra btn-voltar" routerLink="/busca"><app-icone nome="voltar" /> Voltar</a>
        <span class="esp"></span>
        <div class="marca">Relatório</div>
        <span class="esp"></span><span class="espaco-voltar"></span>
      </header>
      <main class="conteudo">
        <h1>Relatório do mês</h1>
        <label class="rotulo" for="mes">Mês de referência</label>
        <div class="campo campo-medio">
          <input id="mes" type="month" [value]="mes()" (change)="trocarMes($event)" />
        </div>

        @if (relatorio(); as r) {
          <dl class="indicadores" aria-live="polite">
            <div class="indicador">
              <dt>Cestas entregues</dt>
              <dd>{{ r.total_entregas }}</dd>
            </div>
            <div class="indicador">
              <dt>Famílias atendidas</dt>
              <dd>{{ r.familias_atendidas }}</dd>
            </div>
            <div class="indicador">
              <dt>Pessoas atendidas</dt>
              <dd>{{ r.pessoas_atendidas }}</dd>
            </div>
            <div class="indicador">
              <dt>Famílias sem cesta no mês</dt>
              <dd>{{ r.familias_sem_entrega }}</dd>
            </div>
          </dl>
          <p class="ajuda">
            {{ r.familias_sem_entrega }} de {{ r.familias_ativas }} famílias ativas não retiraram
            cesta neste mês.
          </p>

          <h2>Entregas por voluntário</h2>
          @if (r.por_voluntario.length) {
            <table class="tabela">
              <caption class="visualmente-oculto">
                Entregas registradas por voluntário
              </caption>
              <thead>
                <tr>
                  <th scope="col">Voluntário</th>
                  <th scope="col" class="numero">Entregas</th>
                </tr>
              </thead>
              <tbody>
                @for (linha of r.por_voluntario; track linha.nome) {
                  <tr>
                    <td>{{ linha.nome }}</td>
                    <td class="numero">{{ linha.entregas }}</td>
                  </tr>
                }
              </tbody>
            </table>
          } @else {
            <p class="vazio">Nenhuma entrega registrada neste mês.</p>
          }
        } @else if (!erro()) {
          <p role="status">Carregando...</p>
        }

        @if (erro(); as mensagem) {
          <p class="mensagem-erro" role="alert">{{ mensagem }}</p>
        }
      </main>
      @if (relatorio()) {
        <div class="rodape">
          <button type="button" class="btn btn-secundario" (click)="imprimir()">
            Imprimir relatório
          </button>
        </div>
      }
    </div>
  `,
})
export class Relatorio implements OnInit {
  private readonly api = inject(ApiService);

  protected readonly mes = signal(mesAtual());
  protected readonly relatorio = signal<RelatorioMensal | null>(null);
  protected readonly erro = signal('');

  ngOnInit(): void {
    this.carregar();
  }

  protected trocarMes(evento: Event): void {
    const valor = (evento.target as HTMLInputElement).value;
    if (/^\d{4}-\d{2}$/.test(valor)) {
      this.mes.set(valor);
      this.carregar();
    }
  }

  protected imprimir(): void {
    window.print();
  }

  private carregar(): void {
    const [ano, mes] = this.mes().split('-').map(Number);
    this.relatorio.set(null);
    this.erro.set('');
    this.api.relatorioMensal(ano, mes).subscribe({
      next: (relatorio) => this.relatorio.set(relatorio),
      error: (e) => this.erro.set(mensagemDeErro(e)),
    });
  }
}

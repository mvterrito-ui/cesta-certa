import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { Router, RouterLink } from '@angular/router';

import { ApiService } from '../../core/api.service';
import { dataHora, diaMes } from '../../core/formatos';
import { ResultadoEntrega } from '../../core/modelos';
import { Icone } from '../../shared/icone';

/** Tela 3 – Resultado: sucesso ou aviso de duplicidade (RF03). */
@Component({
  selector: 'app-resultado',
  imports: [RouterLink, Icone],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="tela">
      <header class="barra">
        <div class="marca"><app-icone nome="cesta" [tamanho]="22" /> Cesta Certa</div>
      </header>
      @if (resultado; as r) {
        <main class="conteudo">
          <h1 class="titulo-resultado">Resultado da entrega</h1>
          <p class="subtitulo">{{ r.nome }}</p>

          <!-- Ícone + título + texto + cor: o aviso não depende só da cor (RNF04). -->
          @if (r.tipo === 'sucesso') {
            <div class="resultado ok" role="alert">
              <app-icone nome="sucesso" [tamanho]="64" />
              <div class="titulo">Entrega registrada</div>
              <div class="texto">
                <strong>{{ r.nome }}</strong> recebeu a cesta em {{ dataHora(r.dataEntrega) }}.
              </div>
            </div>
          } @else {
            <div class="resultado alerta" role="alert">
              <app-icone nome="alerta" [tamanho]="64" />
              <div class="titulo">Já recebeu cesta</div>
              <div class="texto">
                Esta família recebeu cesta em <strong>{{ diaMes(r.ultimaEntrega) }}</strong
                >.<br />
                @if (r.entreguePor) {
                  Entregue por <strong>{{ r.entreguePor }}</strong
                  >.<br />
                }
                Próxima entrega a partir de <strong>{{ diaMes(r.proximaEntrega) }}</strong
                >.
              </div>
              <div class="extra">Nenhuma entrega foi registrada.</div>
            </div>
          }
        </main>
        <div class="rodape">
          @if (r.tipo === 'sucesso') {
            <a class="btn btn-principal" routerLink="/busca" (click)="novaBusca()"
              >Atender próxima família</a
            >
          } @else {
            <a class="btn btn-principal" routerLink="/busca" (click)="novaBusca()"
              ><app-icone nome="voltar" /> Voltar à busca</a
            >
          }
        </div>
      }
    </div>
  `,
})
export class Resultado {
  private readonly api = inject(ApiService);
  protected readonly dataHora = dataHora;
  protected readonly diaMes = diaMes;

  protected readonly resultado: ResultadoEntrega | null =
    (history.state?.resultado as ResultadoEntrega | undefined) ?? null;

  constructor() {
    // Sem resultado (ex.: página recarregada), volta para a busca.
    if (!this.resultado) {
      inject(Router).navigate(['/busca'], { replaceUrl: true });
    }
  }

  novaBusca(): void {
    this.api.ultimaBusca.set('');
  }
}

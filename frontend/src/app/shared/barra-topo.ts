import { ChangeDetectionStrategy, Component, computed, inject } from '@angular/core';

import { AuthService } from '../core/auth.service';
import { Icone } from './icone';

/** Barra verde da Tela 1 com o usuário logado e o botão Sair. */
@Component({
  selector: 'app-barra-topo',
  imports: [Icone],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <header class="barra">
      <div>
        <div class="marca"><app-icone nome="cesta" [tamanho]="22" /> Cesta Certa</div>
        @if (saudacao(); as texto) {
          <div class="usuario">{{ texto }}</div>
        }
      </div>
      <span class="esp"></span>
      <button type="button" class="btn-barra" (click)="auth.sair()">
        <app-icone nome="sair" [tamanho]="20" /> Sair
      </button>
    </header>
  `,
})
export class BarraTopo {
  protected readonly auth = inject(AuthService);

  protected readonly saudacao = computed(() => {
    const usuario = this.auth.usuario();
    if (!usuario) {
      return '';
    }
    const papel = usuario.perfil === 'administrador' ? 'coordenação' : 'equipe voluntária';
    return `Olá, ${usuario.nome} (${papel})`;
  });
}

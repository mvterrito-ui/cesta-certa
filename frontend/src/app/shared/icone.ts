import { ChangeDetectionStrategy, Component, input } from '@angular/core';

export type NomeIcone =
  | 'cesta'
  | 'lupa'
  | 'sair'
  | 'voltar'
  | 'seta'
  | 'casa'
  | 'pessoas'
  | 'documento'
  | 'mais'
  | 'sucesso'
  | 'alerta'
  | 'grafico';

/** Ícones em SVG no próprio template, sem innerHTML (RNF02) e sempre ao lado de um texto (RNF04). */
@Component({
  selector: 'app-icone',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <svg
      [attr.width]="tamanho()"
      [attr.height]="tamanho()"
      viewBox="0 0 24 24"
      aria-hidden="true"
      focusable="false"
    >
      @switch (nome()) {
        @case ('cesta') {
          <path
            fill="currentColor"
            d="M5.5 9 9.6 3.4l1.6 1.2L7.9 9h8.2l-3.3-4.4 1.6-1.2L18.5 9H22v2h-1.2l-1.6 9.1A2 2 0 0 1 17.2 22H6.8a2 2 0 0 1-2-1.9L3.2 11H2V9h3.5Zm-.3 2 1.6 9h10.4l1.6-9H5.2ZM9 13h2v5H9v-5Zm4 0h2v5h-2v-5Z"
          />
        }
        @case ('lupa') {
          <path
            fill="currentColor"
            d="M10 2a8 8 0 0 1 6.3 12.9l5.4 5.4-1.4 1.4-5.4-5.4A8 8 0 1 1 10 2Zm0 2a6 6 0 1 0 0 12 6 6 0 0 0 0-12Z"
          />
        }
        @case ('sair') {
          <path
            fill="currentColor"
            d="M5 3h8v2H5v14h8v2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2Zm11.6 4.6L21 12l-4.4 4.4-1.4-1.4 2-2H9v-2h8.2l-2-2 1.4-1.4Z"
          />
        }
        @case ('voltar') {
          <path
            fill="currentColor"
            d="M20 11v2H8l5.5 5.5-1.4 1.4L4.2 12l7.9-7.9 1.4 1.4L8 11h12Z"
          />
        }
        @case ('seta') {
          <path fill="currentColor" d="m9.4 18.6-1.4-1.4 5.2-5.2-5.2-5.2L9.4 5.4 16 12l-6.6 6.6Z" />
        }
        @case ('casa') {
          <path
            fill="currentColor"
            d="M12 3 2 11.5l1.3 1.5L5 11.6V21h14v-9.4l1.7 1.4 1.3-1.5L12 3Zm5 16h-3v-5h-4v5H7v-9.1l5-4.3 5 4.3V19Z"
          />
        }
        @case ('pessoas') {
          <path
            fill="currentColor"
            d="M9 12a4 4 0 1 1 0-8 4 4 0 0 1 0 8Zm0-2a2 2 0 1 0 0-4 2 2 0 0 0 0 4Zm7.5 2a3 3 0 1 1 0-6 3 3 0 0 1 0 6ZM2 20c0-3.3 3.1-6 7-6s7 2.7 7 6h-2c0-2.1-2.2-4-5-4s-5 1.9-5 4H2Zm15.5-6c2.8 0 4.5 1.9 4.5 5h-2c0-2-1-3-2.5-3H16v-2h1.5Z"
          />
        }
        @case ('documento') {
          <path fill="currentColor" d="M3 5h18v14H3V5Zm2 2v10h14V7H5Zm2 2h4v2H7V9Zm0 4h7v2H7v-2Z" />
        }
        @case ('mais') {
          <path fill="currentColor" d="M11 5h2v6h6v2h-6v6h-2v-6H5v-2h6V5Z" />
        }
        @case ('sucesso') {
          <circle cx="12" cy="12" r="11" fill="#1b5e20" />
          <path fill="#fff" d="m10 15.6-3.6-3.6L5 13.4l5 5 9-9-1.4-1.4L10 15.6Z" />
        }
        @case ('grafico') {
          <path
            fill="currentColor"
            d="M3 3h2v16h16v2H3V3Zm4 9h3v5H7v-5Zm5-5h3v10h-3V7Zm5 3h3v7h-3v-7Z"
          />
        }
        @case ('alerta') {
          <path fill="#8a6200" d="M12 1.5 23.5 21.5H.5L12 1.5Z" />
          <path fill="#fff" d="M11 9h2v6h-2V9Zm0 8h2v2h-2v-2Z" />
        }
      }
    </svg>
  `,
  host: { class: 'icone' },
})
export class Icone {
  readonly nome = input.required<NomeIcone>();
  readonly tamanho = input(24);
}

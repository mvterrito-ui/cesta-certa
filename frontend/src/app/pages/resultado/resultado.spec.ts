import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';

import { ResultadoEntrega } from '../../core/modelos';
import { Resultado } from './resultado';

function renderizar(resultado: ResultadoEntrega): HTMLElement {
  history.replaceState({ resultado }, '');
  TestBed.configureTestingModule({ imports: [Resultado], providers: [provideRouter([])] });
  const fixture = TestBed.createComponent(Resultado);
  fixture.detectChanges();
  return fixture.nativeElement as HTMLElement;
}

describe('Resultado (Tela 3)', () => {
  it('mostra a confirmação de entrega registrada', () => {
    const tela = renderizar({
      tipo: 'sucesso',
      nome: 'Antônio Carlos Silva',
      dataEntrega: '2026-10-24T12:42:00Z',
    });
    const alerta = tela.querySelector('[role="alert"]');
    expect(alerta?.classList).toContain('ok');
    expect(alerta?.textContent).toContain('Entrega registrada');
    expect(alerta?.textContent).toContain('Antônio Carlos Silva recebeu a cesta em 24/10 às 9h42');
    expect(tela.textContent).toContain('Atender próxima família');
  });

  it('mostra o aviso de duplicidade com texto e ícone, não só cor (RNF04)', () => {
    const tela = renderizar({
      tipo: 'aviso',
      nome: 'Maria José da Silva',
      ultimaEntrega: '2026-10-12',
      proximaEntrega: '2026-10-27',
    });
    const alerta = tela.querySelector('[role="alert"]');
    expect(alerta?.classList).toContain('alerta');
    expect(alerta?.textContent).toContain('Já recebeu cesta');
    expect(alerta?.textContent?.replace(/\s+/g, ' ')).toContain(
      'Esta família recebeu cesta em 12/10. Próxima entrega a partir de 27/10.',
    );
    expect(alerta?.textContent).toContain('Nenhuma entrega foi registrada.');
    expect(alerta?.querySelector('svg')).not.toBeNull();
    expect(tela.textContent).toContain('Voltar à busca');
  });
});

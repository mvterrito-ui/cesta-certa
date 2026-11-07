import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';

import { environment } from '../../../environments/environment';
import { FamiliaResumo } from '../../core/modelos';
import { Busca } from './busca';

const FAMILIAS: FamiliaResumo[] = [
  {
    id: 1,
    nome_responsavel: 'Antônio Carlos Silva',
    numero_integrantes: 2,
    cpf: '***.321.654-**',
    ultima_entrega: '2026-10-04',
    apta: true,
    proxima_entrega: '2026-10-19',
  },
  {
    id: 3,
    nome_responsavel: 'Rosana Silva Lima',
    numero_integrantes: 5,
    cpf: '***.987.123-**',
    ultima_entrega: null,
    apta: true,
    proxima_entrega: null,
  },
];

describe('Busca (Tela 1)', () => {
  let fixture: ComponentFixture<Busca>;
  let backend: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [Busca],
      providers: [provideRouter([]), provideHttpClient(), provideHttpClientTesting()],
    });
    backend = TestBed.inject(HttpTestingController);
    fixture = TestBed.createComponent(Busca);
    fixture.detectChanges();
  });

  afterEach(() => backend.verify());

  const tela = () => fixture.nativeElement as HTMLElement;

  it('tem rótulo visível ligado ao campo de busca (RNF04)', () => {
    const rotulo = tela().querySelector('label[for="busca"]');
    expect(rotulo?.textContent).toContain('Nome ou CPF do responsável');
    expect(tela().querySelector('#busca')?.getAttribute('aria-describedby')).toBe('ajuda-busca');
  });

  it('não consulta a API com menos de 3 letras', () => {
    fixture.componentInstance.pesquisar('si');
    backend.expectNone(() => true);
  });

  it('lista as famílias com CPF mascarado e a última cesta', () => {
    fixture.componentInstance.pesquisar('silva');
    const req = backend.expectOne((r) => r.url === `${environment.apiUrl}/familias`);
    expect(req.request.params.get('busca')).toBe('silva');
    req.flush(FAMILIAS);
    fixture.detectChanges();

    const cartoes = tela().querySelectorAll('a.cartao');
    expect(cartoes.length).toBe(2);
    expect(cartoes[0].textContent).toContain('***.321.654-**');
    expect(cartoes[0].textContent).toContain('Última cesta: 04/10');
    expect(cartoes[1].textContent).toContain('Nenhuma cesta registrada');
    expect(tela().querySelector('[role="status"]')?.textContent).toContain(
      '2 famílias encontradas',
    );
  });

  it('orienta quando nenhuma família é encontrada', () => {
    fixture.componentInstance.pesquisar('Joaquim');
    backend.expectOne((r) => r.url === `${environment.apiUrl}/familias`).flush([]);
    fixture.detectChanges();
    expect(tela().textContent).toContain(
      'Nenhuma família encontrada. Confira o nome ou cadastre a família.',
    );
  });

  it('avisa quando não há conexão', () => {
    fixture.componentInstance.pesquisar('silva');
    backend
      .expectOne((r) => r.url === `${environment.apiUrl}/familias`)
      .error(new ProgressEvent('error'), { status: 0 });
    fixture.detectChanges();
    expect(tela().querySelector('[role="alert"]')?.textContent).toContain(
      'Sem conexão com o servidor',
    );
  });
});

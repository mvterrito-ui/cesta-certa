import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';

import { environment } from '../../../environments/environment';
import { RelatorioMensal } from '../../core/modelos';
import { Relatorio, mesAtual } from './relatorio';

const OUTUBRO: RelatorioMensal = {
  ano: 2026,
  mes: 10,
  total_entregas: 3,
  familias_atendidas: 2,
  pessoas_atendidas: 6,
  familias_ativas: 3,
  familias_sem_entrega: 1,
  por_voluntario: [
    { nome: 'Juliana', entregas: 2 },
    { nome: 'Paulo', entregas: 1 },
  ],
};

describe('Relatorio (RF04)', () => {
  let fixture: ComponentFixture<Relatorio>;
  let backend: HttpTestingController;
  const url = `${environment.apiUrl}/relatorios/mensal`;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [Relatorio],
      providers: [provideRouter([]), provideHttpClient(), provideHttpClientTesting()],
    });
    backend = TestBed.inject(HttpTestingController);
    fixture = TestBed.createComponent(Relatorio);
    fixture.detectChanges();
  });

  afterEach(() => backend.verify());

  const tela = () => fixture.nativeElement as HTMLElement;

  it('carrega o mês atual e mostra os indicadores', () => {
    const [ano, mes] = mesAtual().split('-').map(Number);
    const req = backend.expectOne((r) => r.url === url);
    expect(req.request.params.get('ano')).toBe(String(ano));
    expect(req.request.params.get('mes')).toBe(String(mes));
    req.flush(OUTUBRO);
    fixture.detectChanges();

    const indicadores = Array.from(tela().querySelectorAll('.indicador')).map((e) => [
      e.querySelector('dt')?.textContent?.trim(),
      e.querySelector('dd')?.textContent?.trim(),
    ]);
    expect(indicadores).toEqual([
      ['Cestas entregues', '3'],
      ['Famílias atendidas', '2'],
      ['Pessoas atendidas', '6'],
      ['Famílias sem cesta no mês', '1'],
    ]);
    expect(tela().querySelectorAll('tbody tr').length).toBe(2);
  });

  it('busca outro mês quando a coordenação troca a data', () => {
    backend.expectOne((r) => r.url === url).flush(OUTUBRO);
    const campo = tela().querySelector<HTMLInputElement>('#mes')!;
    campo.value = '2026-09';
    campo.dispatchEvent(new Event('change'));

    const req = backend.expectOne((r) => r.url === url);
    expect(req.request.params.get('mes')).toBe('9');
    req.flush({ ...OUTUBRO, mes: 9, total_entregas: 0, por_voluntario: [] });
    fixture.detectChanges();
    expect(tela().textContent).toContain('Nenhuma entrega registrada neste mês.');
  });
});

describe('mesAtual', () => {
  it('calcula o mês atual no horário de Londrina', () => {
    // 1º/11 às 01h UTC ainda é 31/10 em Londrina.
    expect(mesAtual(new Date('2026-11-01T01:00:00Z'))).toBe('2026-10');
  });
});

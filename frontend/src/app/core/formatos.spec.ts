import {
  cpfValido,
  dataHora,
  diaMes,
  diaMesLocal,
  formatarCpfDigitado,
  somenteDigitos,
} from './formatos';

describe('formatos', () => {
  it('converte data ISO em dia/mês', () => {
    expect(diaMes('2026-10-12')).toBe('12/10');
  });

  it('mostra data e hora no horário de Londrina', () => {
    expect(dataHora('2026-10-24T12:42:00Z')).toBe('24/10 às 9h42');
  });

  it('usa o dia de Londrina no histórico, mesmo perto da meia-noite UTC', () => {
    expect(diaMesLocal('2026-10-24T02:00:00Z')).toBe('23/10');
  });

  it('remove pontuação do CPF', () => {
    expect(somenteDigitos('123.321.654-60')).toBe('12332165460');
  });

  it('valida CPF com os dígitos verificadores', () => {
    expect(cpfValido('123.321.654-60')).toBe(true);
    expect(cpfValido('123.321.654-00')).toBe(false);
    expect(cpfValido('111.111.111-11')).toBe(false);
  });

  it('formata o CPF enquanto a pessoa digita', () => {
    expect(formatarCpfDigitado('123')).toBe('123');
    expect(formatarCpfDigitado('1233216')).toBe('123.321.6');
    expect(formatarCpfDigitado('12332165460')).toBe('123.321.654-60');
    expect(formatarCpfDigitado('123321654601234')).toBe('123.321.654-60');
  });
});

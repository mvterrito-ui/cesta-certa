/** "2026-10-12" -> "12/10" (sem conversão de fuso, a data já vem do servidor). */
export function diaMes(dataIso: string): string {
  const [, mes, dia] = dataIso.slice(0, 10).split('-');
  return `${dia}/${mes}`;
}

const FUSO = 'America/Sao_Paulo';

/** "2026-10-24T12:42:00Z" -> "24/10 às 9h42", no horário de Londrina. */
export function dataHora(momentoIso: string): string {
  const momento = new Date(momentoIso);
  const partes = new Intl.DateTimeFormat('pt-BR', {
    timeZone: FUSO,
    day: '2-digit',
    month: '2-digit',
    hour: 'numeric',
    minute: '2-digit',
    hour12: false,
  }).formatToParts(momento);
  const valor = (tipo: string) => partes.find((p) => p.type === tipo)?.value ?? '';
  return `${valor('day')}/${valor('month')} às ${Number(valor('hour'))}h${valor('minute')}`;
}

/** Data do histórico de entregas, no horário de Londrina: "24/10". */
export function diaMesLocal(momentoIso: string): string {
  return new Intl.DateTimeFormat('pt-BR', {
    timeZone: FUSO,
    day: '2-digit',
    month: '2-digit',
  }).format(new Date(momentoIso));
}

export function somenteDigitos(valor: string): string {
  return (valor ?? '').replace(/\D/g, '');
}

/** Mesma validação do servidor; aqui só para avisar antes de enviar. */
export function cpfValido(valor: string): boolean {
  const cpf = somenteDigitos(valor);
  if (cpf.length !== 11 || /^(\d)\1{10}$/.test(cpf)) {
    return false;
  }
  for (const tamanho of [9, 10]) {
    let soma = 0;
    for (let i = 0; i < tamanho; i++) {
      soma += Number(cpf[i]) * (tamanho + 1 - i);
    }
    if (((soma * 10) % 11) % 10 !== Number(cpf[tamanho])) {
      return false;
    }
  }
  return true;
}

/** Formata enquanto digita: "12332165460" -> "123.321.654-60". */
export function formatarCpfDigitado(valor: string): string {
  const d = somenteDigitos(valor).slice(0, 11);
  return d
    .replace(/^(\d{3})(\d)/, '$1.$2')
    .replace(/^(\d{3})\.(\d{3})(\d)/, '$1.$2.$3')
    .replace(/\.(\d{3})(\d{1,2})$/, '.$1-$2');
}

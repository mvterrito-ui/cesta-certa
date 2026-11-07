export type Perfil = 'administrador' | 'voluntario';

export interface Usuario {
  id: number;
  nome: string;
  email: string;
  perfil: Perfil;
}

export interface RespostaLogin {
  access_token: string;
  token_type: string;
  usuario: Usuario;
}

export interface FamiliaResumo {
  id: number;
  nome_responsavel: string;
  numero_integrantes: number;
  cpf: string;
  ultima_entrega: string | null;
  apta: boolean;
  proxima_entrega: string | null;
}

export interface EntregaHistorico {
  id: number;
  data_entrega: string;
  registrado_por: string;
}

export interface FamiliaDetalhe extends FamiliaResumo {
  endereco: string;
  telefone: string | null;
  observacao: string | null;
  status: string;
  entregas: EntregaHistorico[];
}

export interface NovaFamilia {
  nome_responsavel: string;
  documento_responsavel: string;
  endereco: string;
  numero_integrantes: number;
  telefone: string | null;
}

export interface EntregaRegistrada {
  id: number;
  familia_id: number;
  nome_responsavel: string;
  data_entrega: string;
  proxima_entrega: string;
}

/** Corpo do 409 devolvido quando a família recebeu cesta há menos de 15 dias (RF03). */
export interface BloqueioEntrega {
  detail: string;
  ultima_entrega: string;
  proxima_entrega: string;
}

export interface RelatorioMensal {
  ano: number;
  mes: number;
  total_entregas: number;
  familias_atendidas: number;
  pessoas_atendidas: number;
  familias_ativas: number;
  familias_sem_entrega: number;
  por_voluntario: { nome: string; entregas: number }[];
}

/** Estado passado da Tela 2 para a Tela 3. */
export type ResultadoEntrega =
  | { tipo: 'sucesso'; nome: string; dataEntrega: string }
  | { tipo: 'aviso'; nome: string; ultimaEntrega: string; proximaEntrega: string };

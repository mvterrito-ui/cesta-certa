import { HttpClient, HttpErrorResponse, HttpParams } from '@angular/common/http';
import { Injectable, inject, signal } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../environments/environment';
import { EntregaRegistrada, FamiliaDetalhe, FamiliaResumo, NovaFamilia } from './modelos';

@Injectable({ providedIn: 'root' })
export class ApiService {
  private readonly http = inject(HttpClient);
  private readonly base = environment.apiUrl;

  /** Último termo pesquisado, para manter a lista ao voltar da Tela 2. */
  readonly ultimaBusca = signal('');

  buscarFamilias(termo: string): Observable<FamiliaResumo[]> {
    const params = new HttpParams().set('busca', termo);
    return this.http.get<FamiliaResumo[]>(`${this.base}/familias`, { params });
  }

  obterFamilia(id: number): Observable<FamiliaDetalhe> {
    return this.http.get<FamiliaDetalhe>(`${this.base}/familias/${id}`);
  }

  cadastrarFamilia(dados: NovaFamilia): Observable<FamiliaDetalhe> {
    return this.http.post<FamiliaDetalhe>(`${this.base}/familias`, dados);
  }

  registrarEntrega(familiaId: number): Observable<EntregaRegistrada> {
    return this.http.post<EntregaRegistrada>(`${this.base}/familias/${familiaId}/entregas`, {});
  }
}

/** Mensagem legível para qualquer erro da API, sem detalhes técnicos. */
export function mensagemDeErro(erro: unknown): string {
  if (erro instanceof HttpErrorResponse) {
    if (erro.status === 0) {
      return 'Sem conexão com o servidor. Confira a internet e tente de novo.';
    }
    if (typeof erro.error?.detail === 'string') {
      return erro.error.detail;
    }
  }
  return 'Não foi possível concluir agora. Tente novamente.';
}

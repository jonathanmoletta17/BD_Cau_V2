/**
 * Módulo utilitário para filtragem de dados baseada em período.
 * Garante consistência entre Frontend e Backend (ISO 8601).
 */

export interface OpcoesFiltro {
  /**
   * Se true, lança um erro ao encontrar uma data inválida dentro do array de dados.
   * Se false (padrão), apenas ignora o item com data inválida.
   */
  strictMode?: boolean;
}

export interface ResultadoFiltro<T> {
  dados: T[];
  metadados: {
    totalOriginal: number;
    totalFiltrado: number;
    periodoAplicado: {
      inicio: string;
      fim: string;
    };
  };
}

/**
 * Converte uma entrada (string ou Date) para um objeto Date válido.
 * Lança erro se a data for inválida.
 */
function normalizarData(entrada: string | Date | number): Date {
  const data = new Date(entrada);
  if (isNaN(data.getTime())) {
    throw new Error(`Data inválida fornecida: ${String(entrada)}`);
  }
  return data;
}

/**
 * Filtra um array de objetos por um intervalo de datas (inclusivo).
 * 
 * @template T O tipo do objeto contido no array.
 * @param {T[]} dados Array de objetos a serem filtrados.
 * @param {keyof T} campoData A chave do objeto que contém a informação de data.
 * @param {string | Date} inicio Data de início do período (considerada às 00:00:00.000).
 * @param {string | Date} fim Data de fim do período (considerada às 23:59:59.999).
 * @param {OpcoesFiltro} [opcoes] Configurações opcionais de resiliência.
 * 
 * @returns {ResultadoFiltro<T>} Objeto contendo o array filtrado e metadados da operação.
 * 
 * @throws {Error} Se as datas de filtro forem inválidas ou se o início for posterior ao fim.
 * @throws {Error} Se strictMode for true e um item do array tiver data inválida.
 * 
 * @example
 * const { dados, metadados } = filtrarPorData(tickets, 'created_at', '2023-01-01', '2023-01-31');
 */
export function filtrarPorData<T>(
  dados: T[],
  campoData: keyof T,
  inicio: string | Date,
  fim: string | Date,
  opcoes: OpcoesFiltro = { strictMode: false }
): ResultadoFiltro<T> {
  // 1. Validação e Normalização dos Filtros
  let dataInicio: Date;
  let dataFim: Date;

  try {
    dataInicio = normalizarData(inicio);
    // Ajustar para o início do dia (00:00:00.000)
    dataInicio.setHours(0, 0, 0, 0);

    dataFim = normalizarData(fim);
    // Ajustar para o final do dia (23:59:59.999) para garantir inclusividade
    dataFim.setHours(23, 59, 59, 999);
  } catch (e) {
    throw new Error(`Erro nos parâmetros de filtro: ${(e as Error).message}`);
  }

  // 2. Validação Lógica do Intervalo
  if (dataInicio.getTime() > dataFim.getTime()) {
    throw new Error("Intervalo cronologicamente invertido: A data de início não pode ser posterior à data de fim.");
  }

  // 3. Processamento de Filtragem
  const dadosFiltrados = dados.filter((item, index) => {
    const valorItem = item[campoData];

    // Tratamento de valores nulos ou undefined no item
    if (valorItem === null || valorItem === undefined) {
      if (opcoes.strictMode) {
        throw new Error(`Item no índice ${index} possui o campo '${String(campoData)}' nulo ou indefinido.`);
      }
      return false;
    }

    // Tentar converter a data do item
    let dataItem: Date;
    try {
      dataItem = new Date(valorItem as string | number | Date);
      if (isNaN(dataItem.getTime())) {
        throw new Error("Invalid Date");
      }
    } catch (e) {
      if (opcoes.strictMode) {
        throw new Error(`Item no índice ${index} possui data inválida no campo '${String(campoData)}': ${valorItem}`);
      }
      return false; // Ignora o item no modo resiliente (padrão)
    }

    // Comparação por timestamp para performance e precisão
    const timeItem = dataItem.getTime();
    return timeItem >= dataInicio.getTime() && timeItem <= dataFim.getTime();
  });

  // 4. Construção do Retorno
  return {
    dados: dadosFiltrados,
    metadados: {
      totalOriginal: dados.length,
      totalFiltrado: dadosFiltrados.length,
      periodoAplicado: {
        inicio: dataInicio.toISOString(),
        fim: dataFim.toISOString()
      }
    }
  };
}
import { describe, it, expect } from 'vitest';
import { filtrarPorData } from './dateFilter.utils';

// Mock de dados
interface Ticket {
  id: number;
  dataCriacao: string;
  titulo: string;
}

const mockTickets: Ticket[] = [
  { id: 1, dataCriacao: '2023-01-01T10:00:00Z', titulo: 'Ticket Jan 1' },
  { id: 2, dataCriacao: '2023-01-15T12:00:00Z', titulo: 'Ticket Jan 15' },
  { id: 3, dataCriacao: '2023-01-31T23:59:59Z', titulo: 'Ticket Jan 31' },
  { id: 4, dataCriacao: '2023-02-01T00:00:01Z', titulo: 'Ticket Feb 1' },
];

describe('filtrarPorData', () => {
  
  // --- 1. Happy Path ---
  
  it('deve filtrar corretamente registros dentro de um intervalo (inclusivo)', () => {
    const { dados, metadados } = filtrarPorData(
      mockTickets,
      'dataCriacao',
      '2023-01-01',
      '2023-01-31'
    );

    expect(dados).toHaveLength(3); // IDs 1, 2, 3
    expect(dados.map(d => d.id)).toEqual([1, 2, 3]);
    expect(metadados.totalOriginal).toBe(4);
    expect(metadados.totalFiltrado).toBe(3);
  });

  it('deve normalizar strings de data (00:00 a 23:59) garantindo inclusão nas bordas', () => {
    // Filtrando apenas o dia 31
    const { dados } = filtrarPorData(
      mockTickets,
      'dataCriacao',
      '2023-01-31',
      '2023-01-31'
    );
    // Deve incluir o ticket das 23:59:59
    expect(dados).toHaveLength(1);
    expect(dados[0].id).toBe(3);
  });

  // --- 2. Edge Cases ---

  it('deve retornar array vazio se nenhum item corresponder', () => {
    const { dados } = filtrarPorData(
      mockTickets,
      'dataCriacao',
      '2023-03-01',
      '2023-03-31'
    );
    expect(dados).toHaveLength(0);
  });

  it('deve lidar com array de dados vazio', () => {
    const { dados, metadados } = filtrarPorData(
      [],
      'dataCriacao',
      '2023-01-01',
      '2023-01-31'
    );
    expect(dados).toHaveLength(0);
    expect(metadados.totalOriginal).toBe(0);
  });

  // --- 3. Error Handling & Resiliência ---

  it('deve lançar erro se a data de início for posterior ao fim', () => {
    expect(() => {
      filtrarPorData(mockTickets, 'dataCriacao', '2023-02-01', '2023-01-01');
    }).toThrow("Intervalo cronologicamente invertido");
  });

  it('deve lançar erro se as datas de filtro forem inválidas', () => {
    expect(() => {
      filtrarPorData(mockTickets, 'dataCriacao', 'data-invalida', '2023-01-01');
    }).toThrow("Erro nos parâmetros de filtro");
  });

  it('deve ignorar itens com datas inválidas por padrão (strictMode: false)', () => {
    const dadosSujos = [
      ...mockTickets,
      { id: 99, dataCriacao: 'invalid-date', titulo: 'Erro' },
      { id: 100, dataCriacao: null as any, titulo: 'Nulo' }
    ];

    const { dados, metadados } = filtrarPorData(
      dadosSujos,
      'dataCriacao',
      '2023-01-01',
      '2023-01-31'
    );

    // Deve filtrar os válidos (1, 2, 3) e ignorar os inválidos (99, 100) sem quebrar
    expect(dados).toHaveLength(3);
    expect(metadados.totalOriginal).toBe(6);
  });

  it('deve lançar erro ao encontrar data inválida no array se strictMode: true', () => {
    const dadosSujos = [
      { id: 99, dataCriacao: 'invalid-date', titulo: 'Erro' }
    ];

    expect(() => {
      filtrarPorData(
        dadosSujos,
        'dataCriacao',
        '2023-01-01',
        '2023-01-31',
        { strictMode: true }
      );
    }).toThrow(/Item no índice 0 possui data inválida/);
  });
});
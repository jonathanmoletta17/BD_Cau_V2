/**
 * Fuzzy Matching para busca de entidades
 * Implementa Levenshtein distance para encontrar entidades similares
 */

export class FuzzyMatcher {
    /**
     * Calcula Levenshtein distance entre duas strings
     * Retorna o número de edições necessárias para transformar s1 em s2
     */
    static levenshteinDistance(s1: string, s2: string): number {
        const len1 = s1.length;
        const len2 = s2.length;
        const matrix: number[][] = [];

        // Inicializar matriz
        for (let i = 0; i <= len1; i++) {
            matrix[i] = [i];
        }
        for (let j = 0; j <= len2; j++) {
            matrix[0][j] = j;
        }

        // Calcular distâncias
        for (let i = 1; i <= len1; i++) {
            for (let j = 1; j <= len2; j++) {
                const cost = s1[i - 1] === s2[j - 1] ? 0 : 1;
                matrix[i][j] = Math.min(
                    matrix[i - 1][j] + 1,      // Deletion
                    matrix[i][j - 1] + 1,      // Insertion
                    matrix[i - 1][j - 1] + cost // Substitution
                );
            }
        }

        return matrix[len1][len2];
    }

    /**
     * Calcula similaridade entre duas strings (0-1)
     * 1 = idênticas, 0 = completamente diferentes
     */
    static similarity(s1: string, s2: string): number {
        const longer = s1.length > s2.length ? s1 : s2;
        const shorter = s1.length > s2.length ? s2 : s1;

        const longerLength = longer.length;
        if (longerLength === 0) {
            return 1.0;
        }

        const distance = this.levenshteinDistance(longer, shorter);
        return (longerLength - distance) / longerLength;
    }

    /**
     * Normaliza string para comparação
     * Remove acentos, converte para lowercase, remove espaços extras
     */
    static normalize(str: string): string {
        return str
            .toLowerCase()
            .normalize('NFD')
            .replace(/[\u0300-\u036f]/g, '') // Remove acentos
            .replace(/\s+/g, ' ')            // Normaliza espaços
            .trim();
    }

    /**
     * Busca fuzzy em uma lista de strings
     * Retorna matches ordenados por similaridade
     */
    static search<T>(
        query: string,
        items: T[],
        keyExtractor: (item: T) => string,
        minSimilarity: number = 0.6
    ): Array<{ item: T; score: number; match: string }> {
        const normalizedQuery = this.normalize(query);

        const results = items
            .map(item => {
                const itemStr = keyExtractor(item);
                const normalizedItem = this.normalize(itemStr);

                // Calcula várias métricas de similaridade
                const exactMatch = normalizedQuery === normalizedItem ? 1.0 : 0;
                const contains = normalizedItem.includes(normalizedQuery) ? 0.8 : 0;
                const levenshtein = this.similarity(normalizedQuery, normalizedItem);

                // Score final é o máximo das métricas
                const score = Math.max(exactMatch, contains, levenshtein);

                return {
                    item,
                    score,
                    match: itemStr
                };
            })
            .filter(result => result.score >= minSimilarity)
            .sort((a, b) => b.score - a.score);

        return results;
    }

    /**
     * Busca a melhor correspondência
     */
    static findBestMatch<T>(
        query: string,
        items: T[],
        keyExtractor: (item: T) => string,
        minSimilarity: number = 0.7
    ): { item: T; score: number } | null {
        const results = this.search(query, items, keyExtractor, minSimilarity);
        return results.length > 0 ? results[0] : null;
    }

    /**
     * Gera sugestões baseadas em similaridade
     */
    static getSuggestions<T>(
        query: string,
        items: T[],
        keyExtractor: (item: T) => string,
        maxSuggestions: number = 3
    ): string[] {
        const results = this.search(query, items, keyExtractor, 0.5);
        return results
            .slice(0, maxSuggestions)
            .map(r => r.match);
    }
}

/**
 * Exemplo de uso:
 * 
 * const entities = [
 *   { id: 1, name: "Casa Civil" },
 *   { id: 2, name: "Casa Militar" },
 *   { id: 3, name: "SECOM" }
 * ];
 * 
 * const match = FuzzyMatcher.findBestMatch(
 *   "casa civil",
 *   entities,
 *   e => e.name
 * );
 * // { item: { id: 1, name: "Casa Civil" }, score: 1.0 }
 * 
 * const suggestions = FuzzyMatcher.getSuggestions(
 *   "caza",
 *   entities,
 *   e => e.name
 * );
 * // ["Casa Civil", "Casa Militar"]
 */

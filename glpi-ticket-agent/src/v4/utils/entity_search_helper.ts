import { FuzzyMatcher } from '../utils/fuzzy_matcher';

/**
 * Enhanced GLPI Bridge com Fuzzy Matching
 * Extensão do GLPIBridgeService com busca inteligente de entidades
 */

export interface Entity {
    id: number;
    name: string;
}

export class EntitySearchHelper {
    /**
     * Busca entidade com fuzzy matching
     * Ordem de tentativas:
     * 1. Match exato (case-insensitive)
     * 2. Fuzzy match (similaridade > 0.7)
     * 3. Substring match
     */
    static async searchEntityWithFuzzy(
        query: string,
        allEntities: Entity[]
    ): Promise<{
        found: Entity | null;
        confidence: number;
        suggestions: string[];
        method: 'exact' | 'fuzzy' | 'substring' | 'none';
    }> {
        // 1. Tentar match exato (case-insensitive)
        const exactMatch = allEntities.find(e =>
            e.name.toLowerCase() === query.toLowerCase()
        );

        if (exactMatch) {
            console.log(`[EntitySearch] Exact match: "${query}" → "${exactMatch.name}"`);
            return {
                found: exactMatch,
                confidence: 1.0,
                suggestions: [],
                method: 'exact'
            };
        }

        // 2. Tentar fuzzy match
        const fuzzyResult = FuzzyMatcher.findBestMatch(
            query,
            allEntities,
            e => e.name,
            0.7 // Mínimo 70% similaridade
        );

        if (fuzzyResult) {
            console.log(`[EntitySearch] Fuzzy match: "${query}" → "${fuzzyResult.item.name}" (${Math.round(fuzzyResult.score * 100)}%)`);
            return {
                found: fuzzyResult.item,
                confidence: fuzzyResult.score,
                suggestions: [],
                method: 'fuzzy'
            };
        }

        // 3. Tentar substring match
        const substringMatches = allEntities.filter(e =>
            e.name.toLowerCase().includes(query.toLowerCase()) ||
            query.toLowerCase().includes(e.name.toLowerCase())
        );

        if (substringMatches.length === 1) {
            console.log(`[EntitySearch] Substring match: "${query}" → "${substringMatches[0].name}"`);
            return {
                found: substringMatches[0],
                confidence: 0.8,
                suggestions: [],
                method: 'substring'
            };
        }

        // 4. Não encontrou - gerar sugestões
        const suggestions = FuzzyMatcher.getSuggestions(
            query,
            allEntities,
            e => e.name,
            3 // Top 3 sugestões
        );

        console.warn(`[EntitySearch] Não encontrado: "${query}". Sugestões: ${suggestions.join(', ')}`);

        return {
            found: null,
            confidence: 0,
            suggestions,
            method: 'none'
        };
    }

    /**
     * Valida se uma entidade existe com tolerância
     */
    static validateEntity(
        entityName: string,
        allEntities: Entity[],
        minConfidence: number = 0.7
    ): {
        valid: boolean;
        entity?: Entity;
        confidence: number;
        message: string;
    } {
        const result = FuzzyMatcher.findBestMatch(
            entityName,
            allEntities,
            e => e.name,
            minConfidence
        );

        if (result) {
            const isExactMatch = result.score === 1.0;
            return {
                valid: true,
                entity: result.item,
                confidence: result.score,
                message: isExactMatch
                    ? `Entidade: ${result.item.name}`
                    : `Entidade encontrada por similaridade: ${result.item.name} (${Math.round(result.score * 100)}%)`
            };
        }

        const suggestions = FuzzyMatcher.getSuggestions(entityName, allEntities, e => e.name, 3);
        return {
            valid: false,
            confidence: 0,
            message: suggestions.length > 0
                ? `Entidade "${entityName}" não encontrada. Você quis dizer: ${suggestions.join(', ')}?`
                : `Entidade "${entityName}" não encontrada.`
        };
    }
}

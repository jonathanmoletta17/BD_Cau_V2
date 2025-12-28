import { KNOWLEDGE_BASE, EntityKnowledge, CategoryKnowledge, BusinessRule, FAQ } from './knowledge_base';

/**
 * RAG Service - Retrieval-Augmented Generation
 * 
 * Busca contexto relevante na knowledge base e formata para injeção no prompt do LLM
 */

export interface RAGResult {
    entities: EntityKnowledge[];
    categories: CategoryKnowledge[];
    rules: BusinessRule[];
    faqs: FAQ[];
    relevanceScore: number;
}

export class RAGService {
    /**
     * Busca contexto relevante baseado na query do usuário
     */
    search(query: string): RAGResult {
        const normalizedQuery = query.toLowerCase();

        // Buscar entidades relevantes
        const entities = this.searchEntities(normalizedQuery);

        // Buscar categorias relevantes
        const categories = this.searchCategories(normalizedQuery);

        // Buscar regras de negócio relevantes
        const rules = this.searchRules(normalizedQuery);

        // Buscar FAQs relevantes
        const faqs = this.searchFAQs(normalizedQuery);

        // Calcular score de relevância
        const relevanceScore = this.calculateRelevance(
            entities.length,
            categories.length,
            rules.length,
            faqs.length
        );

        return {
            entities,
            categories,
            rules,
            faqs,
            relevanceScore
        };
    }

    /**
     * Busca entidades por nome ou aliases
     */
    private searchEntities(query: string): EntityKnowledge[] {
        return KNOWLEDGE_BASE.entities.filter(entity => {
            // Match no nome
            if (entity.name.toLowerCase().includes(query)) return true;

            // Match no nome completo
            if (entity.fullName.toLowerCase().includes(query)) return true;

            // Match em aliases
            return entity.aliases.some(alias =>
                query.includes(alias.toLowerCase()) || alias.toLowerCase().includes(query)
            );
        });
    }

    /**
     * Busca categorias por nome ou exemplos
     */
    private searchCategories(query: string): CategoryKnowledge[] {
        return KNOWLEDGE_BASE.categories.filter(category => {
            // Match no nome
            if (query.includes(category.name.toLowerCase())) return true;

            // Match em exemplos
            return category.examples.some(example =>
                query.includes(example.toLowerCase()) || example.toLowerCase().includes(query)
            );
        });
    }

    /**
     * Busca regras de negócio por tópico ou conteúdo
     */
    private searchRules(query: string): BusinessRule[] {
        return KNOWLEDGE_BASE.rules.filter(rule => {
            // Match no tópico
            if (query.includes(rule.topic.toLowerCase())) return true;

            // Match no conteúdo
            if (rule.content.toLowerCase().includes(query)) return true;

            // Match em exemplos
            return (rule.examples || []).some(example =>
                query.includes(example.toLowerCase())
            );
        });
    }

    /**
     * Busca FAQs por keywords
     */
    private searchFAQs(query: string): FAQ[] {
        return KNOWLEDGE_BASE.faqs.filter(faq =>
            faq.keywords.some(keyword => query.includes(keyword.toLowerCase()))
        );
    }

    /**
     * Calcula score de relevância (0-1)
     */
    private calculateRelevance(
        entityCount: number,
        categoryCount: number,
        ruleCount: number,
        faqCount: number
    ): number {
        const total = entityCount + categoryCount + ruleCount + faqCount;
        return Math.min(total / 5, 1); // Normalizado para max 1.0
    }

    /**
     * Formata contexto para injeção no prompt
     */
    formatContext(result: RAGResult): string {
        const sections: string[] = [];

        // Adicionar entidades
        if (result.entities.length > 0) {
            sections.push("📋 ENTIDADES RELEVANTES:");
            result.entities.forEach(e => {
                sections.push(`  • ${e.fullName} (${e.name}): ${e.context}`);
            });
        }

        // Adicionar categorias
        if (result.categories.length > 0) {
            sections.push("\n🔧 CATEGORIAS RELACIONADAS:");
            result.categories.forEach(c => {
                sections.push(`  • ${c.name}: ${c.examples.slice(0, 3).join(', ')}`);
            });
        }

        // Adicionar regras
        if (result.rules.length > 0) {
            sections.push("\n📝 REGRAS DE NEGÓCIO:");
            result.rules.forEach(r => {
                sections.push(`  • ${r.topic}: ${r.content}`);
            });
        }

        // Adicionar FAQs
        if (result.faqs.length > 0) {
            sections.push("\n❓ RESPOSTAS COMUNS:");
            result.faqs.forEach(faq => {
                sections.push(`  Q: ${faq.question}`);
                sections.push(`  R: ${faq.answer}`);
            });
        }

        return sections.join('\n');
    }

    /**
     * Busca procedimentos de diagnóstico para uma categoria
     */
    getDiagnosticSteps(categoryName: string): string[] {
        const category = KNOWLEDGE_BASE.categories.find(c =>
            c.name.toLowerCase() === categoryName.toLowerCase()
        );

        return category?.diagnosticSteps || [];
    }

    /**
     * Obtém exemplos de classificação para o Router
     */
    getClassificationExamples(): string {
        const chitchatExamples = KNOWLEDGE_BASE.chitchat
            .flatMap(pattern => pattern.examples.slice(0, 2))
            .map(ex => `  - "${ex}" → CHITCHAT`)
            .join('\n');

        return `
EXEMPLOS DE CLASSIFICAÇÃO:

SERVICE_REQUEST:
${KNOWLEDGE_BASE.categories
                .find(c => c.name === "Novo Usuário")
                ?.examples.slice(0, 4).map(ex => `  - "${ex}" → SERVICE_REQUEST`)
                .join('\n') || ''}

INCIDENT:
${KNOWLEDGE_BASE.categories
                .find(c => c.name === "Impressora")
                ?.examples.slice(0, 3).map(ex => `  - "${ex}" → INCIDENT`)
                .join('\n') || ''}

CHITCHAT:
${chitchatExamples}
`.trim();
    }

    /**
     * Verifica se a query parece ser chitchat
     */
    isLikelyChitchat(query: string): boolean {
        const normalized = query.toLowerCase().trim();

        return KNOWLEDGE_BASE.chitchat.some(pattern =>
            pattern.examples.some(example =>
                normalized === example.toLowerCase() ||
                normalized.includes(example.toLowerCase())
            )
        );
    }
}

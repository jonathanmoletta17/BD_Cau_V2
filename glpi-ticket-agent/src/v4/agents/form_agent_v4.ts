import { LLMService } from '../../services/llm_service';
import { GLPIBridgeService } from '../services/glpi_bridge_service';
import { RAGService } from '../services/rag_service';
import { TelemetryService } from '../services/telemetry_service';
import { AgentResponse, FormSchema, V3Intent } from '../types';
import { FieldValidator, ExtractedFields } from '../validators/field_validator';

/**
 * FormAgent V4 - Gera formulários dinâmicos
 * consultando o GLPI em tempo real + RAG para contexto rico + Telemetria
 */
export class FormAgentV4 {
    // Mapeamento de aliases (nomes curtos → nomes oficiais do GLPI)
    private readonly orgAliases: Record<string, string> = {
        'DTIC': 'Departamento de Tecnologia',
        'GG': 'Gabinente',
        'CAU': 'Central de Atendimentos'
    };

    private ragService: RAGService;

    constructor(
        private llm: LLMService,
        private glpiBridge: GLPIBridgeService,
        private telemetry?: TelemetryService
    ) {
        this.ragService = new RAGService();
    }

    async process(message: string, history: string[], conversationId?: string): Promise<AgentResponse> {
        console.log('[FormAgentV4] Gerando formulário dinâmico...');

        // Iniciar telemetria
        const telemetryEvent = conversationId && this.telemetry
            ? this.telemetry.createEvent(conversationId, 'FormAgentV4', 'generation')
            : null;

        // 1. Buscar contexto do GLPI
        const [categories, entities] = await Promise.all([
            this.glpiBridge.getCategories(),
            this.glpiBridge.getEntities()
        ]);

        // 1.5. PRÉ-VALIDAÇÃO: Detectar entidades mencionadas (com aliases)
        const knownOrgs = [
            'Casa Civil', 'Casa Militar', 'SECOM', 'Gabinete',
            'DTIC', 'Departamento de Tecnologia', 'Procergs',
            'Central de Atendimentos', 'GG', 'CAU'
        ];
        let detectedEntity: { id: number; name: string } | null = null;
        let detectedKeyword: string | null = null;

        for (const orgName of knownOrgs) {
            if (message.toLowerCase().includes(orgName.toLowerCase())) {
                // Resolver alias se existir
                const realName = this.orgAliases[orgName] || orgName;

                const found = await this.glpiBridge.searchEntity(realName);
                if (found) {
                    detectedEntity = { id: found.id, name: found.name };
                    detectedKeyword = orgName;
                    console.log(`[FormAgentV4] 🎯 Entidade detectada: ${orgName} → ${found.name} (ID: ${found.id})`);
                    break;
                }
            }
        }

        // 2. BUSCAR CONTEXTO RAG
        const ragResult = this.ragService.search(message);
        const ragContext = ragResult.relevanceScore > 0.1
            ? `\n${this.ragService.formatContext(ragResult)}\n`
            : '';

        // 3. Construir prompt com informação PRÉ-VALIDADA + RAG
        const entityHint = detectedEntity
            ? `\nENTIDADE JÁ IDENTIFICADA: ${detectedEntity.name} (use value: ${detectedEntity.id})`
            : '';

        const systemPrompt = `
Você é um sistema de geração de formulários. RETORNE APENAS JSON PURO.

${ragContext}
DADOS DO GLPI:
Entidades: ${entities.slice(0, 10).map(e => `${e.name} (ID:${e.id})`).join(', ')}...
${entityHint}

INPUT: "${message}"

IMPORTANTE: Retorne SOMENTE JSON.

INSTRUÇÕES DE EXTRAÇÃO:
1. **userName**: Extraia o nome COMPLETO mencionado (obrigatório)
2. **entity**: Use ID da entidade já identificada ou null (obrigatório)
3. **jobTitle**: Extraia cargo se mencionado, senão use "" (opcional)
4. **email**: Extraia email se mencionado, senão use "" (opcional)
5. **phone**: Extraia telefone se mencionado, senão use "" (opcional)

EXEMPLO DE SAÍDA (JSON puro):
{
    "formKey": "create_user_v4",
    "title": "Solicitação de Novo Usuário",
    "description": "Complete os dados",
    "fields": [
        {"id":"userName","label":"Nome Completo","type":"text","required":true,"value":"NOME_EXTRAIDO"},
        {"id":"entity","label":"Órgão de Lotação","type":"select","required":true,"value":${detectedEntity?.id || 'null'},"options":["Casa Civil","Casa Militar","SECOM","DTIC"]},
        {"id":"jobTitle","label":"Cargo","type":"text","required":false,"value":""},
        {"id":"email","label":"Email","type":"email","required":false,"value":""},
        {"id":"phone","label":"Telefone","type":"tel","required":false,"value":""}
    ],
    "submitLabel": "Criar Usuário"
}`.trim();

        try {
            const response = await this.llm.complete(message, systemPrompt);

            // Tentar extrair JSON se houver texto extra
            const jsonMatch = response.match(/\{[\s\S]*\}/);
            const jsonString = jsonMatch ? jsonMatch[0] : response;

            const formSchema: FormSchema = JSON.parse(jsonString);

            // Completar telemetria
            if (telemetryEvent) {
                await telemetryEvent.complete({
                    input: message,
                    decision: 'Form generated',
                    reasoning: {
                        entity_detected: detectedKeyword && detectedEntity ? {
                            keyword: detectedKeyword,
                            mapped_to: detectedEntity
                        } : undefined,
                        rag_context: {
                            entities_found: ragResult.entities.length,
                            categories_found: ragResult.categories.length,
                            rules_applied: ragResult.rules.map(r => r.topic),
                            relevance_score: ragResult.relevanceScore
                        },
                        extracted_fields: {
                            userName: formSchema.fields.find(f => f.id === 'userName')?.value,
                            entity: detectedEntity?.id
                        }
                    }
                });
            }

            return {
                type: 'FORM',
                message: `Para prosseguir com a **${formSchema.title}**, confirme os dados:`,
                metadata: {
                    form: formSchema,
                    intent: 'SERVICE_REQUEST' as V3Intent
                }
            };

        } catch (error: any) {
            console.error('[FormAgentV4] Erro ao gerar schema:', error);

            if (telemetryEvent) {
                await telemetryEvent.complete({
                    input: message,
                    decision: 'Error',
                    reasoning: {}
                });
            }

            // Fallback: retornar erro como texto
            return {
                type: 'TEXT',
                message: 'Desculpe, tive problemas para processar sua solicitação. Pode reformular?',
                metadata: { intent: 'SERVICE_REQUEST' as V3Intent }
            };
        }
    }
}

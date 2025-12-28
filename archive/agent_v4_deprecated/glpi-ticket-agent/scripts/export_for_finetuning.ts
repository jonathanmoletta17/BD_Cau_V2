import * as fs from 'fs';
import { ConversationLogger, ConversationLog } from '../src/v4/services/conversation_logger';
import { Redis } from 'ioredis';

/**
 * Export de conversas para fine-tuning com NVIDIA NIM / TensorRT-LLM
 * 
 * GPU: RTX A 4000 (16GB VRAM)
 * Formato: NVIDIA NIM, OpenAI, Llama
 */

interface ExportOptions {
    minTurns?: number;
    onlyWithFeedback?: boolean;
    feedbackType?: 'helpful' | 'not_helpful' | 'all';
    format: 'nvidia-nim' | 'openai' | 'llama' | 'alpaca';
    outputFile: string;
    balanceIntents?: boolean;
}

interface NVIDIANIMFormat {
    prompt: string;
    completion: string;
    metadata?: {
        intent: string;
        confidence: number;
        source: string;
    };
}

interface OpenAIFormat {
    messages: Array<{
        role: 'system' | 'user' | 'assistant';
        content: string;
    }>;
}

interface LlamaFormat {
    instruction: string;
    input: string;
    output: string;
}

async function exportConversations(options: ExportOptions) {
    console.log('🚀 Exportando conversas para fine-tuning...\n');
    console.log(`Formato: ${options.format}`);
    console.log(`Filtros: minTurns=${options.minTurns}, onlyFeedback=${options.onlyWithFeedback}\n`);

    const redis = new Redis({
        host: process.env.REDIS_HOST || 'localhost',
        port: parseInt(process.env.REDIS_PORT || '6379')
    });

    const logger = new ConversationLogger(redis);

    // 1. Obter todas as conversas
    const ids = await logger.getAllConversationIds();
    console.log(`📊 Total de conversas encontradas: ${ids.length}\n`);

    const conversations: ConversationLog[] = [];

    for (const id of ids) {
        const conv = await logger.getConversation(id);
        if (!conv) continue;

        // Filtros
        if (options.minTurns && conv.turns.length < options.minTurns) continue;

        if (options.onlyWithFeedback) {
            const hasFeedback = conv.turns.some(t => t.user_feedback !== null);
            if (!hasFeedback) continue;
        }

        if (options.feedbackType && options.feedbackType !== 'all') {
            const hasCorrectFeedback = conv.turns.some(t => t.user_feedback === options.feedbackType);
            if (!hasCorrectFeedback) continue;
        }

        conversations.push(conv);
    }

    console.log(`✅ Conversas filtradas: ${conversations.length}\n`);

    // 2. Converter para formato desejado
    let trainingData: any[] = [];

    switch (options.format) {
        case 'nvidia-nim':
            trainingData = convertToNVIDIANIM(conversations);
            break;
        case 'openai':
            trainingData = convertToOpenAI(conversations);
            break;
        case 'llama':
        case 'alpaca':
            trainingData = convertToLlama(conversations);
            break;
    }

    // 3. Balancear intents se solicitado
    if (options.balanceIntents) {
        trainingData = balanceByIntent(trainingData);
    }

    // 4. Salvar em JSONL
    const jsonlContent = trainingData.map(d => JSON.stringify(d)).join('\n');
    fs.writeFileSync(options.outputFile, jsonlContent);

    console.log(`💾 Dados exportados: ${options.outputFile}`);
    console.log(`📝 Total de exemplos: ${trainingData.length}\n`);

    // 5. Estatísticas
    printStats(trainingData);

    await redis.quit();
}

/**
 * Converte para formato NVIDIA NIM (otimizado para RTX A 4000)
 */
function convertToNVIDIANIM(conversations: ConversationLog[]): NVIDIANIMFormat[] {
    const data: NVIDIANIMFormat[] = [];

    conversations.forEach((conv: ConversationLog) => {
        conv.turns.forEach((turn: any) => {
            // Router classification task
            data.push({
                prompt: `### Task: Classify user intent\n### User: ${turn.input}\n### Intent:`,
                completion: ` ${turn.router_intent}`,
                metadata: {
                    intent: turn.router_intent,
                    confidence: turn.router_confidence,
                    source: 'router'
                }
            });

            // Response generation task (se não for FORM)
            if (turn.response_type === 'TEXT') {
                data.push({
                    prompt: `### Task: Generate support response\n### User: ${turn.input}\n### Assistant:`,
                    completion: ` ${turn.agent_response}`,
                    metadata: {
                        intent: turn.router_intent,
                        confidence: turn.router_confidence,
                        source: 'agent'
                    }
                });
            }
        });
    });

    return data;
}

/**
 * Converte para formato OpenAI
 */
function convertToOpenAI(conversations: ConversationLog[]): OpenAIFormat[] {
    const data: OpenAIFormat[] = [];

    const SYSTEM_PROMPT = `Você é um assistente de suporte técnico especializado em sistemas GLPI. Classifique solicitações como SERVICE_REQUEST, INCIDENT ou CHITCHAT.`;

    conversations.forEach((conv: ConversationLog) => {
        conv.turns.forEach((turn: any) => {
            data.push({
                messages: [
                    { role: 'system', content: SYSTEM_PROMPT },
                    { role: 'user', content: turn.input },
                    { role: 'assistant', content: turn.router_intent }
                ]
            });
        });
    });

    return data;
}

/**
 * Converte para formato Llama/Alpaca
 */
function convertToLlama(conversations: ConversationLog[]): LlamaFormat[] {
    const data: LlamaFormat[] = [];

    conversations.forEach((conv: ConversationLog) => {
        conv.turns.forEach((turn: any) => {
            // Classification task
            data.push({
                instruction: "Classifique a solicitação do usuário em SERVICE_REQUEST, INCIDENT ou CHITCHAT",
                input: turn.input,
                output: turn.router_intent
            });

            // Response task
            if (turn.response_type === 'TEXT') {
                data.push({
                    instruction: "Responda à solicitação do usuário como um assistente de suporte",
                    input: turn.input,
                    output: turn.agent_response
                });
            }
        });
    });

    return data;
}

/**
 * Balanceia dataset por intent
 */
function balanceByIntent(data: any[]): any[] {
    const byIntent: Record<string, any[]> = {
        'SERVICE_REQUEST': [],
        'INCIDENT': [],
        'CHITCHAT': []
    };

    // Separar por intent
    data.forEach(item => {
        const intent = item.metadata?.intent || item.output;
        if (byIntent[intent]) {
            byIntent[intent].push(item);
        }
    });

    // Encontrar mínimo
    const counts = Object.values(byIntent).map(arr => arr.length);
    const minCount = Math.min(...counts);

    // Balancear (undersampling)
    const balanced: any[] = [];
    Object.values(byIntent).forEach(arr => {
        balanced.push(...arr.slice(0, minCount));
    });

    // Shuffle
    return balanced.sort(() => Math.random() - 0.5);
}

/**
 * Imprime estatísticas
 */
function printStats(data: any[]) {
    const intentCounts: Record<string, number> = {};

    data.forEach((item: any) => {
        const intent = item.metadata?.intent || item.output || 'UNKNOWN';
        intentCounts[intent] = (intentCounts[intent] || 0) + 1;
    });

    console.log('📊 Distribuição por Intent:');
    Object.entries(intentCounts).forEach(([intent, count]) => {
        const pct = ((count / data.length) * 100).toFixed(1);
        console.log(`   ${intent}: ${count} (${pct}%)`);
    });
}

// CLI
const args = process.argv.slice(2);
const format = (args.find(a => a.startsWith('--format='))?.split('=')[1] || 'nvidia-nim') as any;
const minTurns = parseInt(args.find(a => a.startsWith('--min-turns='))?.split('=')[1] || '2');
const onlyFeedback = args.includes('--only-feedback');
const balance = args.includes('--balance');
const output = args.find(a => a.startsWith('--output='))?.split('=')[1] || 'training_data.jsonl';

exportConversations({
    format,
    minTurns,
    onlyWithFeedback: onlyFeedback,
    feedbackType: 'helpful',
    balanceIntents: balance,
    outputFile: output
}).catch(console.error);

/**
 * USAGE:
 * 
 * npx tsx scripts/export_for_finetuning.ts \
 *   --format=nvidia-nim \
 *   --min-turns=2 \
 *   --only-feedback \
 *   --balance \
 *   --output=training_data.jsonl
 */

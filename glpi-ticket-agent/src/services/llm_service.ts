import fetch from 'node-fetch';
import { configManager } from '../config';
import { jsonrepair } from 'jsonrepair';

export class LLMService {
    private config = configManager.getLLMConfig();

    /**
     * Completes a prompt using the configured LLM.
     * Returns the raw string response.
     */
    async complete(prompt: string, systemPrompt?: string): Promise<string> {
        // Normalize URL: Remove trailing /v1 or / if present to avoid duplication
        const baseUrl = this.config.baseUrl.replace(/\/v1\/?$/, '').replace(/\/$/, '');
        const url = `${baseUrl}/v1/chat/completions`;

        // Fallback system prompt
        const sys = systemPrompt || "You are a helpful assistant.";

        const body = {
            model: this.config.model,
            messages: [
                { role: "system", content: sys },
                { role: "user", content: prompt }
            ],
            temperature: this.config.temperature,
            max_tokens: 1024,
            stream: false
        };

        try {
            console.log(`[LLMService] Calling ${url} with model ${this.config.model}`);
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.config.apiKey}`
                },
                body: JSON.stringify(body)
            });

            if (!response.ok) {
                const errText = await response.text();
                throw new Error(`LLM API Error ${response.status}: ${errText}`);
            }

            const data = await response.json() as any;

            // OpenAI format
            const content = data.choices?.[0]?.message?.content || "";
            return content.trim();

        } catch (error) {
            console.error("[LLMService] Failed to complete:", error);
            return "";
        }
    }

    /**
     * Completes a prompt and parses the result as JSON.
     * Uses jsonrepair to fix common LLM syntax errors.
     */
    async completeJson<T>(prompt: string, schemaDescription?: string): Promise<T | null> {
        const systemPrompt = `You are a JSON-only API. You must return a valid JSON object matching the requested schema. Do not include markdown blocks like \`\`\`json. Just the raw JSON.
    
    ${schemaDescription ? "Expected Schema:\n" + schemaDescription : ""}
    `;

        const raw = await this.complete(prompt, systemPrompt);
        if (!raw) return null;

        try {
            // Clean up markdown code blocks if present (common Llama artifact)
            let clean = raw.replace(/```json/g, '').replace(/```/g, '').trim();

            // Use jsonrepair to handle missing quotes, trailing commas, etc.
            const parsed = JSON.parse(jsonrepair(clean));
            return parsed as T;
        } catch (e) {
            console.error("[LLMService] JSON Parse Error on:", raw, e);
            return null;
        }
    }
}

export const llmService = new LLMService();

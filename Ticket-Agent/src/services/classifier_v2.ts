import * as fs from 'fs';
import * as path from 'path';
import fetch from 'node-fetch'; // Direct fetch or reuse existing service
import { configManager } from "../agent/config_loader";

// Quick interface for Category Node
interface CategoryNode {
    id: number;
    name: string;
    children: CategoryNode[];
}

interface ClassificationResult {
    category_id: number;
    category_path: string;
    confidence: number;
    reasoning: string;
}

export class ClassifierV2 {
    private categories: CategoryNode[] = [];
    private llmUrl: string = configManager.getLLMConfig().baseUrl;
    private modelName: string = configManager.getLLMConfig().model;

    constructor() {
        this.loadCategories();
    }

    private loadCategories() {
        try {
            const filePath = path.join(process.cwd(), 'src/agent/config/categories_list.json');
            const data = fs.readFileSync(filePath, 'utf-8');
            const rawCategories: CategoryNode[] = JSON.parse(data);

            // Merge duplicate roots by name
            const mergedMap = new Map<string, CategoryNode>();

            rawCategories.forEach(cat => {
                if (mergedMap.has(cat.name)) {
                    const existing = mergedMap.get(cat.name)!;
                    // Merge children
                    existing.children = [...existing.children, ...cat.children];
                    // Keep the ID of the one with more children or lower ID? 
                    // Let's keep the one that already had children if possible.
                    if (cat.children.length > existing.children.length && existing.children.length === 0) {
                        existing.id = cat.id; // Switch ID if the new one is the "real" one
                    }
                } else {
                    mergedMap.set(cat.name, cat);
                }
            });

            this.categories = Array.from(mergedMap.values());
            console.log(`[ClassifierV2] Loaded ${this.categories.length} unique root domains (merged from ${rawCategories.length}).`);
        } catch (e) {
            console.warn("[ClassifierV2] Failed to load categories:", e);
        }
    }

    async classify(userInput: string): Promise<ClassificationResult> {
        // Step 1: Root Classification
        const rootOptions = this.categories.map(c => {
            let hint = "";
            if (c.name === "DTIC") hint = " (Hardware, Equipamentos, Perifericos, Mouse, Teclado, Monitor, Rede, Infraestrutura, Wifi)";
            if (c.name === "ACESSO A SISTEMAS") hint = " (Login, Senha, Permissões, VPN, Email, SOE, FPE, PROA, Tunnel)";
            if (c.name === "IMPRESSORA") hint = " (Toner, Papel, Atolamento)";
            return `ID ${c.id}: ${c.name}${hint}`;
        }).join('\n');
        const rootSystemPrompt = `You are a Triage Specialist. Classify the user request into one of the following HIGH-LEVEL DOMAINS.
Return ONLY a JSON object: {"id": <number>, "reason": "<short string>"}.

DOMAINS:
${rootOptions}`;

        const rootResponse = await this.callLLM(rootSystemPrompt, userInput);
        const rootJson = this.parseJson(rootResponse);

        if (!rootJson || !rootJson.id) {
            return this.fallback();
        }

        const selectedRoot = this.categories.find(c => c.id === rootJson.id);
        if (!selectedRoot) return this.fallback();

        // Step 2: Leaf Classification
        // Flatten children for this root (simple 2-levels deep usually, but let's just take direct children or flatten all descendants)
        // Architecture says "Root -> Children". Let's grab all descendants formatted nicely.
        const leafOptions = this.formatDescendants(selectedRoot);

        if (leafOptions.length === 0) {
            // No children, return root
            return {
                category_id: selectedRoot.id,
                category_path: selectedRoot.name,
                confidence: 0.8,
                reasoning: "Selected root domain directly (no children)."
            };
        }

        const leafSystemPrompt = `You are a Triage Specialist. The user request falls under domain "${selectedRoot.name}".
Select the MOST SPECIFIC Category ID from the list below.
Return ONLY a JSON object: {"id": <number>, "reason": "<short string>"}.

CATEGORIES:
${leafOptions.join('\n')}`;

        const leafResponse = await this.callLLM(leafSystemPrompt, userInput);
        const leafJson = this.parseJson(leafResponse);

        if (!leafJson || !leafJson.id) {
            return {
                category_id: selectedRoot.id,
                category_path: selectedRoot.name,
                confidence: 0.5,
                reasoning: "Fallback to root domain after failed leaf classification."
            };
        }

        return {
            category_id: leafJson.id,
            category_path: `ID ${leafJson.id}`, // We could lookup name but ID is enough for GLPI
            confidence: 0.9,
            reasoning: leafJson.reason || "AI Logic"
        };
    }

    private formatDescendants(node: CategoryNode, prefix = ""): string[] {
        let lines: string[] = [];
        if (!node.children || !Array.isArray(node.children)) return lines;

        for (const child of node.children) {
            lines.push(`ID ${child.id}: ${prefix}${child.name}`);
            lines.push(...this.formatDescendants(child, prefix + child.name + " > "));
        }
        return lines;
    }

    private async callLLM(system: string, user: string): Promise<string> {
        const body = {
            model: this.modelName,
            stream: false,
            messages: [
                { role: "system", content: system },
                { role: "user", content: user }
            ],
            options: { temperature: 0 }
        };

        try {
            const res = await fetch(`${this.llmUrl}/api/chat`, {
                method: 'POST',
                body: JSON.stringify(body),
                headers: { 'Content-Type': 'application/json' }
            });
            const data: any = await res.json();
            return data.message?.content || "";
        } catch (e) {
            console.error("LLM Call Failed", e);
            return "";
        }
    }

    private parseJson(text: string): any {
        try {
            const match = text.match(/\{[\s\S]*\}/);
            if (match) return JSON.parse(match[0]);
        } catch (e) { }
        return null;
    }

    private fallback(): ClassificationResult {
        return {
            category_id: 1, // Default General
            category_path: "Default",
            confidence: 0.1,
            reasoning: "Classification failed."
        };
    }
}

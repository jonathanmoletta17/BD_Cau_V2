
import { GlpiClient } from './glpi';

export interface CategoryNode {
    id: number;
    name: string;
    completeName: string;
    level: number;
}

export class TaxonomyService {
    private client: GlpiClient;
    private categories: CategoryNode[] = [];
    private lastFetch: number = 0;
    private CACHE_TTL = 1000 * 60 * 60; // 1 Hour

    constructor(client: GlpiClient) {
        this.client = client;
    }

    /**
     * Ensures categories are loaded into memory.
     */
    async ensureCache() {
        if (this.categories.length > 0 && (Date.now() - this.lastFetch < this.CACHE_TTL)) {
            return;
        }

        console.log('[Taxonomy] Fetching Categories from GLPI...');
        try {
            // Fetch ALL categories (range 0-200 to be safe, or paginate if needed)
            const raw = await this.client.listItems('ITILCategory', '0-200');

            this.categories = raw.map((c: any) => ({
                id: c.id,
                name: c.name,
                completeName: c.completename,
                level: c.level
            }));

            this.lastFetch = Date.now();
            console.log(`[Taxonomy] Loaded ${this.categories.length} categories.`);
        } catch (e) {
            console.error('[Taxonomy] Failed to fetch categories', e);
            // Non-blocking failure, but resolution will fail
        }
    }

    /**
     * Resolves a string (e.g., "IMPRESSORA", "WIFI") to the best matching Category ID.
     */
    async resolveCategory(input: string): Promise<number> {
        await this.ensureCache();

        if (!input) return 0;

        const normalizedInput = input.trim().toUpperCase();

        // 1. Exact Match (Name)
        const exact = this.categories.find(c => c.name.toUpperCase() === normalizedInput);
        if (exact) return exact.id;

        // 2. Exact Match (Complete Name) - e.g. "DTIC > ... > IMPRESSORA"
        const exactComplete = this.categories.find(c => c.completeName.toUpperCase() === normalizedInput);
        if (exactComplete) return exactComplete.id;

        // 3. Contains Match (Prefer Deepest / Specific)
        // Find all categories where name contains input
        const candidates = this.categories.filter(c => c.name.toUpperCase().includes(normalizedInput));

        if (candidates.length > 0) {
            // Sort by Level Descending (Deepest first)
            candidates.sort((a, b) => b.level - a.level);

            const bestMatch = candidates[0];
            console.log(`[Taxonomy] Resolved '${input}' to '${bestMatch.completeName}' (ID: ${bestMatch.id}, Level: ${bestMatch.level})`);
            return bestMatch.id;
        }

        // 4. Default Fallback
        return 0; // standard/none
    }

    /**
     * Returns the full list for debugging or frontend dropdowns
     */
    getCategories() {
        return this.categories;
    }
}

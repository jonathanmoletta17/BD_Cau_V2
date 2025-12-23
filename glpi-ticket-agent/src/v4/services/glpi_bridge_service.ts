import axios from 'axios';
import { Redis } from 'ioredis';

interface GLPIEntity {
    id: number;
    name: string;
    completename?: string;
}

interface GLPICategory {
    id: number;
    name: string;
    completename?: string;
}

interface GLPILocation {
    id: number;
    name: string;
    completename?: string;
}

/**
 * Ponte TypeScript para a API do GLPI
 * Busca metadados dinâmicos (categorias, entidades, localizações)
 * com cache em Redis para performance.
 */
export class GLPIBridgeService {
    private sessionToken: string | null = null;
    private readonly CACHE_TTL = 600; // 10 minutos

    constructor(
        private baseUrl: string,
        private appToken: string,
        private userToken: string,
        private redis: Redis
    ) {
        this.baseUrl = baseUrl.replace(/\/$/, ''); // Remove trailing slash
    }

    /**
     * Inicializa sessão com GLPI
     */
    private async initSession(): Promise<void> {
        const url = `${this.baseUrl}/initSession`;
        const response = await axios.get(url, {
            headers: {
                'App-Token': this.appToken,
                'Authorization': `user_token ${this.userToken}`
            }
        });

        this.sessionToken = response.data.session_token;
        console.log('[GLPIBridge] Sessão iniciada');
    }

    /**
     * Faz requisição autenticada ao GLPI
     */
    private async request<T>(endpoint: string, params?: any): Promise<T> {
        if (!this.sessionToken) await this.initSession();

        const url = `${this.baseUrl}/${endpoint}`;
        const response = await axios.get(url, {
            headers: {
                'App-Token': this.appToken,
                'Session-Token': this.sessionToken!,
                'Content-Type': 'application/json'
            },
            params
        });

        return response.data;
    }

    /**
     * Busca todas as páginas de um recurso
     */
    private async getAllPages<T>(endpoint: string): Promise<T[]> {
        const allItems: T[] = [];
        let start = 0;
        const limit = 1000;

        while (true) {
            const range = `${start}-${start + limit - 1}`;
            try {
                const items = await this.request<T[]>(endpoint, { range });
                if (!items || items.length === 0) break;

                allItems.push(...items);
                if (items.length < limit) break;
                start += limit;
            } catch (error: any) {
                if (error.response?.status === 416) break; // Range exceed
                throw error;
            }
        }

        return allItems;
    }

    /**
     * Busca todas as categorias ITIL (com cache)
     */
    async getCategories(): Promise<GLPICategory[]> {
        const cacheKey = 'glpi:categories';
        const cached = await this.redis.get(cacheKey);

        if (cached) {
            console.log('[GLPIBridge] Categorias do cache');
            return JSON.parse(cached);
        }

        console.log('[GLPIBridge] Buscando categorias da API...');
        const categories = await this.getAllPages<GLPICategory>('ITILCategory');

        await this.redis.set(cacheKey, JSON.stringify(categories), 'EX', this.CACHE_TTL);
        return categories;
    }

    /**
     * Busca todas as entidades (com cache)
     */
    async getEntities(): Promise<GLPIEntity[]> {
        const cacheKey = 'glpi:entities';
        const cached = await this.redis.get(cacheKey);

        if (cached) {
            console.log('[GLPIBridge] Entidades do cache');
            return JSON.parse(cached);
        }

        console.log('[GLPIBridge] Buscando entidades da API...');
        const entities = await this.getAllPages<GLPIEntity>('Entity');

        await this.redis.set(cacheKey, JSON.stringify(entities), 'EX', this.CACHE_TTL);
        return entities;
    }

    /**
     * Busca todas as localizações (com cache)
     */
    async getLocations(): Promise<GLPILocation[]> {
        const cacheKey = 'glpi:locations';
        const cached = await this.redis.get(cacheKey);

        if (cached) {
            console.log('[GLPIBridge] Localizações do cache');
            return JSON.parse(cached);
        }

        console.log('[GLPIBridge] Buscando localizações da API...');
        const locations = await this.getAllPages<GLPILocation>('Location');

        await this.redis.set(cacheKey, JSON.stringify(locations), 'EX', this.CACHE_TTL);
        return locations;
    }

    /**
     * Busca entidade por nome (fuzzy match)
     */
    async searchEntity(name: string): Promise<GLPIEntity | null> {
        const entities = await this.getEntities();
        const normalized = name.toLowerCase().trim();

        // Procura match exato primeiro
        let match = entities.find(e =>
            e.name.toLowerCase() === normalized ||
            e.completename?.toLowerCase() === normalized
        );

        // Fallback: match parcial
        if (!match) {
            match = entities.find(e =>
                e.name.toLowerCase().includes(normalized) ||
                e.completename?.toLowerCase().includes(normalized)
            );
        }

        return match || null;
    }

    /**
     * Busca categoria por descrição (fuzzy match)
     */
    async searchCategory(description: string): Promise<GLPICategory | null> {
        const categories = await this.getCategories();
        const normalized = description.toLowerCase().trim();

        // Procura keywords relevantes
        const keywords = ['impressora', 'software', 'rede', 'acesso', 'hardware'];
        const relevantKeyword = keywords.find(k => normalized.includes(k));

        if (relevantKeyword) {
            const match = categories.find(c =>
                c.name.toLowerCase().includes(relevantKeyword) ||
                c.completename?.toLowerCase().includes(relevantKeyword)
            );
            if (match) return match;
        }

        // Fallback: primeira categoria que contenha a descrição
        return categories.find(c =>
            c.name.toLowerCase().includes(normalized) ||
            c.completename?.toLowerCase().includes(normalized)
        ) || null;
    }

    /**
     * Fecha a sessão GLPI
     */
    async close(): Promise<void> {
        if (!this.sessionToken) return;

        try {
            await axios.get(`${this.baseUrl}/killSession`, {
                headers: {
                    'App-Token': this.appToken,
                    'Session-Token': this.sessionToken
                }
            });
        } catch (error) {
            console.error('[GLPIBridge] Erro ao fechar sessão:', error);
        } finally {
            this.sessionToken = null;
        }
    }
}

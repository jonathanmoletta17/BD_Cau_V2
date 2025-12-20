import fetch, { Response } from 'node-fetch';
import { GlpiConfig } from '../agent/config_loader';

interface GlpiSession {
    session_token: string;
}

export class GlpiClient {
    private config: GlpiConfig;
    private sessionToken: string | null = null;

    constructor(config: GlpiConfig) {
        this.config = config;
    }

    private async request(endpoint: string, method: string, body?: any, queryParams?: Record<string, string>): Promise<any> {
        const url = new URL(`${this.config.url}/${endpoint}`);

        if (queryParams) {
            Object.keys(queryParams).forEach(key => url.searchParams.append(key, queryParams[key]));
        }

        const headers: Record<string, string> = {
            'Content-Type': 'application/json',
            'App-Token': this.config.appToken
        };

        if (this.sessionToken) {
            headers['Session-Token'] = this.sessionToken;
        } else if (endpoint !== 'initSession') {
            await this.initSession();
            if (this.sessionToken) headers['Session-Token'] = this.sessionToken;
        }

        if (endpoint === 'initSession') {
            if (this.config.userToken) {
                headers['Authorization'] = `user_token ${this.config.userToken}`;
            } else if (this.config.username && this.config.password) {
                const encoded = Buffer.from(`${this.config.username}:${this.config.password}`).toString('base64');
                headers['Authorization'] = `Basic ${encoded}`;
            } else {
                throw new Error("GLPI Client Error: No valid credentials provided (userToken or username/password required)");
            }
        }

        const options: any = {
            method,
            headers,
        };

        if (body) {
            options.body = JSON.stringify(body);
        }

        console.log(`[GLPI] ${method} ${url.toString()}`);
        const response = await fetch(url.toString(), options);

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`GLPI API Error (${response.status}): ${errorText}`);
        }

        return response.json();
    }

    async initSession(): Promise<void> {
        console.log('[GLPI] Initializing session...');
        try {
            const data = await this.request('initSession', 'GET');
            this.sessionToken = data.session_token;
            console.log('[GLPI] Session initialized:', this.sessionToken);
        } catch (error) {
            console.error('[GLPI] Failed to init session:', error);
            throw error;
        }
    }

    async killSession(): Promise<void> {
        if (!this.sessionToken) return;
        try {
            await this.request('killSession', 'GET');
            this.sessionToken = null;
            console.log('[GLPI] Session killed');
        } catch (error) {
            console.warn('[GLPI] Error killing session:', error);
        }
    }

    async listItems(itemType: string, range: string = "0-50"): Promise<any[]> {
        return this.request(itemType, 'GET', undefined, { range });
    }

    async createTicket(title: string, content: string, urgency: number = 3): Promise<any> {
        if (this.config.isReadOnly) {
            throw new Error("Cannot create ticket in Read-Only mode");
        }

        const payload = {
            input: {
                name: title,
                content: content,
                urgency: urgency
            }
        };

        return this.request('Ticket', 'POST', payload);
    }

    // Helper to get raw search options (to find ID mappings)
    async listSearchOptions(itemType: string): Promise<any> {
        return this.request(`listSearchOptions/${itemType}`, 'GET');
    }
}

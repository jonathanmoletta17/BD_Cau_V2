import fetch, { Response } from 'node-fetch';
import { GlpiConfig } from '../config';

interface GlpiSession {
    session_token: string;
}

export interface CreateTicketPayload {
    title: string;
    content: string;
    urgency?: number;
    _users_id_requester?: number;
    itilcategories_id?: number;
    locations_id?: number;
    [key: string]: any; // Allow other fields
}

export class GlpiClient {
    private config: GlpiConfig;
    private sessionToken: string | null = null;

    constructor(config: GlpiConfig) {
        this.config = config;
    }

    public async request(endpoint: string, method: string = 'GET', payload: any = null, sessionToken?: string): Promise<any> {
        let url = new URL(`${this.config.url}/${endpoint}`);

        const options: any = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'App-Token': this.config.appToken
            }
        };

        // Session Token Priority: Function Arg > Class Property > Auto-Init
        const activeToken = sessionToken || this.sessionToken;

        if (activeToken) {
            options.headers['Session-Token'] = activeToken;
        } else if (endpoint !== 'initSession') {
            await this.initSession();
            // Assuming initSession populates 'this.sessionToken'
            if (this.sessionToken) options.headers['Session-Token'] = this.sessionToken;
        }

        if (endpoint === 'initSession') {
            if (this.config.userToken) {
                options.headers['Authorization'] = `user_token ${this.config.userToken}`;
            } else {
                throw new Error("GLPI Client Error: No valid credentials provided");
            }
        }

        if (payload) {
            if (method.toUpperCase() === 'GET') {
                // GLPI Criteria requires nested keys like criteria[0][field]=1
                // URLSearchParams does not support this depth natively.
                // We implement a simple flattener.
                const buildParams = (data: any, prefix: string = ""): string[] => {
                    const parts: string[] = [];
                    for (const key in data) {
                        if (data.hasOwnProperty(key)) {
                            const value = data[key];
                            const pfx = prefix ? `${prefix}[${key}]` : key;
                            if (value !== null && typeof value === "object") {
                                parts.push(...buildParams(value, pfx));
                            } else {
                                parts.push(`${encodeURIComponent(pfx)}=${encodeURIComponent(value)}`);
                            }
                        }
                    }
                    return parts;
                };

                const queryString = buildParams(payload).join("&");
                url.search = queryString;
            } else {
                options.body = JSON.stringify(payload);
            }
        }

        console.log(`[GLPI] ${method} ${url.toString()}`);
        const response = await fetch(url.toString(), options);

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`GLPI API Error (${response.status}): ${errorText}`);
        }

        const responseText = await response.text();

        // Handle Empty Body with Success Status (GLPI Quirk)
        if (!responseText && response.ok) {
            console.log(`[GLPI] Warning: Received empty body with status ${response.status}. Treating as success.`);
            return { message: "Success (Empty Body)" };
        }

        try {
            return JSON.parse(responseText);
        } catch (e) {
            console.error(`[GLPI] Failed to parse JSON. Status: ${response.status}`);
            console.error(`[GLPI] Raw Body: ${responseText.slice(0, 500)}...`);
            throw new Error(`Invalid JSON response from GLPI: ${responseText.slice(0, 100)}`);
        }
    }

    async initSession(): Promise<void> {
        console.log('[GLPI] Initializing System session...');
        try {
            const data = await this.request('initSession', 'GET');
            this.sessionToken = data.session_token;
            console.log('[GLPI] System Session initialized:', this.sessionToken);
        } catch (error) {
            console.error('[GLPI] Failed to init session:', error);
            throw error;
        }
    }

    /**
     * Authenticates a real user and returns a specific session token.
     * Use this token for subsequent requests on behalf of this user.
     * Authenticates a real user and returns a specific session token AND user ID.
     * Use this token for subsequent requests on behalf of this user.
     */
    async login(username: string, password: string): Promise<{ token: string; userId: number }> {
        console.log(`[GLPI] Authenticating user: ${username}`);
        const url = `${this.config.url}/initSession`;

        const basicAuth = Buffer.from(`${username}:${password}`).toString('base64');
        const headers = {
            'Content-Type': 'application/json',
            'App-Token': this.config.appToken,
            'Authorization': `Basic ${basicAuth}`
        };

        const response = await fetch(url, {
            method: 'GET',
            headers: headers
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Authentication Failed (${response.status}): ${errorText}`);
        }

        const data = await response.json();

        // DEBUG: Dump keys to find ID
        // console.log("[GLPI] initSession Raw Keys:", Object.keys(data));
        if (data.session) console.log("[GLPI] initSession.session Keys:", Object.keys(data.session));

        // Try multiple paths
        // If ID is missing, fetch full session
        let userId = data.session?.glpiID || data.session?.user?.id || data.id;

        if (!userId) {
            console.log("[GLPI] User ID not in initSession. Fetching full session...");
            // Use the new token to get session details
            const fullSession = await this.request('getFullSession', 'GET', null, data.session_token);
            userId = fullSession.session?.glpiID || fullSession.session?.user?.id;
            console.log(`[GLPI] Fetched ID override: ${userId}`);
        }

        console.log(`[GLPI] User ${username} authenticated. Token: ${data.session_token} | ID: ${userId}`);
        return { token: data.session_token, userId: userId };
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
        return this.request(itemType, 'GET', { range });
    }

    async createTicket(payload: CreateTicketPayload, sessionToken?: string): Promise<any> {
        if (this.config.isReadOnly) {
            throw new Error("Cannot create ticket in Read-Only mode");
        }

        // Destructure known fields to avoid duplication when spreading 'rest'
        const { title, content, urgency, ...rest } = payload;

        const requestPayload: any = {
            input: {
                name: title,
                content: content,
                urgency: urgency || 3,
                ...rest // Spread only the remaining fields
            }
        };

        return this.request('Ticket', 'POST', requestPayload, sessionToken);
    }

    // Helper to get raw search options (to find ID mappings)
    async listSearchOptions(itemType: string): Promise<any> {
        return this.request(`listSearchOptions/${itemType}`, 'GET');
    }
}

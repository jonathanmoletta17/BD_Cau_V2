
import { GlpiClient } from './glpi';
import { configManager } from '../config';

export class AuthService {
    private client: GlpiClient;

    constructor() {
        this.client = new GlpiClient(configManager.getGlpiConfig());
    }

    /**
     * Authenticates a user against GLPI and returns the session token.
     */
    async login(username: string, password: string): Promise<{ token: string; userId: number }> {
        return await this.client.login(username, password);
    }
}

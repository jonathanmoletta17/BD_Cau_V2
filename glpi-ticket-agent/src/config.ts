
import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';

// ESM compatible __dirname
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Load env vars
dotenv.config({ path: path.resolve(__dirname, '../../.env') });

export interface LLMConfig {
  baseUrl: string;
  model: string;
  apiKey: string;
  temperature: number;
}

export interface GlpiConfig {
  url: string;
  userToken?: string;
  appToken: string;
  isReadOnly: boolean;
}

export class ConfigManager {
  private llm: LLMConfig;
  private glpi: GlpiConfig;

  constructor() {
    this.llm = {
      baseUrl: process.env.LLM_BASE_URL || "http://localhost:11434",
      model: process.env.LLM_MODEL_NAME || "llama3",
      apiKey: process.env.LLM_API_KEY || "ollama",
      temperature: 0.1
    };

    // Safety Switch Logic
    const environment = process.env.ENVIRONMENT || 'test';
    const isProd = environment === 'production';

    // In PROD, use PROD vars. In TEST, use TEST vars if available, else fallback to PROD vars (but safe).
    // Based on user's .env structure:
    const url = isProd ? process.env.GLPI_PROD_URL_CONFIG : (process.env.GLPI_TEST_URL || process.env.GLPI_PROD_URL_CONFIG);
    const user = isProd ? process.env.GLPI_PROD_USER_TOKEN : (process.env.GLPI_TEST_USER_TOKEN || process.env.GLPI_PROD_USER_TOKEN);
    const app = isProd ? process.env.GLPI_PROD_APP_TOKEN : (process.env.GLPI_TEST_APP_TOKEN || process.env.GLPI_PROD_APP_TOKEN);

    this.glpi = {
      url: url || "",
      userToken: user || "",
      appToken: app || "",
      // CRITICAL: Force ReadOnly unless explicitly in production
      isReadOnly: !isProd
    };

    console.log(`[Config] Environment: ${environment} | Safety Mode (ReadOnly): ${this.glpi.isReadOnly}`);
  }

  getLLMConfig() { return this.llm; }
  getGlpiConfig() { return this.glpi; }
}

export const configManager = new ConfigManager();

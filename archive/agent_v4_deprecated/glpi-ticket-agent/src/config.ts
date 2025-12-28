
import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';

// ESM compatible __dirname
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Load env vars
dotenv.config({ path: path.resolve(__dirname, '../../.env') });

export interface LLMProviderConfig {
  baseUrl: string;
  model: string;
  apiKey?: string;
}

export interface LLMConfig {
  nim: LLMProviderConfig;
  ollama: LLMProviderConfig;
  fallbackEnabled: boolean;
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
    // LLM Configuration - Dual Provider (NIM + Ollama)
    this.llm = {
      nim: {
        baseUrl: process.env.LLM_NIM_URL || 'http://nim-llm:8000',
        model: process.env.LLM_NIM_MODEL || 'meta/llama-3.1-8b-instruct',
        apiKey: process.env.NGC_API_KEY
      },
      ollama: {
        baseUrl: process.env.LLM_OLLAMA_URL || process.env.LLM_BASE_URL || 'http://ollama:11434',
        model: process.env.LLM_OLLAMA_MODEL || process.env.LLM_MODEL_NAME || 'llama3.1',
        apiKey: 'ollama' // Ollama doesn't use API keys
      },
      fallbackEnabled: process.env.LLM_FALLBACK_ENABLED !== 'false', // Default: true
      temperature: parseFloat(process.env.LLM_TEMPERATURE || '0.1')
    };

    console.log('[Config] LLM Providers:');
    console.log(`  - NIM: ${this.llm.nim.baseUrl} (model: ${this.llm.nim.model})`);
    console.log(`  - Ollama: ${this.llm.ollama.baseUrl} (model: ${this.llm.ollama.model})`);
    console.log(`  - Fallback Enabled: ${this.llm.fallbackEnabled}`);

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

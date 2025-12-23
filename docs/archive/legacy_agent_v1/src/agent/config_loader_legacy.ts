import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';

// ESM compatible __dirname
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Try to load from root .env if local doesn't exist
dotenv.config({ path: path.resolve(__dirname, '../../../../.env') });

import intentsConfig from "./config/intents.json";
import schemasConfig from "./config/schemas.json";
import policiesConfig from "./config/policies.json";
import inferenceRulesConfig from "./config/inference_rules.json";
import inquiryTemplatesConfig from "./config/inquiry_templates.json";

export interface IntentConfig {
  id: string;
  keywords: string[];
  excludeKeywords?: string[];
  conditionalKeywords?: Record<string, string[]>;
  priority: number;
  schema: string;
  description: string;
}

export interface SchemaConfig {
  required: string[];
  optional?: string[];
  conditionalRequired?: Record<string, Record<string, string[]>>;
  inferred?: string[];
  defaults?: Record<string, string>;
  description: string;
}

export interface LLMConfig {
  baseUrl: string;
  model: string;
  apiKey: string;
  temperature: number;
}

export interface GlpiConfig {
  url: string;
  userToken?: string;
  username?: string;
  password?: string;
  appToken: string;
  isReadOnly: boolean;
}

export interface ConfigLoader {
  intents: IntentConfig[];
  schemas: Record<string, SchemaConfig>;
  policies: Record<string, any>;
  inferenceRules: Record<string, any>;
  inquiryTemplates: Record<string, string>;
  llm: LLMConfig;
  glpi: GlpiConfig;
}

export class ConfigManager {
  private config: ConfigLoader;

  constructor() {
    this.config = {
      intents: intentsConfig.intents,
      schemas: schemasConfig.schemas,
      policies: policiesConfig.policies,
      inferenceRules: inferenceRulesConfig,
      inquiryTemplates: inquiryTemplatesConfig.questions,
      llm: {
        baseUrl: process.env.LLM_BASE_URL || "http://localhost:11434",
        model: process.env.LLM_MODEL_NAME || process.env.LLM_MODEL || "llama3",
        apiKey: process.env.LLM_API_KEY || "ollama",
        temperature: 0.1
      },
      glpi: {
        url: process.env.GLPI_PROD_URL_CONFIG || "",
        userToken: process.env.GLPI_PROD_USER_TOKEN,
        appToken: process.env.GLPI_PROD_APP_TOKEN || "",
        isReadOnly: true // Default to true for safety
      }
    };
  }

  getIntents(): IntentConfig[] {
    return this.config.intents.sort((a, b) => b.priority - a.priority);
  }

  getIntentById(id: string): IntentConfig | undefined {
    return this.config.intents.find(i => i.id === id);
  }

  getSchema(schemaName: string): SchemaConfig | undefined {
    return this.config.schemas[schemaName];
  }

  getPolicies(): Record<string, any> {
    return this.config.policies;
  }

  getInferenceRules(intent: string): Record<string, any> {
    // Try exact match, then lowercase (since json keys are snake_case/lowercase)
    return this.config.inferenceRules[intent] || this.config.inferenceRules[intent.toLowerCase()] || {};
  }

  getQuestion(fieldName: string): string {
    return this.config.inquiryTemplates[fieldName] || `Por favor, forneça: ${fieldName}`;
  }

  getLLMConfig(): LLMConfig {
    return this.config.llm;
  }

  getGlpiConfig(): GlpiConfig {
    return this.config.glpi;
  }
}

export const configManager = new ConfigManager();

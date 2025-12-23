/**
 * Intent Validation Module
 * 
 * Defines completeness rules for each intent type.
 * Provides deterministic validation without LLM inference.
 */

import { FlowData } from './types';

// Intent Requirements Definition
export interface IntentRequirements {
    intent: string;
    requiredFields: (keyof FlowData)[];
    optionalFields?: (keyof FlowData)[];
    completionRules?: (data: FlowData) => boolean;
}

// Mapping of Intent → Required Fields
export const INTENT_REQUIREMENTS: Record<string, IntentRequirements> = {
    'PRINTER_ISSUE': {
        intent: 'PRINTER_ISSUE',
        requiredFields: ['location', 'extension', 'category', 'description'],
        optionalFields: ['printerName'],
        completionRules: (data: FlowData) => {
            // For printer issues, the 4 core fields are sufficient
            return !!(
                data.location &&
                data.extension &&
                data.category &&
                data.description
            );
        }
    },

    'RESET_PASSWORD': {
        intent: 'RESET_PASSWORD',
        requiredFields: ['location', 'extension', 'targetSystem'],
        completionRules: (data: FlowData) => {
            return !!(
                data.location &&
                data.extension &&
                data.targetSystem
            );
        }
    },

    'NETWORK_ISSUE': {
        intent: 'NETWORK_ISSUE',
        requiredFields: ['location', 'extension', 'category', 'description'],
        completionRules: (data: FlowData) => {
            return !!(
                data.location &&
                data.extension &&
                data.category &&
                data.description
            );
        }
    },

    'EQUIPMENT_REQUEST': {
        intent: 'EQUIPMENT_REQUEST',
        requiredFields: ['location', 'extension', 'description'],
        completionRules: (data: FlowData) => {
            return !!(
                data.location &&
                data.extension &&
                data.description
            );
        }
    },

    'UNKNOWN': {
        intent: 'UNKNOWN',
        requiredFields: ['location', 'extension', 'description'],
        completionRules: (data: FlowData) => {
            // For unknown intents, require basic info
            return !!(
                data.location &&
                data.extension &&
                data.description
            );
        }
    }
};

/**
 * Checks if all required fields for an intent are present.
 * 
 * @param intent - The classified intent type
 * @param data - The current flow data
 * @returns true if all required fields are filled, false otherwise
 */
export function isComplete(intent: string | null, data: FlowData): boolean {
    const requirements = INTENT_REQUIREMENTS[intent || 'UNKNOWN'];

    if (!requirements) {
        console.warn(`[Validator] Unknown intent: ${intent}, using UNKNOWN fallback`);
        return isComplete('UNKNOWN', data);
    }

    // Use custom completion rules if defined
    if (requirements.completionRules) {
        return requirements.completionRules(data);
    }

    // Fallback: check if all required fields are truthy
    return requirements.requiredFields.every(field => !!data[field]);
}

/**
 * Returns a list of missing required fields for an intent.
 * 
 * @param intent - The classified intent type
 * @param data - The current flow data
 * @returns Array of field names that are required but missing
 */
export function getMissingFields(intent: string | null, data: FlowData): string[] {
    const requirements = INTENT_REQUIREMENTS[intent || 'UNKNOWN'];

    if (!requirements) {
        console.warn(`[Validator] Unknown intent: ${intent}, using UNKNOWN fallback`);
        return getMissingFields('UNKNOWN', data);
    }

    return requirements.requiredFields.filter(field => !data[field]) as string[];
}

/**
 * Gets human-friendly labels for field names.
 * Used for generating prompts and user messages.
 */
export const FIELD_LABELS: Record<string, string> = {
    'location': 'sua localização (sala/setor)',
    'extension': 'seu ramal',
    'category': 'o tipo de problema',
    'description': 'uma descrição do problema',
    'targetSystem': 'qual sistema (Rede/Email/ERP)',
    'printerName': 'o nome/modelo da impressora'
};

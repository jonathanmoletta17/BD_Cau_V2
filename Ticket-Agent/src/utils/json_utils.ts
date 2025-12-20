import { jsonrepair } from 'jsonrepair';

/**
 * Safely parses a JSON string, attempting to repair it if it's malformed.
 * This is useful for handling LLM outputs which may contain trailing commas,
 * unquoted keys, or other common JSON errors.
 */
export function safeJsonParse<T = any>(jsonString: string): T | null {
    try {
        // First try standard parse
        return JSON.parse(jsonString);
    } catch (e) {
        try {
            // Try to repair
            const repaired = jsonrepair(jsonString);
            return JSON.parse(repaired);
        } catch (repairError) {
            console.error('[SafeJsonParse] Failed to parse JSON even after repair:', repairError);
            return null;
        }
    }
}

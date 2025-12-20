import { type IntentType } from "./schema";
import { configManager } from "./config_loader";
import { llmService } from "../services/llm_service";

export class ExtractorConfigDriven {
  async extract(text: string, intent: IntentType, currentPayload: any = {}, focusedField?: string): Promise<any> {
    const lower = text.toLowerCase();
    let payload = { ...currentPayload };
    const schema = configManager.getSchema(
      configManager.getIntentById(intent)?.schema || ""
    );

    if (!schema) return payload;

    // 1. Contextual "Focus" Fill (simple heuristics)
    if (focusedField && text.trim().length > 0) {
      console.log(`[Extractor] Contextual fill for field: ${focusedField} with value: "${text}"`);
      let cleanValue = text.trim();

      if (focusedField === 'quantity') {
        const num = parseInt(cleanValue.replace(/[^0-9]/g, ''));
        if (!isNaN(num)) payload[focusedField] = num;
      } else {
        payload[focusedField] = cleanValue;
      }
    }

    // 2. Rule-Based Inference (Legacy/Fast)
    const inferenceRules = configManager.getInferenceRules(intent);

    // ... (Keep existing rule-based logic to maintain deterministic behavior where possible)
    // For brevity, I am keeping the logic but delegating to "Smart Extraction" if it fails.
    // Actually, in Vibe Coding, let's keep the legacy rules as a first pass because they are fast and safe.

    // [Legacy Rule Logic - Simplified for readability in this edit]
    // I will preserve the existing switch case structure but run LLM AFTER it if needed.

    // 2. Rule-Based Inference (Generic & Data-Driven)
    // inferenceRules already declared above

    if (inferenceRules) {
      // 2.1 Patterns (Regex for IDs, codes)
      if (inferenceRules.patterns) {
        for (const [field, pattern] of Object.entries(inferenceRules.patterns)) {
          if (payload[field]) continue; // Skip if already filled
          try {
            const regex = new RegExp(pattern as string, 'i');
            const match = text.match(regex);
            if (match) {
              console.log(`[Extractor] Pattern match for ${field}: ${match[0]}`);
              payload[field] = match[0];
            }
          } catch (e) {
            console.error(`[Extractor] Invalid regex pattern for ${field}:`, e);
          }
        }
      }

      // 2.2 Keywords and Defaults
      for (const [field, rules] of Object.entries(inferenceRules)) {
        if (field === 'patterns') continue;
        if (payload[field]) continue; // Skip if already filled

        const fieldRules = rules as any;

        // Keywords Matching
        if (fieldRules.keywords) {
          if (Array.isArray(fieldRules.keywords)) {
            // Simple list (e.g. items) - Set value to the matched keyword itself
            const found = fieldRules.keywords.find((k: string) => lower.includes(k.toLowerCase()));
            if (found) {
              console.log(`[Extractor] Simple keyword match for ${field}: ${found}`);
              payload[field] = found;
            }
          } else {
            // Enum Map (e.g. user_type) - Set value to the mapped key
            for (const [value, kws] of Object.entries(fieldRules.keywords)) {
              if ((kws as string[]).some(k => lower.includes(k.toLowerCase()))) {
                console.log(`[Extractor] Enum keyword match for ${field}: ${value}`);
                payload[field] = value;
                break;
              }
            }
          }
        }

        // Default Value Fallback
        if (!payload[field] && fieldRules.default) {
          console.log(`[Extractor] Applying default for ${field}: ${fieldRules.default}`);
          payload[field] = fieldRules.default;
        }
      }
    }

    // 3. LLM Smart Extraction (The "Brain")
    // If we are missing required fields OR we want to improve quality, call LLM.
    // Logic: If user text is long enough (> 5 words) OR we have missing required fields in the current payload.

    const requiredFields = schema.required;
    const missingFields = requiredFields.filter(f => !payload[f]);

    if (missingFields.length > 0 || text.split(' ').length > 3) {
      console.log(`[Extractor] Invoking LLM for Intent: ${intent}. Missing: ${missingFields.join(', ')}`);

      const description = `Extract the following fields for a '${intent}' request: ${JSON.stringify(schema)}.
        Current known state: ${JSON.stringify(payload)}.
        Only return fields found in the text. Do NOT hallucinate.`;

      const extracted = await llmService.completeJson<any>(
        `Extract data from this support request into JSON: "${text}"`,
        description
      );

      if (extracted) {
        console.log(`[Extractor] LLM found:`, extracted);
        // Merge strategy: Overwrite empty fields, Keep existing (unless focused update?)
        // Safer: Only fill missing fields + special fields like description/reason

        for (const key of Object.keys(extracted)) {
          // If payload doesn't have it, or it's a "description" field (which benefits from LLM summary), take it.
          if (!payload[key] || key === 'description' || key === 'reason') {
            if (extracted[key] && String(extracted[key]).length > 0) {
              payload[key] = extracted[key];
            }
          }
        }
      }
    }

    return payload;
  }
}

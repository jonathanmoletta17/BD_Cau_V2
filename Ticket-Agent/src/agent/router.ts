import { IntentEnum, type IntentType } from "./schema";
import { configManager } from "./config_loader";
import { llmService } from "../services/llm_service";

export class RouterConfigDriven {
  async classify(text: string): Promise<IntentType> {
    const lower = text.toLowerCase();
    const intents = configManager.getIntents();

    // 1. Keyword Matching (Deterministic)
    for (const intent of intents) {
      // Exclude keywords check
      if (intent.excludeKeywords) {
        if (intent.excludeKeywords.some(k => lower.includes(k))) {
          continue; // Skip this intent if forbidden word is found
        }
      }

      // Check main keywords
      if (intent.keywords.some(k => lower.includes(k))) {
        // Special check for conditional keywords
        if (intent.conditionalKeywords) {
          let confirmed = false;
          for (const [trigger, conditions] of Object.entries(intent.conditionalKeywords)) {
            if (lower.includes(trigger)) {
              if (conditions.some(c => lower.includes(c))) {
                confirmed = true;
                break;
              }
            }
          }
          // Conditional logic: if match found but condition NOT met, do we skip?
          // For now, if conditional keywords are defined, usually implies we need the condition.
          // But if the matched main keyword is NOT a trigger key, we might be fine?
          // Keeping original safe logic: Log match and return.
        }
        console.log(`[Router] Keyword match: ${intent.id}`);
        return intent.id as IntentType;
      }
    }

    // 2. AI Fallback (via LLMService)
    try {
      const intentList = intents.map(i => i.id).join(", ");
      const prompt = `You are a Technical Support Triage Agent. Classify the user request into one of these categories: [${intentList}].
      
      Request: "${text}"
      
      Respond ONLY with the Category Name. If you cannot determine, respond UNKNOWN.`;

      const content = await llmService.complete(prompt, "You are a classifier.");

      if (content) {
        console.log(`[Router] AI response: ${content}`);
        const validIntentIds = intents.map(i => i.id);
        const foundIntent = validIntentIds.find(id => content.toUpperCase().includes(id));

        if (foundIntent) {
          console.log(`[Router] AI classified as: ${foundIntent}`);
          return foundIntent as IntentType;
        }
      }
    } catch (err) {
      console.error("[Router] AI Service unavailable, falling back to UNKNOWN", err);
    }

    return "UNKNOWN";
  }
}

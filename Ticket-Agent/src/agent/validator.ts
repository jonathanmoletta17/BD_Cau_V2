import { type IntentType } from "./schema";
import { configManager } from "./config_loader";

export class ValidatorConfigDriven {
  validate(intent: IntentType, payload: any): { is_complete: boolean; missing_fields: string[] } {
    const missing: string[] = [];
    const intentConfig = configManager.getIntentById(intent);
    const schema = intentConfig ? configManager.getSchema(intentConfig.schema) : undefined;

    if (!schema) return { is_complete: false, missing_fields: ["schema_not_found"] };

    // Check required fields
    for (const field of schema.required) {
      if (!payload[field]) {
        missing.push(field);
      }
    }

    // Check conditional requirements
    if (schema.conditionalRequired) {
      for (const [conditionalField, conditions] of Object.entries(schema.conditionalRequired)) {
        const conditionalValue = payload[conditionalField];
        if (conditionalValue && conditions[conditionalValue as string]) {
          const requiredForValue = conditions[conditionalValue as string];
          for (const req of requiredForValue) {
            if (!payload[req]) {
              missing.push(req);
            }
          }
        }
      }
    }

    return {
      is_complete: missing.length === 0,
      missing_fields: missing
    };
  }
}

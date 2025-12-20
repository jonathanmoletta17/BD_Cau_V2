import { RouterConfigDriven } from "./router";
import { ExtractorConfigDriven } from "./extractor";
import { ExtractorV2 } from "../services/extractor_v2"; // Refactored
import { ClassifierV2 } from "../services/classifier_v2"; // Refactored
import { ValidatorV2 } from "../services/validator_v2"; // Strict Rules
import { DocLoader } from "../services/doc_loader"; // V2 Config
import { ValidatorConfigDriven } from "./validator";
import { InquiryConfigDriven } from "./inquiry";
import { type AgentState } from "./schema";
import { configManager } from "./config_loader";
import { PayloadMapper } from "../services/payload_mapper";

export class TriageGraphConfigDriven {
  private router: RouterConfigDriven;
  private extractor: ExtractorConfigDriven;
  private extractorV2: ExtractorV2;
  private classifierV2: ClassifierV2;
  private validator: ValidatorConfigDriven;
  private inquiry: InquiryConfigDriven;
  private readonly MAX_RETRIES: number;

  constructor() {
    this.router = new RouterConfigDriven();
    this.extractor = new ExtractorConfigDriven();
    this.extractorV2 = new ExtractorV2(); // V2 Init
    this.classifierV2 = new ClassifierV2();
    this.validator = new ValidatorConfigDriven();
    this.inquiry = new InquiryConfigDriven();
    this.MAX_RETRIES = configManager.getPolicies().max_retries_per_field || 3;
  }

  private countFieldAttempts(state: AgentState, fieldName: string): number {
    let count = 0;
    for (const msg of state.messages) {
      if (msg.role === "agent" && msg.content.toLowerCase().includes(fieldName.toLowerCase())) {
        count++;
      }
    }
    return count;
  }

  async process(message: string, previousState?: AgentState, systemInfo?: any): Promise<AgentState> {
    let state: AgentState = previousState || {
      intent: "UNKNOWN",
      is_complete: false,
      ticket_payload: {},
      missing_fields: [],
      messages: [],
      pinned_request: message,
      system_info: systemInfo // Initialize if provided
    };

    // If new systemInfo comes in mid-stream (unlikely but possible), update it
    if (systemInfo) {
      state.system_info = systemInfo;
    }

    state.messages.push({ role: "user", content: message });

    // 1. Intent Classification
    if (state.intent === "UNKNOWN") {
      state.intent = await this.router.classify(message);
      state.pinned_request = message;
    }

    if (state.intent === "UNKNOWN") {
      state.messages.push({
        role: "agent",
        content: "Não consegui entender sua solicitação. Poderia reformular? (Ex: 'Esqueci minha senha', 'Novo usuário', 'Meu mouse quebrou')"
      });
      state.diagnostics = "Router failed to classify intent.";
      return state;
    }

    // 2. V2 Doc-Driven Logic (The "New Brain")
    if (DocLoader.hasV2Doc(state.intent)) {
      console.log(`[Graph] Using V2 Engine for intent: ${state.intent}`);

      // Construct History
      const history = state.messages.map(m => `${m.role === 'user' ? 'User' : 'Agent'}: ${m.content}`).join('\n');

      // Call V2 Extractor (Handles Validations & Questions internally)
      const v2Result = await this.extractorV2.extract(state.intent, history);

      if (v2Result.status === 'COMPLETE') {
        // --- STRICT VALIDATION GATE (V2) ---
        // Ensure that even if the LLM thinks it's done, our Code Rules agree.
        const strictValidation = ValidatorV2.validate(state.intent, v2Result.payload);

        if (!strictValidation.valid) {
          // If strict validation fails, we treat it as INCOMPLETE and ask the specific question
          state.is_complete = false;
          state.messages.push({
            role: "agent",
            content: strictValidation.message || "Faltam informações obrigatórias."
          });
          state.diagnostics = `V2 Strict Validation Failed: ${strictValidation.missingField}`;
        } else {
          // Validation Passed
          state.ticket_payload = v2Result.payload; // Full replacement of payload
          state.is_complete = true;

          // --- GLPI INTEGRATION (Simulation) ---
          try {
            // Dynamic Classification (New Step)
            console.log(`[Graph] Classifying category for: "${state.pinned_request || message}"`);
            const classification = await this.classifierV2.classify(state.pinned_request || message);

            const ticketData = PayloadMapper.mapToTicket(
              state.intent,
              state.ticket_payload,
              classification.category_id,
              state.system_info // Pass System Info
            );

            // User Facing Message
            state.messages.push({ role: "agent", content: "✓ Ticket pronto para abertura! (Validado por IA)" });

            // Internal Log Only (Removed from Chat UI)
            console.log(`[Graph] SYSTEM: Mapped to GLPI Ticket: "${ticketData.name}" [CatID: ${ticketData.itilcategories_id}] Reason: ${classification.reasoning}`);

            state.diagnostics = `V2 Validation passed. Ready for GLPI (Cat: ${ticketData.itilcategories_id})`;
          } catch (e: any) {
            state.diagnostics = `V2 Error mapping: ${e.message}`;
            state.is_complete = false; // Fail safe
            state.messages.push({ role: "agent", content: "Erro interno ao processar o ticket." });
          }
          // -------------------------------------
        }
        // INCOMPLETE or ERROR
        state.is_complete = false;
        // If the V2 extractor generates a question, use it.
        if (v2Result.message) {
          state.messages.push({ role: "agent", content: v2Result.message });
        } else {
          // Fallback generic error
          state.messages.push({ role: "agent", content: "Desculpe, tive um erro interno. Pode repetir?" });
        }
      }

      return state;
    }

    // ---------------------------------------------------------
    // Legacy Logic (V1) - Fallback for other intents
    // ---------------------------------------------------------

    // 2. Extraction (Legacy)
    const focusedField = state.missing_fields.length > 0 ? state.missing_fields[0] : undefined;

    if (state.missing_fields.length > 0) {
      // If we are missing fields, we likely asked a question.
      // The current message is likely the answer to that question.
      state.ticket_payload = await this.extractor.extract(message, state.intent, state.ticket_payload, focusedField);
    } else {
      // First pass or spontaneous
      state.ticket_payload = await this.extractor.extract(state.pinned_request || message, state.intent, state.ticket_payload);
      if (state.pinned_request !== message) {
        state.ticket_payload = await this.extractor.extract(message, state.intent, state.ticket_payload);
      }
    }

    // 3. Validation
    const validation = this.validator.validate(state.intent, state.ticket_payload);
    state.is_complete = validation.is_complete;
    state.missing_fields = validation.missing_fields;

    // 4. Inquiry or Finalize
    if (!state.is_complete) {
      const nextField = state.missing_fields[0];
      const attempts = this.countFieldAttempts(state, nextField);

      if (attempts >= this.MAX_RETRIES) {
        const handoverMsg = configManager.getPolicies().handover_message.replace("{retries}", String(this.MAX_RETRIES));
        state.messages.push({ role: "agent", content: handoverMsg });
        state.diagnostics = `HANDOVER: Max retries (${this.MAX_RETRIES}) exceeded for field: ${nextField}`;
        state.is_complete = false;
        return state;
      }

      const question = this.inquiry.generateQuestion(nextField);
      state.messages.push({ role: "agent", content: question });
      state.diagnostics = `Missing: ${state.missing_fields.join(", ")} (attempt ${attempts + 1}/${this.MAX_RETRIES})`;
    } else {
      state.messages.push({ role: "agent", content: "✓ Ticket pronto para abertura!" });
      state.diagnostics = "Validation passed. Payload complete and ready for GLPI integration.";
    }

    return state;
  }
}

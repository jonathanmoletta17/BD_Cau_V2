import { z } from "zod";

// === 1. INTENT DEFINITIONS (DMD v2.1) ===
export const IntentEnum = z.enum([
  "RESET_PASSWORD",
  "CREATE_USER",
  "EQUIPMENT_REQUEST",
  "PRINTER_ISSUE",
  "VPN_ACCESS",
  "CORPORATE_SYSTEMS",
  "UNKNOWN"
]);
export type IntentType = z.infer<typeof IntentEnum>;

// === 2. PAYLOAD SCHEMAS ===

// A. RESET_PASSWORD
export const ResetPasswordSchema = z.object({
  target_system: z.enum(["Rede/Windows", "Office 365", "Email", "Outlook", "SAP", "Other"]).default("Rede/Windows"),
  username: z.string().min(1, "Username is required")
});

// B. CREATE_USER
export const UserTypeEnum = z.enum(["Efetivo", "Estagiário"]);
export const CreateUserSchema = z.object({
  full_name: z.string().min(3),
  department: z.string().min(2),
  user_type: UserTypeEnum,
  // Conditional identifiers (will be validated in Validator logic, but defined here as optional for schema structure)
  cpf: z.string().optional(),       // Required if Efetivo
  rg: z.string().optional(),        // Required if Estagiário
  matricula: z.string().optional(), // Required if Efetivo
  start_date: z.string().optional() // Non-blocking
});

// C. EQUIPMENT_REQUEST
export const RequestTypeEnum = z.enum(["Incident", "Requisition"]);
export const EquipmentRequestSchema = z.object({
  request_type: RequestTypeEnum,
  // Incident specific
  description: z.string().optional(),
  // Requisition specific
  item: z.string().optional(),
  quantity: z.coerce.number().default(1),
  reason: z.string().optional()
});

// D. PRINTER_ISSUE
export const PrinterIssueSchema = z.object({
  description: z.string().min(3),
  // Prohibited: IP, Queue, Patrimony requests
  printer_reference: z.string().optional() // Informal reference
});

// E. VPN_ACCESS
export const VpnAccessSchema = z.object({
  action: z.enum(["Grant_Access", "Install_Client"]).default("Grant_Access"),
  justification: z.string().optional(),
  // User must exist
  existing_username: z.string().min(1)
});

// F. CORPORATE_SYSTEMS
export const CorporateSystemsSchema = z.object({
  system_name: z.string().min(1),
  error_message: z.string().min(1)
});

// Union of all possible payloads
export const TicketPayloadSchema = z.union([
  ResetPasswordSchema,
  CreateUserSchema,
  EquipmentRequestSchema,
  PrinterIssueSchema,
  VpnAccessSchema,

  CorporateSystemsSchema,
  z.object({}) // For UNKNOWN or empty
]);

// === 3. AGENT STATE/OUTPUT CONTRACT ===
export const AgentStateSchema = z.object({
  intent: IntentEnum,
  is_complete: z.boolean(),
  ticket_payload: z.record(z.any()), // Loose validation here, strict in core
  missing_fields: z.array(z.string()),
  diagnostics: z.string().nullable().optional(),
  // Internal context
  pinned_request: z.string().optional(), // Original request
  messages: z.array(z.object({
    role: z.enum(["user", "agent", "system"]),
    content: z.string()
  })).default([]),
  system_info: z.record(z.any()).optional()
});

export type AgentState = z.infer<typeof AgentStateSchema>;

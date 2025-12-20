
# Diagnostic Report: Frontend Integration Failure

## 1. Problem Description
The user experienced `400 Bad Request` errors when interacting with the web interface.
**Error Log:**
```
ApiError: {"error":{"code":400,"message":"API key not valid..."}}
Failed to load resource: generativelanguage.googleapis.com...
```

## 2. Root Cause Analysis
Upon "exhaustive study" of the source code (`frontend/index.tsx`), the following critical architectural mismatch was identified:

*   **Current State**: The frontend is implemented as a **Standalone Client-Side AI App**.
    *   It imports `@google/genai` directly in the browser.
    *   It attempts to instantiate `GoogleGenAI` with `process.env.API_KEY`.
    *   It communicates directly with Google's servers (`generativelanguage.googleapis.com`).
*   **Desired State**: The frontend should be a **Thin Client** for the **Ticket Agent V2 Backend**.
    *   The Backend (Node.js/Express) is running on port 8000/8001.
    *   The Backend handles the LLM logic (via NVIDIA NIM/Llama 3.2).
    *   The Frontend should merely send user input to `POST /chat` and render the response and state returned by the server.

**Why it failed**:
1.  The frontend ignores the backend entirely.
2.  It fails to authenticate with Google because no valid Gemini API Key was provided to the *frontend* build environment.
3.  Even if it had a key, it would be using the wrong model (Gemini) instead of the project standard (Llama 3.2 via NIM).

## 3. Detailed Failure Points
*   **Line 112 (`index.tsx`)**: `const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });` - This line initializes the direct connection to Google.
*   **Line 143 (`index.tsx`)**: `chat.sendMessage(...)` - This bypasses the custom Agent Graph logic (Routing, Extraction, Validation) residing in the container.
*   **Function Calls**: The frontend attempts to run `updateTicketDraft` locally on the client, whereas the V2 Agent calculates the `ticket_payload` on the server.

## 4. Remediation Plan
To fix this and integrate the system correctly:
1.  **Refactor `index.tsx`**:
    *   Remove all `@google/genai` code.
    *   Replace `sendMessage` with a `fetch('/chat', ...)` call to the local backend.
    *   Map the backend's `state.ticket_payload` response to the frontend's `ticket` state variable to update the live preview.
2.  **Rebuild**:
    *   Recompile the frontend bundle.
    *   Restart the container.

# Research Report: Automated Data Sanitization

## 1. Context
The user has a dataset with noisy labels (Human "Laziness") and a high-performing model (Agent). Manual review is inefficient. We need an automated way to "clean" the dataset using the model's confidence.

## 2. Methodologies Researched

### A. Cleanlab (Confident Learning) - **RECOMMENDED**
*   **What it is**: A standard library for finding label errors in datasets.
*   **How it works**: It uses the model's predicted probabilities (`predict_proba`) vs the given label. It calculates "Confident Joint" distribution to find off-diagonal elements (where the model is confidently wrong relative to the label, or the label is confidently wrong relative to the model).
*   **Why it fits**: We essentially have this scenario. The Agent is "Confident" in `Printer`, but the Label is `Support`. Cleanlab is mathematically designed to detect this specific type of noise.
*   **Pros**: Python library, fast, statistically sound, no extra LLM costs.
*   **Cons**: Requires probabilities (which we have from cosine similarity scores).

### B. LLM-as-a-Judge
*   **What it is**: Sending `(Text, Label A, Label B)` to GPT-4 or Gemini.
*   **Pros**: Easy to understand, handles semantic nuances better than pure stats.
*   **Cons**: Slow, costs money/tokens, might hallucinate if not prompted perfectly.

### C. Snorkel (Weak Supervision)
*   **What it is**: Writing labeling functions (heuristics) to generate labels.
*   **Why reject**: We effectively already *have* a strong labeling function (our embedding agent). Snorkel is for *combining* many weak functions.

## 3. Proposal: Hybrid "Smart Audit"
We should implement a **Cleanlab-inspired** pipeline using our existing Agent's confidence scores.

### Algorithm
1.  **Get Scores**: For each ticket, get cosine similarity scores for *all* categories.
2.  **Filter**: Identify tickets where `Model Confidence > Threshold` AND `Model Category != Human Category`.
3.  **Action**:
    *   If `Model Confidence > 0.85` (High): **Auto-Accept Agent Label** (The "Generalist Problem" fix).
    *   If `Model Confidence < 0.85`: Flag for Manual Review (Keep existing Streamlit app for these few edge cases).

This mimics Cleanlab's "Pruning" strategy but tailored to our specific "Generic vs Specific" hierarchy problem.

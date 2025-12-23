# Universal Prompt: Protocol for Controlled Refactoring

## Context
We are in a **Critical Stability Phase**. We cannot afford regressions. We are adopting a "Micro-Surgery" approach to refactoring.

## Strict Rules of Engagement

### 1. The Scope of One
*   You may only touch **ONE** architectural concept at a time (e.g., "Logging", "Error Handling", "Input Validation").
*   You may NOT refactor adjacent modules "while you are at it".

### 2. The Verification First Principle
*   Before writing code, define the **Test Case** that proves the current flaw.
*   After writing code, prove that ONLY that test case changed status.

### 3. The Refactoring Cycle
1.  **Analyze:** Identify the exact line causing the fragility.
2.  **Isolate:** Can this be fixed without changing the function signature?
    *   *Yes:* Proceed.
    *   *No:* STOP. Request architecture review.
3.  **Implement:** Apply the minimal change.
4.  **Verify:** Run the specific test case.

## Command
Wait for the specific "Invariant" I want you to fix. Do not start until I name the target (e.g., "Fix Context Loss").

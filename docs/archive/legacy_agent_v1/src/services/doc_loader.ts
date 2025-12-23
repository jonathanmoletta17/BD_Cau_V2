import * as fs from 'fs';
import * as path from 'path';

// Mapping of Intent -> Governance Document
const DOC_MAPPING: Record<string, string> = {
    'create_user': '17_AI_OPTIMIZED.md',
    'printer_issue': '20_AI_PRINTER_ISSUE.md',
    'reset_password': '21_AI_RESET_PASSWORD.md',
    'equipment_request': '22_EQUIPMENT_REQUEST.md'
};

export class DocLoader {
    private static docsPath = path.join(process.cwd(), 'archive-docs');

    /**
     * Loads the AI-Optimized Governance Document for a given intent.
     * @param intent The detected user intent.
     * @returns The markdown content of the governance doc.
     */
    static loadDoc(intent: string): string {
        const filename = DOC_MAPPING[intent.toLowerCase()];
        if (!filename) {
            console.warn(`⚠️ No AI Governance Doc found for intent: ${intent}`);
            return ""; // Return empty or a default "Generic IT Support" doc
        }

        try {
            const filePath = path.join(this.docsPath, filename);
            return fs.readFileSync(filePath, 'utf-8');
        } catch (error) {
            console.error(`❌ Failed to load doc ${filename}:`, error);
            return "";
        }
    }

    /**
     * Checks if a V2 doc exists for this intent.
     */
    static hasV2Doc(intent: string): boolean {
        return !!DOC_MAPPING[intent.toLowerCase()];
    }
}

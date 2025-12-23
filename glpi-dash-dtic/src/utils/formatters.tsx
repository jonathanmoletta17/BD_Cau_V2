
import React from 'react';

// Detects if text is likely from GLPI Formcreator
export const isFormCreatorText = (text: string): boolean => {
    return text.includes("Dados do formulário") || text.includes("Dados Gerais");
};

// Parses "1) Question : Answer" pattern
export const parseFormCreatorText = (text: string) => {
    // Remove common headers
    let cleanText = text
        .replace(/Dados do formulário/g, "")
        .replace(/Dados Gerais/g, "")
        .replace(/Detalhamento/g, "");

    // Split by number followed by )
    // Regex: (?:^|\s)(\d+\)) matches " 1)" or start "1)"
    // We use capturing group (\d+\)) so split includes the delimiter.
    const parts = cleanText.split(/(?:^|\s)(\d+\))/);

    const items = [];

    for (let i = 1; i < parts.length; i += 2) {
        const number = parts[i]; // "1)"
        const content = parts[i + 1] || ""; // " Question : Answer "

        // Split content by first colon ":"
        const separatorIndex = content.indexOf(":");
        let question = "";
        let answer = "";

        if (separatorIndex !== -1) {
            question = content.substring(0, separatorIndex).trim();
            answer = content.substring(separatorIndex + 1).trim();
        } else {
            // Fallback if no colon
            question = content.trim();
        }

        if (question || answer) {
            items.push({ number, question, answer });
        }
    }

    return items;
};

export const SmartDescription: React.FC<{ text: string }> = ({ text }) => {
    if (!text) return null;

    if (isFormCreatorText(text)) {
        const items = parseFormCreatorText(text);
        if (items.length > 0) {
            return (
                <div className="space-y-3">
                    {items.map((item, idx) => (
                        <div key={idx} className="bg-slate-800/50 p-3 rounded border border-slate-700/50">
                            <div className="text-xs font-bold text-slate-500 uppercase mb-1">
                                {item.question}
                            </div>
                            <div className="text-sm text-slate-200">
                                {item.answer || <span className="italic text-slate-600">Sem resposta</span>}
                            </div>
                        </div>
                    ))}
                </div>
            );
        }
    }

    // Default rendering for normal text (preserving newlines)
    return (
        <div className="text-sm text-slate-300 whitespace-pre-wrap leading-relaxed font-sans">
            {text}
        </div>
    );
};

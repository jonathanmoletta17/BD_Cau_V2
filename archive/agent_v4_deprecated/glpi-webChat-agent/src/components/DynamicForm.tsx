
import React, { useState } from 'react';
import { FormSchema, FormField } from '../types/chat';

interface DynamicFormProps {
    schema: FormSchema;
    onSubmit: (data: any) => void;
}

export default function DynamicForm({ schema, onSubmit }: DynamicFormProps) {
    // Initialize state with values from schema (pre-filled by AI)
    const [formData, setFormData] = useState<Record<string, any>>(() => {
        const initial: Record<string, any> = {};
        schema.fields.forEach(f => {
            if (f.value) initial[f.id] = f.value;
        });
        return initial;
    });

    const handleChange = (id: string, value: string) => {
        setFormData(prev => ({ ...prev, [id]: value }));
    };

    const handleSubmit = () => {
        onSubmit(formData);
    };

    return (
        <div className="mt-4 bg-white border border-slate-200 rounded-lg p-4 shadow-sm">
            <h3 className="font-semibold text-slate-800 mb-4 border-b border-slate-200 pb-2">
                {schema.title}
            </h3>
            <div className="space-y-4">
                {schema.fields.map((field) => (
                    <div key={field.id} className="flex flex-col gap-1">
                        <label className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                            {field.label} {field.required && <span className="text-red-500">*</span>}
                        </label>

                        {field.type === 'select' ? (
                            <select
                                value={formData[field.id] || ''}
                                onChange={(e) => handleChange(field.id, e.target.value)}
                                className="w-full px-3 py-2 text-sm border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
                            >
                                <option value="">Selecione...</option>
                                {field.options?.map(opt => (
                                    <option key={opt} value={opt}>{opt}</option>
                                ))}
                            </select>
                        ) : (
                            <input
                                type={field.type}
                                value={formData[field.id] || ''}
                                onChange={(e) => handleChange(field.id, e.target.value)}
                                placeholder={field.placeholder}
                                className={`w-full px-3 py-2 text-sm border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors
                                    ${!formData[field.id] && field.required
                                        ? 'border-amber-300 bg-amber-50 focus:border-blue-500 focus:bg-white'
                                        : 'border-slate-300 bg-white'}`}
                            />
                        )}
                    </div>
                ))}
            </div>
            <button
                onClick={handleSubmit}
                className="mt-6 w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2.5 rounded-lg transition-all shadow-sm hover:shadow active:scale-95 text-sm"
            >
                {schema.submitLabel || 'Confirmar e Enviar'}
            </button>
        </div>
    );
}

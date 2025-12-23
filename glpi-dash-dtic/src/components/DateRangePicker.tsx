import React, { useState, useEffect } from 'react';
import { Calendar, Check } from 'lucide-react';

interface DateRangePickerProps {
    startDate: string;
    endDate: string;
    onChange: (start: string, end: string) => void;
}

export const DateRangePicker: React.FC<DateRangePickerProps> = ({
    startDate,
    endDate,
    onChange
}) => {
    const today = new Date().toISOString().split('T')[0];

    // Temporary state for pending changes
    const [tempStart, setTempStart] = useState(startDate);
    const [tempEnd, setTempEnd] = useState(endDate);
    const [hasPendingChanges, setHasPendingChanges] = useState(false);

    // Sync with parent when props change
    useEffect(() => {
        setTempStart(startDate);
        setTempEnd(endDate);
        setHasPendingChanges(false);
    }, [startDate, endDate]);

    const handleStartChange = (value: string) => {
        setTempStart(value);
        setHasPendingChanges(true);
    };

    const handleEndChange = (value: string) => {
        setTempEnd(value);
        setHasPendingChanges(true);
    };

    const handleApply = () => {
        onChange(tempStart, tempEnd);
        setHasPendingChanges(false);
    };

    return (
        <div className="flex items-center gap-2 bg-blue-900/40 px-4 py-2 rounded border border-blue-500/30">
            <Calendar className="w-4 h-4 text-blue-300" />

            <label className="text-xs text-blue-200 whitespace-nowrap">Período:</label>

            <input
                type="date"
                value={tempStart}
                onChange={(e) => handleStartChange(e.target.value)}
                max={tempEnd}
                className="bg-transparent text-sm font-medium border-none focus:outline-none focus:ring-0 cursor-pointer text-white date-input"
                title="Data inicial"
            />

            <span className="text-slate-400">→</span>

            <input
                type="date"
                value={tempEnd}
                onChange={(e) => handleEndChange(e.target.value)}
                min={tempStart}
                max={today}
                className="bg-transparent text-sm font-medium border-none focus:outline-none focus:ring-0 cursor-pointer text-white date-input"
                title="Data final"
            />

            <button
                onClick={handleApply}
                disabled={!hasPendingChanges}
                className={`ml-2 px-3 py-1.5 rounded text-xs font-semibold flex items-center gap-1.5 transition-all ${hasPendingChanges ? 'bg-blue-600 text-white hover:bg-blue-500 cursor-pointer shadow-md' : 'bg-slate-700/50 text-slate-500 cursor-not-allowed'}`}
                title={hasPendingChanges ? "Clique para aplicar o filtro" : "Selecione as datas primeiro"}
            >
                <Check className="w-3.5 h-3.5" />
                Aplicar
            </button>
        </div>
    );
};

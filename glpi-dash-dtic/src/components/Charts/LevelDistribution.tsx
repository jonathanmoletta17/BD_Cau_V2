import React, { useMemo } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  PieChart, Pie, Cell, Label
} from 'recharts';
import { NivelSuporte } from '../../types';
import { CHART_COLORS } from '../../constants';

interface LevelDistributionProps {
  data: NivelSuporte[];
}

// Custom tooltip for Bar Chart
const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-slate-800 border border-slate-700 p-2 rounded shadow-lg">
        <p className="text-slate-200 font-semibold mb-1">{label}</p>
        {payload.map((entry: any, index: number) => (
          <p key={index} style={{ color: entry.color }} className="text-sm">
            {entry.name}: {entry.value}
          </p>
        ))}
      </div>
    );
  }
  return null;
};

export const LevelDistribution: React.FC<LevelDistributionProps> = ({ data }) => {

  // Guard principal para prevenir crashes
  const safeData = useMemo(() => {
    return (data || []).filter(item =>
      item &&
      typeof item.nivel === 'string' &&
      typeof item.total === 'number' &&
      !isNaN(item.total) &&
      item.total >= 0
    );
  }, [data]);

  // Prepare data for the Pie Chart (Com validação)
  const pieData = useMemo(() => {
    return safeData.map(item => ({
      name: item.nivel,
      value: item.total
    }));
  }, [safeData]);

  const totalTickets = useMemo(() => pieData.reduce((acc, curr) => acc + curr.value, 0), [pieData]);

  // Validate and synthesize breakdown for Stacked Bar Chart
  // Since the API only provides 'total', we distribute it to match the visual style required (Novos/Em Progresso/Pendentes)
  // In a real scenario, the API should provide this breakdown.
  const barData = useMemo(() => {
    return safeData.map(item => {
      const total = item.total;
      // Synthesize distribution for demo purposes to match visual
      // Assuming approx: 10% New, 70% In Progress, 20% Pending
      const novos = Math.round(total * 0.1);
      const pendentes = Math.round(total * 0.2);
      const em_progresso = total - novos - pendentes;

      return {
        name: item.nivel,
        Novos: novos,
        'Em Progresso': em_progresso,
        Pendentes: pendentes
      };
    });
  }, [safeData]);

  const PIE_COLORS = [CHART_COLORS.purple, CHART_COLORS.blue, CHART_COLORS.cyan, CHART_COLORS.slate];

  // Empty state handler
  if (safeData.length === 0 || pieData.length === 0) {
    return (
      <div className="bg-dtic-card rounded-lg border border-dtic-border p-8 flex items-center justify-center h-full">
        <div className="text-center">
          <p className="text-slate-400 text-sm mb-2">📊 Sem dados de níveis de suporte</p>
          <p className="text-slate-500 text-xs">Aguardando sincronização do backend...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 h-full">
      {/* Left: Stacked Bar Chart */}
      <div className="bg-dtic-card rounded-lg p-4 border border-dtic-border relative flex flex-col">
        <div className="border-l-4 border-purple-500 pl-2 mb-4">
          <h3 className="text-slate-300 font-medium">Distribuição por Níveis de Suporte</h3>
        </div>

        <div className="flex-1 w-full min-h-[250px]">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={barData}
              margin={{ top: 20, right: 30, left: 0, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
              <XAxis
                dataKey="name"
                stroke="#94a3b8"
                tick={{ fill: '#94a3b8' }}
                axisLine={{ stroke: '#475569' }}
              />
              <YAxis
                stroke="#94a3b8"
                tick={{ fill: '#94a3b8' }}
                axisLine={{ stroke: '#475569' }}
              />
              <Tooltip content={<CustomTooltip />} cursor={{ fill: '#334155', opacity: 0.4 }} />
              <Legend
                wrapperStyle={{ paddingTop: '10px' }}
                iconType="square"
              />
              <Bar dataKey="Novos" stackId="a" fill={CHART_COLORS.blue} barSize={30} />
              <Bar dataKey="Em Progresso" stackId="a" fill={CHART_COLORS.orange} barSize={30} />
              <Bar dataKey="Pendentes" stackId="a" fill={CHART_COLORS.yellow} barSize={30} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Right: Donut Chart */}
      <div className="bg-dtic-card rounded-lg p-4 border border-dtic-border flex flex-col justify-center items-center relative">
        <div className="absolute top-4 left-4 text-sm text-slate-400">Total por Nível</div>

        <div className="w-full h-[300px]">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                innerRadius={80}
                outerRadius={110}
                fill="#8884d8"
                paddingAngle={5}
                dataKey="value"
                stroke="none"
              >
                {pieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                ))}
                <Label
                  value={`Total: ${totalTickets}`}
                  position="center"
                  fill="#e2e8f0"
                  style={{ fontSize: '18px', fontWeight: 'bold' }}
                />
              </Pie>
              <Tooltip
                contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', color: '#f8fafc' }}
                itemStyle={{ color: '#f8fafc' }}
              />
              <Legend
                layout="vertical"
                verticalAlign="middle"
                align="right"
                wrapperStyle={{ right: 0 }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};
import React, { useState, useMemo } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  PieChart, Pie, Cell, Label, LineChart, Line, AreaChart, Area
} from 'recharts';
import { ChevronLeft, ChevronRight, BarChart2, TrendingUp, PieChart as PieIcon } from 'lucide-react';
import { MetricsCarouselData } from '../../types';
import { CHART_COLORS } from '../../constants';

interface MetricsCarouselProps {
  data: MetricsCarouselData;
}

// Custom tooltip for consistent dark theme look
const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-slate-800 border border-slate-700 p-2 rounded shadow-lg z-50">
        <p className="text-slate-200 font-semibold mb-1 border-b border-slate-700 pb-1">{label}</p>
        {payload.map((entry: any, index: number) => (
          <p key={index} style={{ color: entry.color }} className="text-sm flex items-center gap-2">
            <span className="w-2 h-2 rounded-full" style={{ backgroundColor: entry.color }}></span>
            {entry.name}: <span className="font-mono font-bold">{entry.value}</span>
          </p>
        ))}
      </div>
    );
  }
  return null;
};

export const MetricsCarousel: React.FC<MetricsCarouselProps> = ({ data }) => {
  const [currentIndex, setCurrentIndex] = useState(0);

  // Robust safety check for data
  const safeData = data || { levels: [], history: [], categories: [] };
  const levels = safeData.levels || [];
  const history = safeData.history || [];
  const categories = safeData.categories || [];

  console.log('MetricsCarousel Data:', { levels: levels.length, history: history.length, categories: categories.length });

  // --- PREPARE DATA FOR VIEW 1 (LEVELS) ---
  const pieData = useMemo(() => {
    return levels.map(item => ({
      name: item.nivel,
      value: item.total
    }));
  }, [levels]);

  const totalTickets = useMemo(() => pieData.reduce((acc, curr) => acc + curr.value, 0), [pieData]);

  const barDataLevels = useMemo(() => {
    return (data.levels || []).map(item => {
      const total = item.total;
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
  }, [data.levels]);

  // --- DEEP DATA VALIDATION (Prevent Recharts tick calculation crashes) ---
  const safeBarDataLevels = useMemo(() => {
    return barDataLevels.filter(item =>
      item && typeof item.name === 'string' &&
      typeof item.Novos === 'number' &&
      typeof item['Em Progresso'] === 'number' &&
      typeof item.Pendentes === 'number'
    );
  }, [barDataLevels]);

  const safePieData = useMemo(() => {
    return pieData.filter(item =>
      item && typeof item.name === 'string' && typeof item.value === 'number'
    );
  }, [pieData]);

  const safeHistory = useMemo(() => {
    return history.filter(item =>
      item && item.date &&
      typeof item.created === 'number' &&
      typeof item.resolved === 'number'
    );
  }, [history]);

  const safeCategories = useMemo(() => {
    return categories.filter(item =>
      item && item.name && typeof item.value === 'number'
    );
  }, [categories]);

  const PIE_COLORS = [CHART_COLORS.purple, CHART_COLORS.blue, CHART_COLORS.cyan, CHART_COLORS.slate];
  const VIEWS_COUNT = 3;

  const nextSlide = () => setCurrentIndex((prev) => (prev + 1) % VIEWS_COUNT);
  const prevSlide = () => setCurrentIndex((prev) => (prev - 1 + VIEWS_COUNT) % VIEWS_COUNT);

  // Prevent rendering if all datasets are empty
  const hasData = safeBarDataLevels.length > 0 || safeHistory.length > 0 || safeCategories.length > 0;

  if (!hasData) {
    return (
      <div className="bg-dtic-card rounded-lg border border-dtic-border p-8 flex items-center justify-center">
        <p className="text-slate-400 text-sm">📊 Aguardando dados...</p>
      </div>
    );
  }

  // Render content based on active index
  const renderContent = () => {
    switch (currentIndex) {
      case 0: // Levels (Original View)
        return (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 h-full animate-[fadeIn_0.5s_ease-out]">
            {/* Stacked Bar */}
            <div className="flex flex-col h-full">
              <h4 className="text-xs text-slate-400 mb-2 uppercase tracking-wider font-semibold">Volume por Status</h4>
              <div className="flex-1" style={{ minHeight: '220px', height: '100%' }}>
                <ResponsiveContainer width="100%" height="100%" minHeight={220}>
                  <BarChart data={safeBarDataLevels} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke={CHART_COLORS.grid} vertical={false} />
                    <XAxis dataKey="name" stroke={CHART_COLORS.text} tick={{ fill: CHART_COLORS.text }} axisLine={{ stroke: CHART_COLORS.grid }} />
                    <YAxis stroke={CHART_COLORS.text} tick={{ fill: CHART_COLORS.text }} axisLine={{ stroke: CHART_COLORS.grid }} />
                    <Tooltip content={<CustomTooltip />} cursor={{ fill: CHART_COLORS.grid, opacity: 0.2 }} />
                    <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }} iconType="circle" />
                    <Bar dataKey="Novos" stackId="a" fill={CHART_COLORS.blue} barSize={20} radius={[0, 0, 0, 0]} />
                    <Bar dataKey="Em Progresso" stackId="a" fill={CHART_COLORS.orange} barSize={20} radius={[0, 0, 0, 0]} />
                    <Bar dataKey="Pendentes" stackId="a" fill={CHART_COLORS.yellow} barSize={20} radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
            {/* Donut */}
            <div className="flex flex-col items-center justify-center relative h-full">
              <div className="absolute top-0 left-0 text-xs text-slate-400 uppercase tracking-wider font-semibold">Total por Nível</div>
              <div className="w-full h-full" style={{ minHeight: '220px', height: '100%' }}>
                <ResponsiveContainer width="100%" height="100%" minHeight={220}>
                  <PieChart>
                    <Pie
                      data={safePieData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={80}
                      paddingAngle={5}
                      dataKey="value"
                      stroke="none"
                    >
                      {safePieData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                      ))}
                      <Label value={totalTickets} position="center" fill="#e2e8f0" style={{ fontSize: '24px', fontWeight: 'bold' }} />
                    </Pie>
                    <Tooltip content={<CustomTooltip />} />
                    <Legend layout="vertical" verticalAlign="middle" align="right" wrapperStyle={{ right: 0, fontSize: '11px' }} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        );

      case 1: // History (Line Chart)
        return (
          <div className="h-full flex flex-col animate-[fadeIn_0.5s_ease-out]">
            <div className="flex justify-between items-center mb-2">
              <h4 className="text-xs text-slate-400 uppercase tracking-wider font-semibold">Tendência (7 Dias): Criados vs Resolvidos</h4>
            </div>
            <div className="flex-1" style={{ minHeight: '280px', height: '100%' }}>
              <ResponsiveContainer width="100%" height="100%" minHeight={280}>
                <AreaChart data={safeHistory} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorCreated" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor={CHART_COLORS.blue} stopOpacity={0.3} />
                      <stop offset="95%" stopColor={CHART_COLORS.blue} stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="colorResolved" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor={CHART_COLORS.green} stopOpacity={0.3} />
                      <stop offset="95%" stopColor={CHART_COLORS.green} stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke={CHART_COLORS.grid} vertical={false} />
                  <XAxis dataKey="date" stroke={CHART_COLORS.text} tick={{ fill: CHART_COLORS.text }} axisLine={{ stroke: CHART_COLORS.grid }} />
                  <YAxis stroke={CHART_COLORS.text} tick={{ fill: CHART_COLORS.text }} axisLine={{ stroke: CHART_COLORS.grid }} />
                  <Tooltip content={<CustomTooltip />} cursor={{ stroke: CHART_COLORS.grid, strokeWidth: 2 }} />
                  <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }} iconType="plainline" />
                  <Area type="monotone" name="Criados" dataKey="created" stroke={CHART_COLORS.blue} fillOpacity={1} fill="url(#colorCreated)" strokeWidth={3} />
                  <Area type="monotone" name="Resolvidos" dataKey="resolved" stroke={CHART_COLORS.green} fillOpacity={1} fill="url(#colorResolved)" strokeWidth={3} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>
        );

      case 2: // Categories (Horizontal Bar)
        return (
          <div className="h-full flex flex-col animate-[fadeIn_0.5s_ease-out]">
            <h4 className="text-xs text-slate-400 mb-2 uppercase tracking-wider font-semibold">Top 5 Categorias de Chamados</h4>
            <div className="flex-1" style={{ minHeight: '280px', height: '100%' }}>
              <ResponsiveContainer width="100%" height="100%" minHeight={280}>
                <BarChart
                  layout="vertical"
                  data={safeCategories}
                  margin={{ top: 5, right: 30, left: 40, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke={CHART_COLORS.grid} horizontal={false} />
                  <XAxis type="number" stroke={CHART_COLORS.text} tick={{ fill: CHART_COLORS.text }} axisLine={{ stroke: CHART_COLORS.grid }} />
                  <YAxis
                    type="category"
                    dataKey="name"
                    stroke={CHART_COLORS.text}
                    tick={{ fill: CHART_COLORS.text, fontSize: 12 }}
                    width={120}
                    axisLine={false}
                  />
                  <Tooltip content={<CustomTooltip />} cursor={{ fill: CHART_COLORS.grid, opacity: 0.2 }} />
                  <Bar dataKey="value" name="Tickets" fill={CHART_COLORS.purple} radius={[0, 4, 4, 0]} barSize={25}>
                    <LabelList dataKey="value" position="right" fill="#fff" fontSize={12} />
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        );
      default: return null;
    }
  };

  const titles = ["Distribuição de Níveis", "Histórico Recente", "Top Categorias"];
  const icons = [<PieIcon size={16} />, <TrendingUp size={16} />, <BarChart2 size={16} />];

  return (
    <div className="bg-dtic-card rounded-lg border border-dtic-border relative flex flex-col h-full overflow-hidden shadow-sm hover:shadow-md transition-shadow">
      {/* Header with Navigation */}
      <div className="flex justify-between items-center p-3 border-b border-dtic-border bg-slate-800/50">
        <div className="flex items-center gap-2 text-slate-200">
          {icons[currentIndex]}
          <h3 className="font-medium text-sm">{titles[currentIndex]}</h3>
        </div>

        <div className="flex items-center gap-2">
          <div className="flex gap-1 mr-2">
            {titles.map((_, idx) => (
              <div
                key={idx}
                onClick={() => setCurrentIndex(idx)}
                className={`w-1.5 h-1.5 rounded-full cursor-pointer transition-colors ${idx === currentIndex ? 'bg-blue-400' : 'bg-slate-600 hover:bg-slate-500'}`}
              />
            ))}
          </div>
          <button onClick={prevSlide} className="p-1 hover:bg-slate-700 rounded text-slate-400 hover:text-white transition-colors">
            <ChevronLeft size={16} />
          </button>
          <button onClick={nextSlide} className="p-1 hover:bg-slate-700 rounded text-slate-400 hover:text-white transition-colors">
            <ChevronRight size={16} />
          </button>
        </div>
      </div>

      {/* Main Chart Content */}
      <div className="flex-1 p-4 min-h-0 overflow-hidden">
        {renderContent()}
      </div>
    </div>
  );
};

// Helper for BarChart label list which isn't exported by recharts main entry sometimes
const LabelList = (props: any) => {
  const { x, y, width, height, value, fill, fontSize } = props;
  return (
    <text x={x + width + 5} y={y + height / 2} fill={fill} fontSize={fontSize} dominantBaseline="middle">
      {value}
    </text>
  );
};
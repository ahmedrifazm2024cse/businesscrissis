import React from 'react';
import { useMarketDashboard } from '../hooks/useMarketData';
import { Loader2, Calendar, TrendingUp } from 'lucide-react';
import { LineChart } from '../components/LineChart';

export const DemandForecast: React.FC = () => {
  const { data, isLoading, error } = useMarketDashboard();

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh] gap-4">
        <Loader2 className="w-8 h-8 text-brand-500 animate-spin" />
        <p className="text-sm font-semibold text-slate-500">Running forecast models...</p>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="p-6 border border-red-200 dark:border-red-900/30 bg-red-50 dark:bg-red-950/20 rounded-2xl">
        <h3 className="font-bold text-red-800 dark:text-red-400">Connection Failed</h3>
        <p className="text-sm text-red-700 dark:text-red-400/80 mt-1">
          Could not communicate with the Market Intelligence Agent API.
        </p>
      </div>
    );
  }

  const { historical, forecast, message } = data.demandForecast;

  // Construct label indices & data lines for the Chart
  const labels = [
    ...historical.map((h) => h.month),
    ...forecast.map((f) => f.month)
  ];

  // Historical data has actual numbers, then is blank (null) during forecast period
  const historicalData = [
    ...historical.map((h) => h.sales_units),
    ...forecast.map(() => null as any)
  ];

  // Forecast data has nulls for historical period, then has predicted values
  // We can connect the line by making the last historical index match the first forecast index
  const forecastData = [
    ...historical.map((h, idx) => idx === historical.length - 1 ? h.sales_units : null as any),
    ...forecast.map((f) => f.sales_units)
  ];

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl md:text-3xl font-extrabold tracking-tight text-slate-800 dark:text-white">
          Demand Forecasting
        </h1>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
          Sales volume projections computed via scikit-learn regression algorithms.
        </p>
      </div>

      {/* Summary message banner */}
      <div className="p-6 bg-brand-50 dark:bg-brand-950/20 border border-brand-100 dark:border-brand-900/30 rounded-2xl flex items-start gap-4">
        <div className="p-2 bg-white dark:bg-slate-900 rounded-lg shadow-sm border border-slate-100 dark:border-slate-800">
          <TrendingUp className="w-5 h-5 text-brand-600 dark:text-brand-400" />
        </div>
        <div>
          <h3 className="text-sm font-bold text-slate-800 dark:text-white">Regression Engine Forecast Summary</h3>
          <p className="text-sm text-slate-600 dark:text-slate-350 mt-1 font-semibold">{message}</p>
        </div>
      </div>

      {/* Chart container */}
      <div className="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800 rounded-2xl p-6 shadow-sm">
        <h3 className="text-sm font-semibold text-slate-500 dark:text-slate-400 mb-6">Historical vs Forecasted Volume (Units)</h3>
        <LineChart 
          labels={labels} 
          historicalData={historicalData} 
          forecastData={forecastData} 
        />
      </div>

      {/* Detailed Forecast Points List */}
      <div className="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800 rounded-2xl p-6 shadow-sm">
        <h3 className="text-sm font-semibold text-slate-500 dark:text-slate-400 mb-6">Projected Target Milestones</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {forecast.slice(0, 3).map((point, idx) => (
            <div key={idx} className="p-4 rounded-xl border border-slate-100 dark:border-slate-850 bg-slate-50/40 dark:bg-slate-900 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Calendar className="w-5 h-5 text-slate-400" />
                <div>
                  <p className="text-xs text-slate-400 dark:text-slate-500 font-bold uppercase">{point.month}</p>
                  <p className="text-lg font-extrabold text-slate-700 dark:text-slate-100 mt-0.5">{point.sales_units} units</p>
                </div>
              </div>
              <span className="text-[10px] font-bold text-slate-400 dark:text-slate-500">
                NPS: {point.nps}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

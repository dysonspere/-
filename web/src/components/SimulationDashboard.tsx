import { useState } from 'react';
import { Portfolio } from '../services/Portfolio';
import { Simulator, MonteCarloSimulator } from '../services/Simulator';
import type { SimulationResult, SimulationStatistics, MonteCarloResults } from '../services';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  AreaChart,
  Area,
} from 'recharts';
import { Play, BarChart3, Loader } from 'lucide-react';

interface SimulationDashboardProps {
  portfolio: Portfolio;
}

export function SimulationDashboard({ portfolio }: SimulationDashboardProps) {
  const [simulationType, setSimulationType] = useState<'single' | 'montecarlo'>('single');
  const [days, setDays] = useState('252');
  const [numSimulations, setNumSimulations] = useState('1000');
  const [isRunning, setIsRunning] = useState(false);
  const [progress, setProgress] = useState(0);

  const [results, setResults] = useState<SimulationResult[] | null>(null);
  const [statistics, setStatistics] = useState<SimulationStatistics | null>(null);
  const [mcResults, setMcResults] = useState<MonteCarloResults | null>(null);

  const handleRunSimulation = async () => {
    setIsRunning(true);
    setProgress(0);
    setResults(null);
    setStatistics(null);
    setMcResults(null);

    // Clone portfolio for simulation
    const simPortfolio = portfolio.clone();

    if (simulationType === 'single') {
      const simulator = new Simulator(simPortfolio);

      // Run simulation with progress updates
      await new Promise<void>((resolve) => {
        setTimeout(() => {
          const simResults = simulator.run(parseInt(days), (current, total) => {
            setProgress((current / total) * 100);
          });
          setResults(simResults);
          setStatistics(simulator.getStatistics());
          setIsRunning(false);
          resolve();
        }, 100);
      });
    } else {
      const mcSimulator = new MonteCarloSimulator(simPortfolio);

      await new Promise<void>((resolve) => {
        setTimeout(() => {
          const mcRes = mcSimulator.run(
            parseInt(numSimulations),
            parseInt(days),
            (current, total) => {
              setProgress((current / total) * 100);
            }
          );
          setMcResults(mcRes);
          setIsRunning(false);
          resolve();
        }, 100);
      });
    }
  };

  return (
    <div className="simulation-dashboard">
      <h2>シミュレーション</h2>

      <div className="simulation-controls">
        <div className="simulation-type-selector">
          <button
            className={simulationType === 'single' ? 'active' : ''}
            onClick={() => setSimulationType('single')}
          >
            <BarChart3 size={20} />
            単一シミュレーション
          </button>
          <button
            className={simulationType === 'montecarlo' ? 'active' : ''}
            onClick={() => setSimulationType('montecarlo')}
          >
            <BarChart3 size={20} />
            モンテカルロ
          </button>
        </div>

        <div className="simulation-params">
          <div className="param-group">
            <label>シミュレーション期間（日数）</label>
            <input
              type="number"
              value={days}
              onChange={(e) => setDays(e.target.value)}
              min="1"
              max="5000"
              disabled={isRunning}
            />
            <small>{Math.round(parseInt(days) / 252)} 年</small>
          </div>

          {simulationType === 'montecarlo' && (
            <div className="param-group">
              <label>シミュレーション回数</label>
              <input
                type="number"
                value={numSimulations}
                onChange={(e) => setNumSimulations(e.target.value)}
                min="100"
                max="10000"
                step="100"
                disabled={isRunning}
              />
            </div>
          )}
        </div>

        <button
          onClick={handleRunSimulation}
          className="btn-primary btn-large"
          disabled={isRunning}
        >
          {isRunning ? (
            <>
              <Loader size={20} className="spinner" />
              実行中... {progress.toFixed(0)}%
            </>
          ) : (
            <>
              <Play size={20} />
              シミュレーション実行
            </>
          )}
        </button>
      </div>

      {results && statistics && simulationType === 'single' && (
        <div className="simulation-results">
          <div className="stats-grid">
            <StatCard label="初期資産" value={`¥${statistics.initialValue.toLocaleString()}`} />
            <StatCard label="最終資産" value={`¥${statistics.finalValue.toLocaleString()}`} />
            <StatCard
              label="総リターン"
              value={`${statistics.totalReturn >= 0 ? '+' : ''}${statistics.totalReturn.toFixed(2)}%`}
              highlight={statistics.totalReturn >= 0}
            />
            <StatCard
              label="最大ドローダウン"
              value={`${statistics.maxDrawdown.toFixed(2)}%`}
            />
            <StatCard label="ボラティリティ" value={`${statistics.volatility.toFixed(2)}%`} />
            <StatCard label="シャープレシオ" value={statistics.sharpeRatio.toFixed(2)} />
          </div>

          <div className="chart-container">
            <h3>ポートフォリオ価値の推移</h3>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={results}>
                <defs>
                  <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#4f46e5" stopOpacity={0.8} />
                    <stop offset="95%" stopColor="#4f46e5" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis
                  dataKey="day"
                  label={{ value: '日数', position: 'insideBottom', offset: -5 }}
                />
                <YAxis
                  tickFormatter={(value) => `¥${(value / 1000000).toFixed(1)}M`}
                  label={{ value: '資産価値', angle: -90, position: 'insideLeft' }}
                />
                <Tooltip
                  formatter={(value: number) => [`¥${value.toLocaleString()}`, 'ポートフォリオ価値']}
                />
                <Area
                  type="monotone"
                  dataKey="portfolioValue"
                  stroke="#4f46e5"
                  fillOpacity={1}
                  fill="url(#colorValue)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          <div className="chart-container">
            <h3>累積リターンの推移</h3>
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={results}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="day" />
                <YAxis
                  tickFormatter={(value) => `${value.toFixed(1)}%`}
                  label={{ value: 'リターン (%)', angle: -90, position: 'insideLeft' }}
                />
                <Tooltip formatter={(value: number) => [`${value.toFixed(2)}%`, '累積リターン']} />
                <Line
                  type="monotone"
                  dataKey="cumulativeReturn"
                  stroke="#10b981"
                  strokeWidth={2}
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {mcResults && simulationType === 'montecarlo' && (
        <div className="montecarlo-results">
          <h3>モンテカルロシミュレーション結果</h3>

          <div className="percentiles-grid">
            <PercentileCard
              percentile="5%"
              label="悲観的"
              value={mcResults.percentiles.p5}
              color="red"
            />
            <PercentileCard
              percentile="25%"
              label="やや悲観的"
              value={mcResults.percentiles.p25}
              color="orange"
            />
            <PercentileCard
              percentile="50%"
              label="中央値"
              value={mcResults.percentiles.p50}
              color="blue"
            />
            <PercentileCard
              percentile="75%"
              label="やや楽観的"
              value={mcResults.percentiles.p75}
              color="lightgreen"
            />
            <PercentileCard
              percentile="95%"
              label="楽観的"
              value={mcResults.percentiles.p95}
              color="green"
            />
          </div>

          <div className="stats-grid">
            <StatCard
              label="平均最終資産"
              value={`¥${mcResults.statistics.meanFinalValue.toLocaleString()}`}
            />
            <StatCard
              label="中央値"
              value={`¥${mcResults.statistics.medianFinalValue.toLocaleString()}`}
            />
            <StatCard
              label="標準偏差"
              value={`¥${mcResults.statistics.stdFinalValue.toLocaleString()}`}
            />
            <StatCard
              label="最小値"
              value={`¥${mcResults.statistics.minFinalValue.toLocaleString()}`}
            />
            <StatCard
              label="最大値"
              value={`¥${mcResults.statistics.maxFinalValue.toLocaleString()}`}
            />
          </div>

          <div className="chart-container">
            <h3>シミュレーション結果の分布（サンプル）</h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="day" />
                <YAxis tickFormatter={(value) => `¥${(value / 1000000).toFixed(1)}M`} />
                <Tooltip />
                <Legend />
                {mcResults.simulations.slice(0, 20).map((sim, idx) => (
                  <Line
                    key={idx}
                    type="monotone"
                    data={sim}
                    dataKey="portfolioValue"
                    stroke={`hsl(${(idx * 360) / 20}, 70%, 50%)`}
                    strokeWidth={1}
                    dot={false}
                    opacity={0.3}
                  />
                ))}
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
    </div>
  );
}

interface StatCardProps {
  label: string;
  value: string;
  highlight?: boolean;
}

function StatCard({ label, value, highlight }: StatCardProps) {
  return (
    <div className={`stat-card ${highlight ? 'highlight' : ''}`}>
      <label>{label}</label>
      <div className="value">{value}</div>
    </div>
  );
}

interface PercentileCardProps {
  percentile: string;
  label: string;
  value: number;
  color: string;
}

function PercentileCard({ percentile, label, value, color }: PercentileCardProps) {
  return (
    <div className={`percentile-card ${color}`}>
      <div className="percentile">{percentile}</div>
      <div className="label">{label}</div>
      <div className="value">¥{value.toLocaleString()}</div>
    </div>
  );
}

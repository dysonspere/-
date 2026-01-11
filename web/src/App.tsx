import { useState } from 'react';
import { Portfolio } from './services/Portfolio';
import { PortfolioBuilder } from './components/PortfolioBuilder';
import { SimulationDashboard } from './components/SimulationDashboard';
import { VerticalTextEditor } from './components/VerticalTextEditor';
import { TrendingUp } from 'lucide-react';
import './App.css';

function App() {
  const [portfolio, setPortfolio] = useState<Portfolio>(new Portfolio(10000000));
  const [activeTab, setActiveTab] = useState<'builder' | 'simulation' | 'editor'>('editor');

  const handlePortfolioChange = (newPortfolio: Portfolio) => {
    setPortfolio(newPortfolio);
  };

  const handleRunSimulation = () => {
    setActiveTab('simulation');
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <div className="logo">
            <TrendingUp size={32} />
            <h1>資産運用シミュレーター</h1>
          </div>
          <p className="subtitle">株式と債券のポートフォリオ管理とシミュレーション</p>
        </div>
      </header>

      <nav className="app-nav">
        <button
          className={activeTab === 'editor' ? 'active' : ''}
          onClick={() => setActiveTab('editor')}
        >
          縦書きエディタ
        </button>
        <button
          className={activeTab === 'builder' ? 'active' : ''}
          onClick={() => setActiveTab('builder')}
        >
          ポートフォリオ作成
        </button>
        <button
          className={activeTab === 'simulation' ? 'active' : ''}
          onClick={() => setActiveTab('simulation')}
        >
          シミュレーション
        </button>
      </nav>

      <main className="app-main">
        {activeTab === 'editor' ? (
          <VerticalTextEditor />
        ) : activeTab === 'builder' ? (
          <PortfolioBuilder
            portfolio={portfolio}
            onPortfolioChange={handlePortfolioChange}
            onRunSimulation={handleRunSimulation}
          />
        ) : (
          <SimulationDashboard portfolio={portfolio} />
        )}
      </main>

      <footer className="app-footer">
        <p>
          Asset Management Simulator - 株式（幾何ブラウン運動）と債券（現在価値法）による資産運用シミュレーション
        </p>
      </footer>
    </div>
  );
}

export default App;

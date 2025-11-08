import { useState } from 'react';
import { Portfolio } from '../services/Portfolio';
import { Stock } from '../models/Stock';
import { Bond } from '../models/Bond';
import { AssetInput } from './AssetInput';
import { Trash2, TrendingUp, TrendingDown } from 'lucide-react';

interface PortfolioBuilderProps {
  portfolio: Portfolio;
  onPortfolioChange: (portfolio: Portfolio) => void;
  onRunSimulation: () => void;
}

export function PortfolioBuilder({
  portfolio,
  onPortfolioChange,
  onRunSimulation,
}: PortfolioBuilderProps) {
  const [initialCash, setInitialCash] = useState('10000000');

  const handleSetInitialCash = () => {
    const cash = parseFloat(initialCash);
    if (cash > 0) {
      const newPortfolio = new Portfolio(cash);
      onPortfolioChange(newPortfolio);
    }
  };

  const handleAddAsset = (asset: Stock | Bond, quantity: number) => {
    const success = portfolio.buy(asset.symbol, asset, quantity);
    if (success) {
      onPortfolioChange(portfolio);
    }
  };

  const handleRemoveAsset = (symbol: string) => {
    const holding = portfolio.holdings.get(symbol);
    if (holding) {
      portfolio.sell(symbol, holding.quantity);
      onPortfolioChange(portfolio);
    }
  };

  const summary = portfolio.getSummary();
  const allocation = summary.assetAllocation;

  return (
    <div className="portfolio-builder">
      <div className="builder-header">
        <h2>ポートフォリオ作成</h2>
      </div>

      <div className="initial-cash-section">
        <h3>初期現金</h3>
        <div className="cash-input-group">
          <input
            type="number"
            value={initialCash}
            onChange={(e) => setInitialCash(e.target.value)}
            placeholder="10000000"
            min="0"
            step="100000"
          />
          <button onClick={handleSetInitialCash} className="btn-secondary">
            設定
          </button>
        </div>
        <p className="cash-display">
          現在の現金: <strong>¥{portfolio.cash.toLocaleString()}</strong>
        </p>
      </div>

      <AssetInput onAddAsset={handleAddAsset} />

      <div className="portfolio-summary">
        <h3>ポートフォリオサマリー</h3>

        <div className="summary-grid">
          <div className="summary-card">
            <label>総資産価値</label>
            <div className="value">¥{summary.totalValue.toLocaleString()}</div>
          </div>

          <div className="summary-card">
            <label>累積リターン</label>
            <div className={`value ${summary.returns >= 0 ? 'positive' : 'negative'}`}>
              {summary.returns >= 0 ? <TrendingUp size={20} /> : <TrendingDown size={20} />}
              {summary.returns.toFixed(2)}%
            </div>
          </div>

          <div className="summary-card">
            <label>期待リターン（年率）</label>
            <div className="value">{(summary.expectedReturn * 100).toFixed(2)}%</div>
          </div>

          <div className="summary-card">
            <label>リスク（年率）</label>
            <div className="value">{(summary.risk * 100).toFixed(2)}%</div>
          </div>

          <div className="summary-card">
            <label>シャープレシオ</label>
            <div className="value">{summary.sharpeRatio.toFixed(2)}</div>
          </div>

          <div className="summary-card">
            <label>保有銘柄数</label>
            <div className="value">{summary.numHoldings}</div>
          </div>
        </div>

        <div className="asset-allocation">
          <h4>資産配分</h4>
          <div className="allocation-bars">
            {Object.entries(allocation).map(([symbol, percentage]) => (
              <div key={symbol} className="allocation-item">
                <div className="allocation-label">
                  <span>{symbol}</span>
                  <span>{percentage.toFixed(1)}%</span>
                </div>
                <div className="allocation-bar-container">
                  <div
                    className="allocation-bar"
                    style={{ width: `${percentage}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="holdings-list">
          <h4>保有資産</h4>
          {portfolio.holdings.size === 0 ? (
            <p className="empty-state">資産を追加してください</p>
          ) : (
            <table>
              <thead>
                <tr>
                  <th>シンボル</th>
                  <th>名称</th>
                  <th>種類</th>
                  <th>数量</th>
                  <th>単価</th>
                  <th>評価額</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {Array.from(portfolio.holdings.entries()).map(([symbol, { asset, quantity }]) => {
                  const value = asset.currentPrice * quantity;
                  return (
                    <tr key={symbol}>
                      <td>{symbol}</td>
                      <td>{asset.name}</td>
                      <td>{asset instanceof Stock ? '株式' : '債券'}</td>
                      <td>{quantity}</td>
                      <td>¥{asset.currentPrice.toLocaleString()}</td>
                      <td>¥{value.toLocaleString()}</td>
                      <td>
                        <button
                          onClick={() => handleRemoveAsset(symbol)}
                          className="btn-icon-danger"
                          title="削除"
                        >
                          <Trash2 size={16} />
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          )}
        </div>

        {portfolio.holdings.size > 0 && (
          <button onClick={onRunSimulation} className="btn-primary btn-large">
            シミュレーション実行
          </button>
        )}
      </div>
    </div>
  );
}

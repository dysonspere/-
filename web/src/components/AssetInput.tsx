import { useState } from 'react';
import { Stock } from '../models/Stock';
import { Bond } from '../models/Bond';
import { Plus } from 'lucide-react';

interface AssetInputProps {
  onAddAsset: (asset: Stock | Bond, quantity: number) => void;
}

export function AssetInput({ onAddAsset }: AssetInputProps) {
  const [assetType, setAssetType] = useState<'stock' | 'bond'>('stock');
  const [symbol, setSymbol] = useState('');
  const [name, setName] = useState('');
  const [price, setPrice] = useState('');
  const [quantity, setQuantity] = useState('');

  // Stock specific
  const [expectedReturn, setExpectedReturn] = useState('0.10');
  const [volatility, setVolatility] = useState('0.20');
  const [dividendYield, setDividendYield] = useState('0.02');

  // Bond specific
  const [faceValue, setFaceValue] = useState('100');
  const [couponRate, setCouponRate] = useState('0.02');
  const [yearsToMaturity, setYearsToMaturity] = useState('10');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!symbol || !name || !price || !quantity) {
      alert('すべての必須フィールドを入力してください');
      return;
    }

    const qty = parseInt(quantity);
    if (qty <= 0) {
      alert('数量は正の整数である必要があります');
      return;
    }

    let asset: Stock | Bond;

    if (assetType === 'stock') {
      asset = new Stock(
        symbol,
        name,
        parseFloat(price),
        parseFloat(expectedReturn),
        parseFloat(volatility),
        parseFloat(dividendYield)
      );
    } else {
      asset = new Bond(
        symbol,
        name,
        parseFloat(faceValue),
        parseFloat(couponRate),
        parseInt(yearsToMaturity)
      );
    }

    onAddAsset(asset, qty);

    // Reset form
    setSymbol('');
    setName('');
    setPrice('');
    setQuantity('');
  };

  return (
    <div className="asset-input">
      <h3>資産を追加</h3>

      <div className="asset-type-selector">
        <button
          className={assetType === 'stock' ? 'active' : ''}
          onClick={() => setAssetType('stock')}
        >
          株式
        </button>
        <button
          className={assetType === 'bond' ? 'active' : ''}
          onClick={() => setAssetType('bond')}
        >
          債券
        </button>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="form-grid">
          <div className="form-group">
            <label>シンボル *</label>
            <input
              type="text"
              value={symbol}
              onChange={(e) => setSymbol(e.target.value)}
              placeholder="例: 7203"
              required
            />
          </div>

          <div className="form-group">
            <label>名称 *</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="例: トヨタ自動車"
              required
            />
          </div>

          {assetType === 'stock' ? (
            <>
              <div className="form-group">
                <label>現在価格 *</label>
                <input
                  type="number"
                  value={price}
                  onChange={(e) => setPrice(e.target.value)}
                  placeholder="2500"
                  min="0"
                  step="0.01"
                  required
                />
              </div>

              <div className="form-group">
                <label>数量 *</label>
                <input
                  type="number"
                  value={quantity}
                  onChange={(e) => setQuantity(e.target.value)}
                  placeholder="100"
                  min="1"
                  step="1"
                  required
                />
              </div>

              <div className="form-group">
                <label>期待リターン（年率）</label>
                <input
                  type="number"
                  value={expectedReturn}
                  onChange={(e) => setExpectedReturn(e.target.value)}
                  placeholder="0.10"
                  min="0"
                  max="1"
                  step="0.01"
                />
                <small>{(parseFloat(expectedReturn) * 100).toFixed(0)}%</small>
              </div>

              <div className="form-group">
                <label>ボラティリティ（年率）</label>
                <input
                  type="number"
                  value={volatility}
                  onChange={(e) => setVolatility(e.target.value)}
                  placeholder="0.20"
                  min="0"
                  max="2"
                  step="0.01"
                />
                <small>{(parseFloat(volatility) * 100).toFixed(0)}%</small>
              </div>

              <div className="form-group">
                <label>配当利回り（年率）</label>
                <input
                  type="number"
                  value={dividendYield}
                  onChange={(e) => setDividendYield(e.target.value)}
                  placeholder="0.02"
                  min="0"
                  max="0.2"
                  step="0.001"
                />
                <small>{(parseFloat(dividendYield) * 100).toFixed(1)}%</small>
              </div>
            </>
          ) : (
            <>
              <div className="form-group">
                <label>額面金額 *</label>
                <input
                  type="number"
                  value={faceValue}
                  onChange={(e) => setFaceValue(e.target.value)}
                  placeholder="100"
                  min="0"
                  step="0.01"
                  required
                />
              </div>

              <div className="form-group">
                <label>数量 *</label>
                <input
                  type="number"
                  value={quantity}
                  onChange={(e) => setQuantity(e.target.value)}
                  placeholder="50"
                  min="1"
                  step="1"
                  required
                />
              </div>

              <div className="form-group">
                <label>クーポンレート（年率）</label>
                <input
                  type="number"
                  value={couponRate}
                  onChange={(e) => setCouponRate(e.target.value)}
                  placeholder="0.02"
                  min="0"
                  max="0.2"
                  step="0.001"
                />
                <small>{(parseFloat(couponRate) * 100).toFixed(1)}%</small>
              </div>

              <div className="form-group">
                <label>償還までの年数</label>
                <input
                  type="number"
                  value={yearsToMaturity}
                  onChange={(e) => setYearsToMaturity(e.target.value)}
                  placeholder="10"
                  min="1"
                  max="30"
                  step="1"
                />
                <small>{yearsToMaturity}年</small>
              </div>
            </>
          )}
        </div>

        <button type="submit" className="btn-primary">
          <Plus size={20} />
          追加
        </button>
      </form>
    </div>
  );
}

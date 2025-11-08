# 資産運用シミュレーター (Asset Management Simulator)

株式と債券のポートフォリオ管理と投資シミュレーションを行うPythonアプリケーション

## 機能

- 📈 株式の価格シミュレーション（幾何ブラウン運動モデル）
- 📊 債券の価格計算と利回り管理
- 💼 ポートフォリオ管理（複数資産の保有と売買）
- 📉 リスク分析（標準偏差、シャープレシオ）
- 💰 リターン計算とパフォーマンス追跡

## インストール

```bash
pip install -r requirements.txt
```

## 使用方法

```bash
python main.py
```

## プロジェクト構造

```
.
├── main.py                 # メインエントリーポイント
├── models/
│   ├── asset.py           # 資産の基底クラス
│   ├── stock.py           # 株式クラス
│   └── bond.py            # 債券クラス
├── portfolio.py           # ポートフォリオ管理
├── simulator.py           # シミュレーションエンジン
├── reporting.py           # レポート生成
├── utils.py               # ユーティリティ関数
└── examples/              # 使用例
    ├── basic_example.py
    ├── monte_carlo_example.py
    └── rebalancing_example.py
```

## クイックスタート

### 対話型CLIの使用

```bash
python main.py
```

メニューから選択するだけで、すぐにシミュレーションを開始できます。

### Pythonコードでの使用

```python
from models.stock import Stock
from models.bond import Bond
from portfolio import Portfolio
from simulator import Simulator

# ポートフォリオ作成（初期資金1000万円）
portfolio = Portfolio(initial_cash=10000000)

# 株式を購入
toyota = Stock("7203", "トヨタ自動車", 2500, expected_return=0.10, volatility=0.25)
portfolio.buy("7203", toyota, 100)

# 債券を購入
jgb = Bond("JGB10", "国債10年", 100, coupon_rate=0.015, years_to_maturity=10)
portfolio.buy("JGB10", jgb, 50)

# シミュレーション実行（1年間）
simulator = Simulator(portfolio)
results = simulator.run(days=252, verbose=True)

# 統計情報表示
simulator.print_statistics()
portfolio.print_summary()
```

## 使用例

プロジェクトには3つの実用的な例が含まれています：

### 1. 基本的な使用例

```bash
cd examples
python basic_example.py
```

株式と債券を含むポートフォリオの作成と1年間のシミュレーション

### 2. モンテカルロシミュレーション

```bash
cd examples
python monte_carlo_example.py
```

1000回のシミュレーションで将来の資産価値の分布を分析

### 3. リバランシング戦略

```bash
cd examples
python rebalancing_example.py
```

四半期ごとにポートフォリオをリバランスする戦略の実装

## 詳細ドキュメント

詳しい使い方は[USER_GUIDE.md](USER_GUIDE.md)を参照してください。

## 技術仕様

### 株式モデル
- **価格モデル**: 幾何ブラウン運動（Geometric Brownian Motion）
- **パラメータ**: 期待リターン、ボラティリティ、配当利回り
- **配当**: 自動的に配当金を計算・支払い

### 債券モデル
- **価格計算**: 現在価値法（Present Value Method）
- **パラメータ**: 額面、クーポンレート、償還期間、市場利回り
- **リスク計算**: デュレーションベースのボラティリティ推定

### ポートフォリオ分析
- 資産配分の計算
- 期待リターン（加重平均）
- リスク（加重平均ボラティリティ）
- シャープレシオ
- 最大ドローダウン

## 貢献

バグ報告や機能提案は、GitHubのIssuesまでお願いします。

## ライセンス

MIT License

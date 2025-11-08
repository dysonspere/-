# 資産運用シミュレーター ユーザーガイド

## 目次

1. [概要](#概要)
2. [インストール](#インストール)
3. [基本的な使い方](#基本的な使い方)
4. [主要機能](#主要機能)
5. [使用例](#使用例)
6. [API リファレンス](#apiリファレンス)

## 概要

資産運用シミュレーターは、株式と債券のポートフォリオ管理と投資シミュレーションを行うPythonアプリケーションです。

### 主な特徴

- **リアルな価格モデル**: 株式は幾何ブラウン運動、債券は現在価値法を使用
- **リスク分析**: ボラティリティ、シャープレシオ、最大ドローダウンなどを計算
- **モンテカルロシミュレーション**: 複数シナリオで将来の資産価値を予測
- **インタラクティブCLI**: 使いやすいコマンドラインインターフェース
- **詳細レポート**: 包括的なパフォーマンスレポート生成

## インストール

### 必要要件

- Python 3.8以上
- pip（Pythonパッケージマネージャー）

### セットアップ

```bash
# リポジトリをクローン
git clone <repository-url>
cd asset-management-simulator

# 依存パッケージをインストール
pip install -r requirements.txt
```

## 基本的な使い方

### メインアプリケーションの起動

```bash
python main.py
```

メニューから以下のオプションを選択できます：

1. サンプルポートフォリオでシミュレーション
2. 保守的ポートフォリオでシミュレーション（債券中心）
3. 積極的ポートフォリオでシミュレーション（株式中心）
4. カスタムポートフォリオ作成
5. モンテカルロシミュレーション
6. クイックデモ

### クイックスタート

最も簡単な方法は、クイックデモ（オプション6）を実行することです：

```bash
python main.py
# メニューで「6」を選択
```

## 主要機能

### 1. 資産クラス

#### 株式（Stock）

幾何ブラウン運動モデルを使用して価格をシミュレート：

```python
from models.stock import Stock

stock = Stock(
    symbol="7203",           # ティッカーシンボル
    name="トヨタ自動車",      # 会社名
    current_price=2500,      # 現在価格
    expected_return=0.10,    # 期待リターン（年率10%）
    volatility=0.25,         # ボラティリティ（年率25%）
    dividend_yield=0.02      # 配当利回り（年率2%）
)
```

**特徴:**
- 価格変動シミュレーション
- 配当金の支払い
- リスク・リターン分析

#### 債券（Bond）

現在価値法による債券価格計算：

```python
from models.bond import Bond

bond = Bond(
    symbol="JGB10",          # 債券シンボル
    name="日本国債10年",      # 債券名
    face_value=100,          # 額面金額
    coupon_rate=0.015,       # クーポンレート（年率1.5%）
    years_to_maturity=10     # 償還までの年数
)
```

**特徴:**
- 債券価格の自動計算
- クーポン支払い
- 利回り変動シミュレーション
- デュレーション計算

### 2. ポートフォリオ管理

```python
from portfolio import Portfolio

# ポートフォリオ作成
portfolio = Portfolio(initial_cash=10000000)  # 1000万円

# 資産購入
portfolio.buy("7203", stock, 100)   # 100株購入
portfolio.buy("JGB10", bond, 50)    # 50口購入

# 資産売却
portfolio.sell("7203", 50)          # 50株売却

# サマリー表示
portfolio.print_summary()
```

**機能:**
- 資産の購入・売却
- ポートフォリオ価値の追跡
- 資産配分の計算
- リスク・リターン分析
- シャープレシオ計算

### 3. シミュレーション

#### 基本シミュレーション

```python
from simulator import Simulator

simulator = Simulator(portfolio)
results = simulator.run(days=252, verbose=True)  # 1年間

# 統計情報表示
simulator.print_statistics()
```

#### モンテカルロシミュレーション

複数のシナリオで将来の資産価値を予測：

```python
from simulator import MonteCarloSimulator

mc_simulator = MonteCarloSimulator(portfolio)
mc_simulator.run(
    num_simulations=1000,  # 1000回のシミュレーション
    days=252,              # 各1年間
    verbose=True
)

# 結果サマリー
mc_simulator.print_summary()

# パーセンタイル分析
stats_50 = mc_simulator.get_percentile_results(50)  # 中央値
stats_95 = mc_simulator.get_percentile_results(95)  # 楽観的
stats_5 = mc_simulator.get_percentile_results(5)    # 悲観的
```

### 4. レポート生成

```python
from reporting import Report, PerformanceAnalyzer

# レポート生成
report = Report(portfolio, simulation_results)
report.print_report()

# ファイルに保存
report.save_report("portfolio_report.txt")

# パフォーマンス分析
analyzer = PerformanceAnalyzer(simulation_results)
analyzer.print_analysis()
```

## 使用例

### 例1: 基本的なポートフォリオ

```bash
cd examples
python basic_example.py
```

株式と債券を含む基本的なポートフォリオを作成し、1年間のシミュレーションを実行します。

### 例2: モンテカルロシミュレーション

```bash
cd examples
python monte_carlo_example.py
```

1000回のシミュレーションを実行し、将来の資産価値の分布を分析します。

### 例3: リバランシング戦略

```bash
cd examples
python rebalancing_example.py
```

四半期ごとにポートフォリオをリバランスする戦略を実装します。

## APIリファレンス

### Stock クラス

**メソッド:**
- `simulate_price_change(days=1)`: 価格変動をシミュレート
- `pay_dividend(shares)`: 配当金を計算
- `calculate_expected_return()`: 期待リターンを取得
- `calculate_risk()`: リスクを取得

### Bond クラス

**メソッド:**
- `update_yield(new_yield)`: 市場利回りを更新
- `pay_coupon(quantity)`: クーポン支払いを計算
- `time_step()`: 時間経過を処理
- `calculate_expected_return()`: 期待リターンを取得
- `calculate_risk()`: リスクを取得

### Portfolio クラス

**メソッド:**
- `buy(symbol, asset, quantity)`: 資産を購入
- `sell(symbol, quantity)`: 資産を売却
- `get_total_value()`: ポートフォリオの総価値を取得
- `get_asset_allocation()`: 資産配分を取得
- `get_returns()`: 累積リターンを取得
- `get_portfolio_risk()`: ポートフォリオリスクを取得
- `get_portfolio_expected_return()`: ポートフォリオ期待リターンを取得
- `calculate_sharpe_ratio(risk_free_rate)`: シャープレシオを計算
- `print_summary()`: サマリーを表示

### Simulator クラス

**メソッド:**
- `run(days, verbose)`: シミュレーションを実行
- `get_statistics()`: 統計情報を取得
- `print_statistics()`: 統計情報を表示

### MonteCarloSimulator クラス

**メソッド:**
- `run(num_simulations, days, verbose)`: モンテカルロシミュレーションを実行
- `get_percentile_results(percentile)`: パーセンタイル結果を取得
- `print_summary()`: サマリーを表示

## トラブルシューティング

### インポートエラー

```
ModuleNotFoundError: No module named 'numpy'
```

**解決方法:**
```bash
pip install -r requirements.txt
```

### 資金不足エラー

```
資金不足: 必要額 ¥500,000, 保有現金 ¥300,000
```

**解決方法:**
- 初期現金を増やす
- 購入数量を減らす

## さらなる情報

- [README.md](README.md): プロジェクト概要
- [examples/](examples/): 使用例スクリプト
- GitHub Issues: バグ報告や機能要望

## ライセンス

MIT License

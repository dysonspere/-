#!/usr/bin/env python3
"""
リバランシングの例
定期的にポートフォリオのバランスを調整する戦略
"""
import sys
sys.path.insert(0, '..')

from portfolio import Portfolio
from models.stock import Stock
from models.bond import Bond
from simulator import Simulator


def rebalance_portfolio(portfolio: Portfolio, target_stock_ratio: float = 0.6):
    """
    ポートフォリオをリバランス

    Args:
        portfolio: リバランス対象のポートフォリオ
        target_stock_ratio: 目標株式比率（デフォルト60%）
    """
    total_value = portfolio.get_total_value()
    target_stock_value = total_value * target_stock_ratio
    target_bond_value = total_value * (1 - target_stock_ratio)

    # 現在の株式・債券の価値を計算
    current_stock_value = 0
    current_bond_value = 0

    stocks = {}
    bonds = {}

    for symbol, (asset, quantity) in portfolio.holdings.items():
        asset_value = asset.current_price * quantity
        if isinstance(asset, Stock):
            current_stock_value += asset_value
            stocks[symbol] = (asset, quantity, asset_value)
        elif isinstance(asset, Bond):
            current_bond_value += asset_value
            bonds[symbol] = (asset, quantity, asset_value)

    print(f"\nリバランシング実行:")
    print(f"  現在: 株式 ¥{current_stock_value:,.0f} ({current_stock_value/total_value*100:.1f}%), "
          f"債券 ¥{current_bond_value:,.0f} ({current_bond_value/total_value*100:.1f}%)")
    print(f"  目標: 株式 ¥{target_stock_value:,.0f} ({target_stock_ratio*100:.1f}%), "
          f"債券 ¥{target_bond_value:,.0f} ({(1-target_stock_ratio)*100:.1f}%)")

    # 調整が必要な金額
    stock_adjustment = target_stock_value - current_stock_value
    bond_adjustment = target_bond_value - current_bond_value

    if abs(stock_adjustment) < total_value * 0.05:  # 5%未満の差異は無視
        print("  調整不要（差異が小さい）")
        return

    # 株式の調整
    if stock_adjustment > 0:
        # 株式を買い増し（債券を売却）
        print(f"  株式を ¥{stock_adjustment:,.0f} 買い増し")
        # 簡略化のため、最初の債券を売却
        if bonds:
            symbol, (asset, quantity, value) = list(bonds.items())[0]
            sell_quantity = int(stock_adjustment / asset.current_price)
            if sell_quantity > 0 and sell_quantity <= quantity:
                portfolio.sell(symbol, sell_quantity)
                # 最初の株式を購入
                if stocks:
                    stock_symbol, (stock_asset, _, _) = list(stocks.items())[0]
                    buy_quantity = int(stock_adjustment / stock_asset.current_price)
                    if buy_quantity > 0:
                        portfolio.buy(stock_symbol, stock_asset, buy_quantity)
    else:
        # 株式を減らし（株式を売却して債券を購入）
        print(f"  株式を ¥{abs(stock_adjustment):,.0f} 削減")
        if stocks:
            symbol, (asset, quantity, value) = list(stocks.items())[0]
            sell_quantity = int(abs(stock_adjustment) / asset.current_price)
            if sell_quantity > 0 and sell_quantity <= quantity:
                portfolio.sell(symbol, sell_quantity)
                # 債券を購入
                if bonds:
                    bond_symbol, (bond_asset, _, _) = list(bonds.items())[0]
                    buy_quantity = int(abs(stock_adjustment) / bond_asset.current_price)
                    if buy_quantity > 0:
                        portfolio.buy(bond_symbol, bond_asset, buy_quantity)


def main():
    print("="*60)
    print("リバランシング戦略の例")
    print("="*60)

    # ポートフォリオ作成（株式60%, 債券40%を目標）
    portfolio = Portfolio(initial_cash=10000000)

    # 初期投資
    toyota = Stock("7203", "トヨタ", 2500, 0.10, 0.25)
    apple = Stock("AAPL", "Apple", 18000, 0.12, 0.28)
    jgb = Bond("JGB10", "国債10年", 100, 0.015, 10)
    corporate = Bond("CORP5", "社債5年", 100, 0.025, 5)

    portfolio.buy("7203", toyota, 1200)   # 300万円
    portfolio.buy("AAPL", apple, 166)     # 約300万円
    portfolio.buy("JGB10", jgb, 20000)    # 約200万円
    portfolio.buy("CORP5", corporate, 20000)  # 約200万円

    print("\n初期ポートフォリオ:")
    portfolio.print_summary()

    # リバランシング戦略でシミュレーション
    print("\n" + "="*60)
    print("リバランシング付きシミュレーション（1年間、四半期ごとにリバランス）")
    print("="*60)

    total_days = 252
    rebalance_interval = 63  # 四半期ごと（約3ヶ月）

    for quarter in range(4):
        start_day = quarter * rebalance_interval
        end_day = min(start_day + rebalance_interval, total_days)
        days = end_day - start_day

        print(f"\n第{quarter + 1}四半期 (Day {start_day} - {end_day}):")

        # シミュレーション実行
        simulator = Simulator(portfolio)
        results = simulator.run(days=days, verbose=False)

        # 四半期末の状態
        print(f"  四半期末資産価値: ¥{portfolio.get_total_value():,.0f}")
        print(f"  累積リターン: {portfolio.get_returns():+.2f}%")

        # リバランシング（最終四半期以外）
        if quarter < 3:
            rebalance_portfolio(portfolio, target_stock_ratio=0.6)

    # 最終結果
    print("\n" + "="*60)
    print("最終結果")
    print("="*60)
    portfolio.print_summary()

    print("\n取引履歴:")
    print("-" * 60)
    for txn in portfolio.transaction_history:
        print(f"{txn['timestamp'].strftime('%Y-%m-%d %H:%M:%S')} "
              f"{txn['type']:4s} {txn['symbol']:8s} "
              f"{txn['quantity']:4d}株/口 @ ¥{txn['price']:,.0f}")


if __name__ == "__main__":
    main()

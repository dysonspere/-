#!/usr/bin/env python3
"""
モンテカルロシミュレーションの例
複数のシナリオで将来の資産価値を予測
"""
import sys
sys.path.insert(0, '..')

from portfolio import Portfolio
from models.stock import Stock
from models.bond import Bond
from simulator import MonteCarloSimulator


def main():
    print("="*60)
    print("モンテカルロシミュレーションの例")
    print("="*60)

    # ポートフォリオ作成
    portfolio = Portfolio(initial_cash=10000000)  # 1000万円

    # 株式60%、債券40%のバランス型ポートフォリオ
    print("\nバランス型ポートフォリオ（株式60%, 債券40%）を作成")

    # 株式（600万円相当）
    toyota = Stock("7203", "トヨタ", 2500, expected_return=0.10, volatility=0.25)
    sony = Stock("6758", "ソニー", 13000, expected_return=0.12, volatility=0.30)

    portfolio.buy("7203", toyota, 120)      # 30万円
    portfolio.buy("6758", sony, 40)         # 52万円

    # Apple（米国株）
    apple = Stock("AAPL", "Apple", 18000, expected_return=0.15, volatility=0.28)
    portfolio.buy("AAPL", apple, 100)       # 180万円

    # 債券（400万円相当）
    jgb10 = Bond("JGB10", "国債10年", 100, 0.015, 10)
    corporate = Bond("CORP5", "社債5年", 100, 0.03, 5)

    portfolio.buy("JGB10", jgb10, 2000)     # 約20万円
    portfolio.buy("CORP5", corporate, 1800) # 約18万円

    # ポートフォリオサマリー
    portfolio.print_summary()

    # モンテカルロシミュレーション実行
    print("\n" + "="*60)
    print("モンテカルロシミュレーション実行")
    print("="*60)
    print("1000回のシミュレーション、各1年間（252日）\n")

    mc_simulator = MonteCarloSimulator(portfolio)
    mc_simulator.run(num_simulations=1000, days=252, verbose=True)

    # 結果サマリー表示
    mc_simulator.print_summary()

    # パーセンタイル分析
    print("\n" + "="*60)
    print("詳細なパーセンタイル分析")
    print("="*60)

    percentiles = [1, 5, 10, 25, 50, 75, 90, 95, 99]

    print(f"\n{'パーセンタイル':>12} {'最終資産価値':>15} {'リターン':>10}")
    print("-" * 40)

    for p in percentiles:
        stats = mc_simulator.get_percentile_results(p)
        print(f"{p:10d}% ¥{stats['final_value']:14,.0f} {stats['final_return']:9.2f}%")

    # 投資判断のための情報
    print("\n" + "="*60)
    print("投資判断のための情報")
    print("="*60)

    stats_50 = mc_simulator.get_percentile_results(50)
    stats_5 = mc_simulator.get_percentile_results(5)
    stats_95 = mc_simulator.get_percentile_results(95)

    initial_value = portfolio.initial_cash

    print(f"\n初期投資額: ¥{initial_value:,.0f}")
    print(f"\n中央値（50%）のケース:")
    print(f"  最終資産: ¥{stats_50['final_value']:,.0f}")
    print(f"  リターン: {stats_50['final_return']:+.2f}%")

    print(f"\n楽観的（95%）のケース:")
    print(f"  最終資産: ¥{stats_95['final_value']:,.0f}")
    print(f"  リターン: {stats_95['final_return']:+.2f}%")
    print(f"  利益:     ¥{stats_95['final_value'] - initial_value:+,.0f}")

    print(f"\n悲観的（5%）のケース:")
    print(f"  最終資産: ¥{stats_5['final_value']:,.0f}")
    print(f"  リターン: {stats_5['final_return']:+.2f}%")
    print(f"  損失:     ¥{stats_5['final_value'] - initial_value:+,.0f}")

    # リスク評価
    loss_probability = sum(
        1 for sim in mc_simulator.all_simulations
        if sim[-1]['portfolio_value'] < initial_value
    ) / len(mc_simulator.all_simulations) * 100

    print(f"\n損失確率: {loss_probability:.1f}%")
    print(f"利益確率: {100 - loss_probability:.1f}%")

    print("\n" + "="*60)


if __name__ == "__main__":
    main()

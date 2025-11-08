#!/usr/bin/env python3
"""
基本的な使用例
株式と債券を含むポートフォリオを作成し、シミュレーションを実行
"""
import sys
sys.path.insert(0, '..')

from portfolio import Portfolio
from models.stock import Stock
from models.bond import Bond
from simulator import Simulator
from reporting import Report, PerformanceAnalyzer


def main():
    print("="*60)
    print("基本的な使用例")
    print("="*60)

    # 1. ポートフォリオを作成（初期資金500万円）
    portfolio = Portfolio(initial_cash=5000000)
    print(f"\n初期現金: ¥{portfolio.cash:,.0f}")

    # 2. 株式を追加
    print("\n株式を購入:")

    # トヨタ株
    toyota = Stock(
        symbol="7203",
        name="トヨタ自動車",
        current_price=2500,
        expected_return=0.08,  # 8%期待リターン
        volatility=0.20,        # 20%ボラティリティ
        dividend_yield=0.025    # 2.5%配当利回り
    )
    portfolio.buy("7203", toyota, 100)
    print(f"  トヨタ: 100株 @ ¥2,500 = ¥{100 * 2500:,}")

    # Apple株
    apple = Stock(
        symbol="AAPL",
        name="Apple Inc.",
        current_price=18000,
        expected_return=0.12,
        volatility=0.25,
        dividend_yield=0.005
    )
    portfolio.buy("AAPL", apple, 30)
    print(f"  Apple: 30株 @ ¥18,000 = ¥{30 * 18000:,}")

    # 3. 債券を追加
    print("\n債券を購入:")

    # 日本国債
    jgb = Bond(
        symbol="JGB10",
        name="日本国債10年",
        face_value=100,
        coupon_rate=0.015,      # 1.5%クーポン
        years_to_maturity=10
    )
    portfolio.buy("JGB10", jgb, 50)
    print(f"  日本国債: 50口 @ ¥{jgb.current_price:.2f}")

    # 4. ポートフォリオサマリー表示
    portfolio.print_summary()

    # 5. シミュレーション実行（1年間 = 252営業日）
    print("\n" + "="*60)
    print("1年間のシミュレーションを実行")
    print("="*60)

    simulator = Simulator(portfolio)
    results = simulator.run(days=252, verbose=True)

    # 6. 統計情報表示
    simulator.print_statistics()

    # 7. 最終ポートフォリオ
    print("\n最終ポートフォリオ:")
    portfolio.print_summary()

    # 8. パフォーマンス分析
    analyzer = PerformanceAnalyzer(results)
    analyzer.print_analysis()

    # 9. レポート生成
    print("\n" + "="*60)
    print("レポート生成")
    print("="*60)

    report = Report(portfolio, results)
    report.print_report()

    # レポートをファイルに保存
    # report.save_report("basic_example_report.txt")


if __name__ == "__main__":
    main()

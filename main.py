#!/usr/bin/env python3
"""
資産運用シミュレーター - メインエントリーポイント
株式と債券のポートフォリオ管理とシミュレーション
"""
import sys
from portfolio import Portfolio
from models.stock import Stock
from models.bond import Bond
from simulator import Simulator, MonteCarloSimulator
from utils import (
    plot_portfolio_value,
    create_sample_portfolio,
    create_conservative_portfolio,
    create_aggressive_portfolio
)


def print_menu():
    """メインメニューを表示"""
    print("\n" + "="*60)
    print("資産運用シミュレーター")
    print("="*60)
    print("1. サンプルポートフォリオでシミュレーション")
    print("2. 保守的ポートフォリオでシミュレーション（債券中心）")
    print("3. 積極的ポートフォリオでシミュレーション（株式中心）")
    print("4. カスタムポートフォリオ作成")
    print("5. モンテカルロシミュレーション")
    print("6. クイックデモ")
    print("0. 終了")
    print("="*60)


def quick_demo():
    """クイックデモを実行"""
    print("\n" + "="*60)
    print("クイックデモ実行中...")
    print("="*60 + "\n")

    # サンプルポートフォリオを作成
    portfolio = create_sample_portfolio()

    print("初期ポートフォリオ:")
    portfolio.print_summary()

    # 1年間のシミュレーション
    simulator = Simulator(portfolio)
    print("\n1年間（252営業日）のシミュレーションを実行中...\n")
    results = simulator.run(days=252, verbose=True)

    # 統計情報を表示
    simulator.print_statistics()

    # 最終ポートフォリオ
    print("最終ポートフォリオ:")
    portfolio.print_summary()

    # 簡易グラフ表示
    plot_portfolio_value(results)


def run_simulation(portfolio_type: str = "sample"):
    """
    シミュレーションを実行

    Args:
        portfolio_type: ポートフォリオタイプ（'sample', 'conservative', 'aggressive'）
    """
    # ポートフォリオ作成
    if portfolio_type == "conservative":
        portfolio = create_conservative_portfolio()
        print("\n保守的ポートフォリオを作成しました")
    elif portfolio_type == "aggressive":
        portfolio = create_aggressive_portfolio()
        print("\n積極的ポートフォリオを作成しました")
    else:
        portfolio = create_sample_portfolio()
        print("\nサンプルポートフォリオを作成しました")

    portfolio.print_summary()

    # シミュレーション期間を入力
    try:
        days = int(input("\nシミュレーション期間（日数、デフォルト252日=1年）: ") or "252")
    except ValueError:
        days = 252

    # シミュレーション実行
    simulator = Simulator(portfolio)
    results = simulator.run(days=days, verbose=True)

    # 統計情報表示
    simulator.print_statistics()

    # 最終ポートフォリオ
    print("最終ポートフォリオ:")
    portfolio.print_summary()

    # グラフ表示
    plot_portfolio_value(results)


def create_custom_portfolio():
    """カスタムポートフォリオを作成"""
    print("\n" + "="*60)
    print("カスタムポートフォリオ作成")
    print("="*60)

    try:
        initial_cash = float(input("初期現金残高（円）: ") or "10000000")
    except ValueError:
        initial_cash = 10000000

    portfolio = Portfolio(initial_cash=initial_cash)

    while True:
        print("\n資産を追加:")
        print("1. 株式")
        print("2. 債券")
        print("0. 完了")

        choice = input("選択: ")

        if choice == "0":
            break
        elif choice == "1":
            # 株式追加
            symbol = input("  ティッカーシンボル: ")
            name = input("  会社名: ")
            try:
                price = float(input("  現在価格: "))
                quantity = int(input("  購入数量: "))
                expected_return = float(input("  期待リターン（年率、例: 0.10 = 10%）: ") or "0.10")
                volatility = float(input("  ボラティリティ（年率、例: 0.20 = 20%）: ") or "0.20")
                dividend_yield = float(input("  配当利回り（年率、例: 0.02 = 2%）: ") or "0.02")

                stock = Stock(symbol, name, price, expected_return, volatility, dividend_yield)
                if portfolio.buy(symbol, stock, quantity):
                    print(f"  ✓ {symbol} を {quantity}株 購入しました")
            except ValueError:
                print("  入力エラー: 数値を入力してください")

        elif choice == "2":
            # 債券追加
            symbol = input("  債券シンボル: ")
            name = input("  債券名: ")
            try:
                face_value = float(input("  額面金額: "))
                coupon_rate = float(input("  クーポンレート（年率、例: 0.02 = 2%）: "))
                years_to_maturity = int(input("  償還までの年数: "))
                quantity = int(input("  購入数量: "))

                bond = Bond(symbol, name, face_value, coupon_rate, years_to_maturity)
                if portfolio.buy(symbol, bond, quantity):
                    print(f"  ✓ {symbol} を {quantity}口 購入しました")
            except ValueError:
                print("  入力エラー: 数値を入力してください")

    portfolio.print_summary()

    # シミュレーション実行
    if input("\nシミュレーションを実行しますか？ (y/n): ").lower() == 'y':
        try:
            days = int(input("シミュレーション期間（日数）: ") or "252")
        except ValueError:
            days = 252

        simulator = Simulator(portfolio)
        results = simulator.run(days=days, verbose=True)
        simulator.print_statistics()
        portfolio.print_summary()
        plot_portfolio_value(results)


def run_monte_carlo():
    """モンテカルロシミュレーションを実行"""
    print("\n" + "="*60)
    print("モンテカルロシミュレーション")
    print("="*60)

    # ポートフォリオタイプ選択
    print("\nポートフォリオタイプを選択:")
    print("1. サンプル（バランス型）")
    print("2. 保守的（債券中心）")
    print("3. 積極的（株式中心）")

    choice = input("選択（デフォルト1）: ") or "1"

    if choice == "2":
        portfolio = create_conservative_portfolio()
    elif choice == "3":
        portfolio = create_aggressive_portfolio()
    else:
        portfolio = create_sample_portfolio()

    portfolio.print_summary()

    # パラメータ入力
    try:
        num_simulations = int(input("\nシミュレーション回数（デフォルト1000）: ") or "1000")
        days = int(input("シミュレーション期間（日数、デフォルト252）: ") or "252")
    except ValueError:
        num_simulations = 1000
        days = 252

    # モンテカルロシミュレーション実行
    mc_simulator = MonteCarloSimulator(portfolio)
    mc_simulator.run(num_simulations=num_simulations, days=days, verbose=True)

    # 結果表示
    mc_simulator.print_summary()


def main():
    """メインエントリーポイント"""
    print("\n" + "#"*60)
    print("#" + " "*58 + "#")
    print("#" + "  資産運用シミュレーター  ".center(58) + "#")
    print("#" + "  Asset Management Simulator  ".center(58) + "#")
    print("#" + " "*58 + "#")
    print("#"*60)

    while True:
        print_menu()
        choice = input("\n選択してください: ")

        if choice == "0":
            print("\nシミュレーターを終了します。")
            sys.exit(0)
        elif choice == "1":
            run_simulation("sample")
        elif choice == "2":
            run_simulation("conservative")
        elif choice == "3":
            run_simulation("aggressive")
        elif choice == "4":
            create_custom_portfolio()
        elif choice == "5":
            run_monte_carlo()
        elif choice == "6":
            quick_demo()
        else:
            print("\n無効な選択です。もう一度選択してください。")

        input("\nEnterキーを押して続行...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nシミュレーターを終了します。")
        sys.exit(0)

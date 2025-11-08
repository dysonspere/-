"""ユーティリティ関数"""
import numpy as np
from typing import List, Tuple


def plot_portfolio_value(simulation_results: List[dict], title: str = "ポートフォリオ価値の推移"):
    """
    ポートフォリオ価値の推移を簡易的にテキストでプロット

    Args:
        simulation_results: シミュレーション結果
        title: グラフのタイトル
    """
    if not simulation_results:
        print("データがありません")
        return

    values = [r["portfolio_value"] for r in simulation_results]
    days = [r["day"] for r in simulation_results]

    # 簡易的なASCIIグラフを作成
    print(f"\n{title}")
    print("=" * 60)

    # 正規化（グラフの高さを30行に）
    max_val = max(values)
    min_val = min(values)
    height = 20

    if max_val == min_val:
        print("価値の変動がありません")
        return

    # グラフを描画
    normalized = [int((v - min_val) / (max_val - min_val) * height) for v in values]

    # サンプリング（最大60ポイント）
    step = max(1, len(values) // 60)
    sampled_days = days[::step]
    sampled_normalized = normalized[::step]
    sampled_values = values[::step]

    for h in range(height, -1, -1):
        line = ""
        for i, norm_val in enumerate(sampled_normalized):
            if norm_val == h:
                line += "*"
            elif norm_val > h:
                line += "|"
            else:
                line += " "

        # Y軸のラベル
        val_at_height = min_val + (max_val - min_val) * (h / height)
        print(f"{val_at_height:10.0f} | {line}")

    # X軸
    print(" " * 11 + "+" + "-" * len(sampled_normalized))
    print(" " * 11 + f"  0{' ' * (len(sampled_normalized) - 10)}{sampled_days[-1]}")
    print(" " * 11 + "  (日数)")
    print("=" * 60 + "\n")


def calculate_correlation(returns1: List[float], returns2: List[float]) -> float:
    """
    2つのリターン系列の相関係数を計算

    Args:
        returns1: リターン系列1
        returns2: リターン系列2

    Returns:
        相関係数
    """
    if len(returns1) != len(returns2) or len(returns1) < 2:
        return 0.0

    return np.corrcoef(returns1, returns2)[0, 1]


def format_currency(amount: float) -> str:
    """
    金額を日本円形式でフォーマット

    Args:
        amount: 金額

    Returns:
        フォーマットされた文字列
    """
    return f"¥{amount:,.2f}"


def format_percentage(value: float, decimal_places: int = 2) -> str:
    """
    パーセンテージをフォーマット

    Args:
        value: パーセンテージ値（0.05 = 5%）
        decimal_places: 小数点以下の桁数

    Returns:
        フォーマットされた文字列
    """
    return f"{value * 100:.{decimal_places}f}%"


def create_sample_portfolio():
    """サンプルポートフォリオを作成"""
    from portfolio import Portfolio
    from models.stock import Stock
    from models.bond import Bond

    portfolio = Portfolio(initial_cash=10000000)  # 1000万円

    # 日本株（テクノロジー）
    toyota = Stock("7203", "トヨタ自動車", 2500, expected_return=0.10, volatility=0.25)
    sony = Stock("6758", "ソニーグループ", 13000, expected_return=0.12, volatility=0.30)
    portfolio.buy("7203", toyota, 100)
    portfolio.buy("6758", sony, 50)

    # 米国株
    apple = Stock("AAPL", "Apple Inc.", 18000, expected_return=0.15, volatility=0.28)
    msft = Stock("MSFT", "Microsoft", 38000, expected_return=0.14, volatility=0.26)
    portfolio.buy("AAPL", apple, 20)
    portfolio.buy("MSFT", msft, 10)

    # 債券
    jgb = Bond("JGB10", "日本国債10年", 100, coupon_rate=0.015, years_to_maturity=10)
    corporate = Bond("CORP5", "社債5年", 100, coupon_rate=0.025, years_to_maturity=5)
    portfolio.buy("JGB10", jgb, 30)
    portfolio.buy("CORP5", corporate, 20)

    return portfolio


def create_conservative_portfolio():
    """保守的なポートフォリオを作成（債券中心）"""
    from portfolio import Portfolio
    from models.stock import Stock
    from models.bond import Bond

    portfolio = Portfolio(initial_cash=10000000)

    # 株式は少なめ
    toyota = Stock("7203", "トヨタ自動車", 2500, expected_return=0.08, volatility=0.20)
    portfolio.buy("7203", toyota, 50)

    # 債券を多めに
    jgb = Bond("JGB10", "日本国債10年", 100, coupon_rate=0.015, years_to_maturity=10)
    jgb5 = Bond("JGB5", "日本国債5年", 100, coupon_rate=0.012, years_to_maturity=5)
    corporate = Bond("CORP5", "社債5年", 100, coupon_rate=0.025, years_to_maturity=5)

    portfolio.buy("JGB10", jgb, 60)
    portfolio.buy("JGB5", jgb5, 40)
    portfolio.buy("CORP5", corporate, 30)

    return portfolio


def create_aggressive_portfolio():
    """積極的なポートフォリオを作成（株式中心）"""
    from portfolio import Portfolio
    from models.stock import Stock
    from models.bond import Bond

    portfolio = Portfolio(initial_cash=10000000)

    # 株式を多めに
    toyota = Stock("7203", "トヨタ自動車", 2500, expected_return=0.12, volatility=0.28)
    sony = Stock("6758", "ソニーグループ", 13000, expected_return=0.15, volatility=0.35)
    apple = Stock("AAPL", "Apple Inc.", 18000, expected_return=0.18, volatility=0.32)
    tsla = Stock("TSLA", "Tesla", 25000, expected_return=0.25, volatility=0.50)

    portfolio.buy("7203", toyota, 150)
    portfolio.buy("6758", sony, 80)
    portfolio.buy("AAPL", apple, 40)
    portfolio.buy("TSLA", tsla, 20)

    # 債券は少なめ
    jgb = Bond("JGB10", "日本国債10年", 100, coupon_rate=0.015, years_to_maturity=10)
    portfolio.buy("JGB10", jgb, 20)

    return portfolio

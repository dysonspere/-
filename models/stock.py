"""株式クラス"""
import numpy as np
from .asset import Asset


class Stock(Asset):
    """株式を表すクラス"""

    def __init__(self, symbol: str, name: str, current_price: float,
                 expected_return: float = 0.08, volatility: float = 0.20,
                 dividend_yield: float = 0.02):
        """
        Args:
            symbol: 株式のティッカーシンボル
            name: 会社名
            current_price: 現在の株価
            expected_return: 期待リターン（年率、デフォルト8%）
            volatility: ボラティリティ（年率、デフォルト20%）
            dividend_yield: 配当利回り（年率、デフォルト2%）
        """
        super().__init__(symbol, name, current_price)
        self.expected_return = expected_return
        self.volatility = volatility
        self.dividend_yield = dividend_yield

    def calculate_expected_return(self) -> float:
        """期待リターンを取得（年率）"""
        return self.expected_return

    def calculate_risk(self) -> float:
        """リスク（ボラティリティ）を取得（年率）"""
        return self.volatility

    def simulate_price_change(self, days: int = 1) -> float:
        """
        幾何ブラウン運動を使用して価格変動をシミュレート

        Args:
            days: シミュレーション日数

        Returns:
            新しい価格
        """
        dt = days / 252  # 年率を日次に変換（営業日252日）

        # 幾何ブラウン運動: S_t = S_0 * exp((μ - σ²/2)t + σ√t * Z)
        # μ: ドリフト（期待リターン）
        # σ: ボラティリティ
        # Z: 標準正規分布の乱数

        drift = (self.expected_return - 0.5 * self.volatility ** 2) * dt
        shock = self.volatility * np.sqrt(dt) * np.random.standard_normal()

        price_ratio = np.exp(drift + shock)
        new_price = self.current_price * price_ratio

        return max(new_price, 0.01)  # 価格は正の値を保つ

    def pay_dividend(self, shares: int) -> float:
        """
        配当金を計算

        Args:
            shares: 保有株数

        Returns:
            配当金額
        """
        annual_dividend = self.current_price * self.dividend_yield
        return annual_dividend * shares / 252  # 日次配当（簡易計算）

"""債券クラス"""
import numpy as np
from .asset import Asset


class Bond(Asset):
    """債券を表すクラス"""

    def __init__(self, symbol: str, name: str, face_value: float,
                 coupon_rate: float, years_to_maturity: int,
                 current_yield: float = None):
        """
        Args:
            symbol: 債券のシンボル
            name: 債券の名称
            face_value: 額面金額
            coupon_rate: クーポンレート（年率）
            years_to_maturity: 償還までの年数
            current_yield: 現在の市場利回り（指定しない場合はクーポンレートと同じ）
        """
        self.face_value = face_value
        self.coupon_rate = coupon_rate
        self.years_to_maturity = years_to_maturity
        self.current_yield = current_yield if current_yield is not None else coupon_rate

        # 債券価格を計算
        initial_price = self._calculate_bond_price()
        super().__init__(symbol, name, initial_price)

    def _calculate_bond_price(self) -> float:
        """
        債券の現在価格を計算（現在価値法）

        Returns:
            債券価格
        """
        if self.years_to_maturity == 0:
            return self.face_value

        # 年次クーポン支払い
        coupon_payment = self.face_value * self.coupon_rate

        # クーポン支払いの現在価値
        pv_coupons = 0
        for t in range(1, self.years_to_maturity + 1):
            pv_coupons += coupon_payment / ((1 + self.current_yield) ** t)

        # 額面の現在価値
        pv_face = self.face_value / ((1 + self.current_yield) ** self.years_to_maturity)

        return pv_coupons + pv_face

    def calculate_expected_return(self) -> float:
        """期待リターン（利回り）を取得"""
        return self.current_yield

    def calculate_risk(self) -> float:
        """
        債券のリスク（デュレーションベース）を計算
        簡易的にボラティリティを推定
        """
        # マコーレー・デュレーションの簡易計算
        duration = self._calculate_duration()

        # 金利変動を仮定（標準偏差1%程度）
        interest_rate_volatility = 0.01

        # 債券価格のボラティリティ = デュレーション × 金利ボラティリティ
        return duration * interest_rate_volatility

    def _calculate_duration(self) -> float:
        """マコーレー・デュレーションを計算"""
        if self.years_to_maturity == 0:
            return 0

        coupon_payment = self.face_value * self.coupon_rate
        bond_price = self.current_price

        weighted_cash_flows = 0
        for t in range(1, self.years_to_maturity + 1):
            cash_flow = coupon_payment if t < self.years_to_maturity else coupon_payment + self.face_value
            pv_cash_flow = cash_flow / ((1 + self.current_yield) ** t)
            weighted_cash_flows += t * pv_cash_flow

        duration = weighted_cash_flows / bond_price
        return duration

    def update_yield(self, new_yield: float):
        """
        市場利回りを更新し、債券価格を再計算

        Args:
            new_yield: 新しい市場利回り
        """
        self.current_yield = new_yield
        new_price = self._calculate_bond_price()
        self.update_price(new_price)

    def pay_coupon(self, quantity: int) -> float:
        """
        クーポン支払いを計算

        Args:
            quantity: 保有債券数

        Returns:
            クーポン支払い額
        """
        annual_coupon = self.face_value * self.coupon_rate
        return annual_coupon * quantity / 252  # 日次支払い（簡易計算）

    def time_step(self):
        """時間経過（1日）を処理"""
        # 償還日に近づく
        self.years_to_maturity -= 1/252
        if self.years_to_maturity <= 0:
            self.years_to_maturity = 0
            self.update_price(self.face_value)

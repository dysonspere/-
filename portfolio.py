"""ポートフォリオ管理クラス"""
from typing import Dict, List, Tuple
from datetime import datetime
from models.asset import Asset


class Portfolio:
    """投資ポートフォリオを管理するクラス"""

    def __init__(self, initial_cash: float = 0):
        """
        Args:
            initial_cash: 初期現金残高
        """
        self.cash = initial_cash
        self.initial_cash = initial_cash
        self.holdings: Dict[str, Tuple[Asset, int]] = {}  # {symbol: (asset, quantity)}
        self.transaction_history: List[Dict] = []
        self.value_history: List[Tuple[datetime, float]] = []
        self._record_value()

    def buy(self, symbol: str, asset: Asset, quantity: int) -> bool:
        """
        資産を購入

        Args:
            symbol: 資産のシンボル
            asset: 資産オブジェクト
            quantity: 購入数量

        Returns:
            購入成功の場合True
        """
        total_cost = asset.current_price * quantity

        if total_cost > self.cash:
            print(f"資金不足: 必要額 ¥{total_cost:,.0f}, 保有現金 ¥{self.cash:,.0f}")
            return False

        self.cash -= total_cost

        if symbol in self.holdings:
            existing_asset, existing_qty = self.holdings[symbol]
            self.holdings[symbol] = (asset, existing_qty + quantity)
        else:
            self.holdings[symbol] = (asset, quantity)

        self._record_transaction("BUY", symbol, quantity, asset.current_price)
        return True

    def sell(self, symbol: str, quantity: int) -> bool:
        """
        資産を売却

        Args:
            symbol: 資産のシンボル
            quantity: 売却数量

        Returns:
            売却成功の場合True
        """
        if symbol not in self.holdings:
            print(f"エラー: {symbol} を保有していません")
            return False

        asset, current_qty = self.holdings[symbol]

        if quantity > current_qty:
            print(f"エラー: 保有数量不足（保有: {current_qty}, 売却希望: {quantity}）")
            return False

        total_proceeds = asset.current_price * quantity
        self.cash += total_proceeds

        new_qty = current_qty - quantity
        if new_qty == 0:
            del self.holdings[symbol]
        else:
            self.holdings[symbol] = (asset, new_qty)

        self._record_transaction("SELL", symbol, quantity, asset.current_price)
        return True

    def get_total_value(self) -> float:
        """ポートフォリオの総価値を計算"""
        assets_value = sum(
            asset.current_price * quantity
            for asset, quantity in self.holdings.values()
        )
        return self.cash + assets_value

    def get_asset_allocation(self) -> Dict[str, float]:
        """資産配分を計算（パーセンテージ）"""
        total_value = self.get_total_value()
        if total_value == 0:
            return {}

        allocation = {"CASH": (self.cash / total_value) * 100}

        for symbol, (asset, quantity) in self.holdings.items():
            asset_value = asset.current_price * quantity
            allocation[symbol] = (asset_value / total_value) * 100

        return allocation

    def get_returns(self) -> float:
        """累積リターンを計算（パーセンテージ）"""
        if self.initial_cash == 0:
            return 0.0

        current_value = self.get_total_value()
        return ((current_value - self.initial_cash) / self.initial_cash) * 100

    def get_portfolio_risk(self) -> float:
        """ポートフォリオ全体のリスク（加重平均ボラティリティ）を計算"""
        total_value = self.get_total_value()
        if total_value == 0:
            return 0.0

        weighted_risk = 0.0
        for symbol, (asset, quantity) in self.holdings.items():
            asset_value = asset.current_price * quantity
            weight = asset_value / total_value
            weighted_risk += weight * asset.calculate_risk()

        return weighted_risk

    def get_portfolio_expected_return(self) -> float:
        """ポートフォリオの期待リターン（加重平均）を計算"""
        total_value = self.get_total_value()
        if total_value == 0:
            return 0.0

        weighted_return = 0.0
        for symbol, (asset, quantity) in self.holdings.items():
            asset_value = asset.current_price * quantity
            weight = asset_value / total_value
            weighted_return += weight * asset.calculate_expected_return()

        return weighted_return

    def calculate_sharpe_ratio(self, risk_free_rate: float = 0.01) -> float:
        """
        シャープレシオを計算

        Args:
            risk_free_rate: リスクフリーレート（デフォルト1%）

        Returns:
            シャープレシオ
        """
        portfolio_return = self.get_portfolio_expected_return()
        portfolio_risk = self.get_portfolio_risk()

        if portfolio_risk == 0:
            return 0.0

        return (portfolio_return - risk_free_rate) / portfolio_risk

    def _record_transaction(self, transaction_type: str, symbol: str,
                          quantity: int, price: float):
        """取引履歴を記録"""
        self.transaction_history.append({
            "timestamp": datetime.now(),
            "type": transaction_type,
            "symbol": symbol,
            "quantity": quantity,
            "price": price,
            "total": quantity * price
        })

    def _record_value(self):
        """ポートフォリオ価値の履歴を記録"""
        self.value_history.append((datetime.now(), self.get_total_value()))

    def get_summary(self) -> Dict:
        """ポートフォリオのサマリー情報を取得"""
        return {
            "total_value": self.get_total_value(),
            "cash": self.cash,
            "returns": self.get_returns(),
            "expected_return": self.get_portfolio_expected_return(),
            "risk": self.get_portfolio_risk(),
            "sharpe_ratio": self.calculate_sharpe_ratio(),
            "asset_allocation": self.get_asset_allocation(),
            "num_holdings": len(self.holdings)
        }

    def print_summary(self):
        """ポートフォリオのサマリーを表示"""
        summary = self.get_summary()

        print("\n" + "="*60)
        print("ポートフォリオサマリー")
        print("="*60)
        print(f"総資産価値: ¥{summary['total_value']:,.2f}")
        print(f"現金残高:   ¥{summary['cash']:,.2f}")
        print(f"累積リターン: {summary['returns']:.2f}%")
        print(f"期待リターン: {summary['expected_return']*100:.2f}%（年率）")
        print(f"リスク:       {summary['risk']*100:.2f}%（年率）")
        print(f"シャープレシオ: {summary['sharpe_ratio']:.2f}")
        print(f"\n保有銘柄数: {summary['num_holdings']}")

        print("\n" + "-"*60)
        print("資産配分:")
        print("-"*60)
        for symbol, allocation in summary['asset_allocation'].items():
            print(f"  {symbol:10s}: {allocation:6.2f}%")

        if self.holdings:
            print("\n" + "-"*60)
            print("保有資産詳細:")
            print("-"*60)
            for symbol, (asset, quantity) in self.holdings.items():
                value = asset.current_price * quantity
                print(f"  {symbol:10s}: {quantity:4d}株/口 @ ¥{asset.current_price:8.2f} = ¥{value:12,.2f}")

        print("="*60 + "\n")

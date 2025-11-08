"""資産の基底クラス"""
from abc import ABC, abstractmethod
from typing import List, Tuple
from datetime import datetime


class Asset(ABC):
    """すべての資産の基底クラス"""

    def __init__(self, symbol: str, name: str, current_price: float):
        """
        Args:
            symbol: 資産のシンボル（ティッカー）
            name: 資産の名称
            current_price: 現在価格
        """
        self.symbol = symbol
        self.name = name
        self.current_price = current_price
        self.price_history: List[Tuple[datetime, float]] = []
        self._add_to_history(current_price)

    def _add_to_history(self, price: float):
        """価格履歴に追加"""
        self.price_history.append((datetime.now(), price))

    def update_price(self, new_price: float):
        """価格を更新"""
        self.current_price = new_price
        self._add_to_history(new_price)

    @abstractmethod
    def calculate_expected_return(self) -> float:
        """期待リターンを計算（年率）"""
        pass

    @abstractmethod
    def calculate_risk(self) -> float:
        """リスク（ボラティリティ）を計算（年率）"""
        pass

    def get_price_history(self) -> List[float]:
        """価格履歴を取得"""
        return [price for _, price in self.price_history]

    def __repr__(self):
        return f"{self.__class__.__name__}(symbol='{self.symbol}', price={self.current_price:.2f})"

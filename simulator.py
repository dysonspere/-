"""資産運用シミュレーションエンジン"""
import numpy as np
from typing import Dict, List
from datetime import datetime, timedelta
from portfolio import Portfolio
from models.stock import Stock
from models.bond import Bond


class Simulator:
    """資産運用のシミュレーションを実行するクラス"""

    def __init__(self, portfolio: Portfolio):
        """
        Args:
            portfolio: シミュレーション対象のポートフォリオ
        """
        self.portfolio = portfolio
        self.simulation_results: List[Dict] = []

    def run(self, days: int = 252, verbose: bool = True) -> List[Dict]:
        """
        シミュレーションを実行

        Args:
            days: シミュレーション日数（デフォルト252日 = 1年）
            verbose: 進捗を表示するか

        Returns:
            日次シミュレーション結果のリスト
        """
        if verbose:
            print(f"\n{'='*60}")
            print(f"シミュレーション開始: {days}日間")
            print(f"{'='*60}\n")

        self.simulation_results = []
        initial_value = self.portfolio.get_total_value()

        for day in range(days):
            # 1日の開始時点での状態を記録
            day_start_value = self.portfolio.get_total_value()

            # 株式価格の更新（幾何ブラウン運動）
            for symbol, (asset, quantity) in list(self.portfolio.holdings.items()):
                if isinstance(asset, Stock):
                    new_price = asset.simulate_price_change(days=1)
                    asset.update_price(new_price)

                    # 配当金の支払い（四半期ごとに簡易的に処理）
                    if day > 0 and day % 63 == 0:  # 約3ヶ月ごと
                        dividend = asset.pay_dividend(quantity) * 63
                        self.portfolio.cash += dividend
                        if verbose and day % 126 == 0:
                            print(f"  Day {day}: {symbol} 配当金 ¥{dividend:,.2f}")

                elif isinstance(asset, Bond):
                    # 債券の時間経過処理
                    asset.time_step()

                    # 金利変動のシミュレーション（小さな変動）
                    if day > 0 and day % 21 == 0:  # 月次
                        yield_change = np.random.normal(0, 0.001)  # 0.1%の標準偏差
                        new_yield = max(0.001, asset.current_yield + yield_change)
                        asset.update_yield(new_yield)

                    # クーポン支払い（年1回を簡易的に四半期分割）
                    if day > 0 and day % 63 == 0:
                        coupon = asset.pay_coupon(quantity) * 63
                        self.portfolio.cash += coupon
                        if verbose and day % 126 == 0:
                            print(f"  Day {day}: {symbol} クーポン ¥{coupon:,.2f}")

            # 日次結果を記録
            day_end_value = self.portfolio.get_total_value()
            daily_return = ((day_end_value - day_start_value) / day_start_value * 100
                          if day_start_value > 0 else 0)

            result = {
                "day": day,
                "date": datetime.now() + timedelta(days=day),
                "portfolio_value": day_end_value,
                "daily_return": daily_return,
                "cumulative_return": ((day_end_value - initial_value) / initial_value * 100
                                     if initial_value > 0 else 0),
                "cash": self.portfolio.cash,
                "holdings_value": day_end_value - self.portfolio.cash
            }
            self.simulation_results.append(result)

            # 進捗表示（週次）
            if verbose and day % 21 == 0:
                print(f"  Day {day:3d}: ポートフォリオ価値 ¥{day_end_value:,.2f} "
                      f"(累積リターン: {result['cumulative_return']:+.2f}%)")

        # 最終結果の表示
        if verbose:
            final_result = self.simulation_results[-1]
            print(f"\n{'='*60}")
            print(f"シミュレーション完了")
            print(f"{'='*60}")
            print(f"初期資産: ¥{initial_value:,.2f}")
            print(f"最終資産: ¥{final_result['portfolio_value']:,.2f}")
            print(f"累積リターン: {final_result['cumulative_return']:+.2f}%")
            print(f"{'='*60}\n")

        return self.simulation_results

    def get_statistics(self) -> Dict:
        """シミュレーション結果の統計情報を取得"""
        if not self.simulation_results:
            return {}

        values = [r["portfolio_value"] for r in self.simulation_results]
        returns = [r["daily_return"] for r in self.simulation_results]

        return {
            "total_days": len(self.simulation_results),
            "initial_value": values[0],
            "final_value": values[-1],
            "min_value": min(values),
            "max_value": max(values),
            "avg_value": np.mean(values),
            "total_return": ((values[-1] - values[0]) / values[0] * 100) if values[0] > 0 else 0,
            "avg_daily_return": np.mean(returns),
            "volatility": np.std(returns),
            "max_drawdown": self._calculate_max_drawdown(values),
            "sharpe_ratio": self._calculate_sharpe_ratio(returns)
        }

    def _calculate_max_drawdown(self, values: List[float]) -> float:
        """最大ドローダウンを計算"""
        peak = values[0]
        max_dd = 0

        for value in values:
            if value > peak:
                peak = value
            dd = (peak - value) / peak * 100
            if dd > max_dd:
                max_dd = dd

        return max_dd

    def _calculate_sharpe_ratio(self, returns: List[float],
                               risk_free_rate: float = 0.01) -> float:
        """
        シャープレシオを計算

        Args:
            returns: 日次リターンのリスト
            risk_free_rate: リスクフリーレート（年率）

        Returns:
            シャープレシオ
        """
        if not returns or np.std(returns) == 0:
            return 0.0

        daily_rf = risk_free_rate / 252
        excess_returns = [r / 100 - daily_rf for r in returns]
        avg_excess_return = np.mean(excess_returns)
        std_excess_return = np.std(excess_returns)

        if std_excess_return == 0:
            return 0.0

        # 年率換算
        sharpe = (avg_excess_return / std_excess_return) * np.sqrt(252)
        return sharpe

    def print_statistics(self):
        """統計情報を表示"""
        stats = self.get_statistics()

        if not stats:
            print("シミュレーション結果がありません")
            return

        print("\n" + "="*60)
        print("シミュレーション統計")
        print("="*60)
        print(f"シミュレーション期間: {stats['total_days']}日")
        print(f"初期資産:     ¥{stats['initial_value']:,.2f}")
        print(f"最終資産:     ¥{stats['final_value']:,.2f}")
        print(f"最高資産:     ¥{stats['max_value']:,.2f}")
        print(f"最低資産:     ¥{stats['min_value']:,.2f}")
        print(f"平均資産:     ¥{stats['avg_value']:,.2f}")
        print(f"\n総リターン:   {stats['total_return']:+.2f}%")
        print(f"平均日次リターン: {stats['avg_daily_return']:+.4f}%")
        print(f"ボラティリティ:   {stats['volatility']:.4f}%")
        print(f"最大ドローダウン: {stats['max_drawdown']:.2f}%")
        print(f"シャープレシオ:   {stats['sharpe_ratio']:.2f}")
        print("="*60 + "\n")


class MonteCarloSimulator:
    """モンテカルロシミュレーション"""

    def __init__(self, portfolio: Portfolio):
        """
        Args:
            portfolio: シミュレーション対象のポートフォリオ（テンプレート）
        """
        self.portfolio_template = portfolio
        self.all_simulations: List[List[Dict]] = []

    def run(self, num_simulations: int = 1000, days: int = 252,
            verbose: bool = True) -> List[List[Dict]]:
        """
        モンテカルロシミュレーションを実行

        Args:
            num_simulations: シミュレーション回数
            days: 各シミュレーションの日数
            verbose: 進捗を表示するか

        Returns:
            全シミュレーション結果
        """
        if verbose:
            print(f"\n{'='*60}")
            print(f"モンテカルロシミュレーション開始")
            print(f"シミュレーション回数: {num_simulations}, 期間: {days}日")
            print(f"{'='*60}\n")

        self.all_simulations = []

        for i in range(num_simulations):
            # ポートフォリオのコピーを作成（深いコピーが必要）
            # 簡易的に新しいポートフォリオを作成
            sim_portfolio = self._clone_portfolio()
            simulator = Simulator(sim_portfolio)
            results = simulator.run(days=days, verbose=False)
            self.all_simulations.append(results)

            if verbose and (i + 1) % 100 == 0:
                print(f"  完了: {i + 1}/{num_simulations}")

        if verbose:
            print(f"\n{'='*60}")
            print("モンテカルロシミュレーション完了")
            print(f"{'='*60}\n")

        return self.all_simulations

    def _clone_portfolio(self) -> Portfolio:
        """ポートフォリオのクローンを作成"""
        new_portfolio = Portfolio(self.portfolio_template.cash)
        new_portfolio.initial_cash = self.portfolio_template.initial_cash

        for symbol, (asset, quantity) in self.portfolio_template.holdings.items():
            # 資産のクローンを作成
            if isinstance(asset, Stock):
                new_asset = Stock(
                    asset.symbol, asset.name, asset.current_price,
                    asset.expected_return, asset.volatility, asset.dividend_yield
                )
            elif isinstance(asset, Bond):
                new_asset = Bond(
                    asset.symbol, asset.name, asset.face_value,
                    asset.coupon_rate, asset.years_to_maturity, asset.current_yield
                )
            else:
                continue

            new_portfolio.holdings[symbol] = (new_asset, quantity)

        return new_portfolio

    def get_percentile_results(self, percentile: float = 50) -> Dict:
        """
        指定されたパーセンタイルの結果を取得

        Args:
            percentile: パーセンタイル（0-100）

        Returns:
            統計情報
        """
        if not self.all_simulations:
            return {}

        final_values = [sim[-1]["portfolio_value"] for sim in self.all_simulations]
        final_returns = [sim[-1]["cumulative_return"] for sim in self.all_simulations]

        return {
            "percentile": percentile,
            "final_value": np.percentile(final_values, percentile),
            "final_return": np.percentile(final_returns, percentile),
            "mean_final_value": np.mean(final_values),
            "median_final_value": np.median(final_values),
            "std_final_value": np.std(final_values),
            "min_final_value": np.min(final_values),
            "max_final_value": np.max(final_values)
        }

    def print_summary(self):
        """モンテカルロシミュレーションのサマリーを表示"""
        if not self.all_simulations:
            print("シミュレーション結果がありません")
            return

        print("\n" + "="*60)
        print("モンテカルロシミュレーション結果")
        print("="*60)

        for percentile in [5, 25, 50, 75, 95]:
            stats = self.get_percentile_results(percentile)
            print(f"{percentile:2d}パーセンタイル: ¥{stats['final_value']:,.2f} "
                  f"(リターン: {stats['final_return']:+.2f}%)")

        overall = self.get_percentile_results(50)
        print(f"\n平均最終資産: ¥{overall['mean_final_value']:,.2f}")
        print(f"標準偏差:     ¥{overall['std_final_value']:,.2f}")
        print(f"最小値:       ¥{overall['min_final_value']:,.2f}")
        print(f"最大値:       ¥{overall['max_final_value']:,.2f}")
        print("="*60 + "\n")

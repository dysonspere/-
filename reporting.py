"""レポート生成機能"""
from typing import List, Dict
from datetime import datetime
from portfolio import Portfolio
from simulator import Simulator


class Report:
    """シミュレーション結果のレポートを生成"""

    def __init__(self, portfolio: Portfolio, simulation_results: List[Dict] = None):
        """
        Args:
            portfolio: ポートフォリオ
            simulation_results: シミュレーション結果（オプション）
        """
        self.portfolio = portfolio
        self.simulation_results = simulation_results or []

    def generate_summary_report(self) -> str:
        """サマリーレポートを生成"""
        report = []
        report.append("=" * 80)
        report.append("資産運用シミュレーション レポート")
        report.append("=" * 80)
        report.append(f"生成日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}")
        report.append("")

        # ポートフォリオサマリー
        summary = self.portfolio.get_summary()
        report.append("-" * 80)
        report.append("ポートフォリオ概要")
        report.append("-" * 80)
        report.append(f"総資産価値:     ¥{summary['total_value']:,.2f}")
        report.append(f"現金残高:       ¥{summary['cash']:,.2f}")
        report.append(f"累積リターン:   {summary['returns']:+.2f}%")
        report.append(f"期待リターン:   {summary['expected_return']*100:.2f}% (年率)")
        report.append(f"リスク:         {summary['risk']*100:.2f}% (年率)")
        report.append(f"シャープレシオ: {summary['sharpe_ratio']:.2f}")
        report.append(f"保有銘柄数:     {summary['num_holdings']}")
        report.append("")

        # 資産配分
        report.append("-" * 80)
        report.append("資産配分")
        report.append("-" * 80)
        for symbol, allocation in summary['asset_allocation'].items():
            bar = "█" * int(allocation / 2)  # 2%ごとに1文字
            report.append(f"{symbol:12s} {allocation:6.2f}% |{bar}")
        report.append("")

        # 保有資産詳細
        if self.portfolio.holdings:
            report.append("-" * 80)
            report.append("保有資産詳細")
            report.append("-" * 80)
            report.append(f"{'シンボル':<12} {'数量':>8} {'単価':>12} {'評価額':>15} {'期待リターン':>12} {'リスク':>10}")
            report.append("-" * 80)

            for symbol, (asset, quantity) in self.portfolio.holdings.items():
                value = asset.current_price * quantity
                exp_ret = asset.calculate_expected_return() * 100
                risk = asset.calculate_risk() * 100

                report.append(
                    f"{symbol:<12} {quantity:8d} "
                    f"¥{asset.current_price:11,.2f} "
                    f"¥{value:14,.2f} "
                    f"{exp_ret:10.2f}% "
                    f"{risk:9.2f}%"
                )
            report.append("")

        # 取引履歴
        if self.portfolio.transaction_history:
            report.append("-" * 80)
            report.append("取引履歴（最新10件）")
            report.append("-" * 80)
            report.append(f"{'日時':<20} {'種別':<6} {'シンボル':<12} {'数量':>8} {'単価':>12} {'合計':>15}")
            report.append("-" * 80)

            for txn in self.portfolio.transaction_history[-10:]:
                report.append(
                    f"{txn['timestamp'].strftime('%Y-%m-%d %H:%M:%S'):<20} "
                    f"{txn['type']:<6} "
                    f"{txn['symbol']:<12} "
                    f"{txn['quantity']:8d} "
                    f"¥{txn['price']:11,.2f} "
                    f"¥{txn['total']:14,.2f}"
                )
            report.append("")

        # シミュレーション結果
        if self.simulation_results:
            report.append("-" * 80)
            report.append("シミュレーション結果")
            report.append("-" * 80)

            initial_value = self.simulation_results[0]['portfolio_value']
            final_value = self.simulation_results[-1]['portfolio_value']
            total_return = ((final_value - initial_value) / initial_value * 100
                          if initial_value > 0 else 0)

            report.append(f"シミュレーション期間: {len(self.simulation_results)}日")
            report.append(f"初期資産:   ¥{initial_value:,.2f}")
            report.append(f"最終資産:   ¥{final_value:,.2f}")
            report.append(f"総リターン: {total_return:+.2f}%")

            # 日次リターンの統計
            daily_returns = [r['daily_return'] for r in self.simulation_results]
            import numpy as np
            report.append(f"\n日次リターン統計:")
            report.append(f"  平均: {np.mean(daily_returns):+.4f}%")
            report.append(f"  標準偏差: {np.std(daily_returns):.4f}%")
            report.append(f"  最大: {np.max(daily_returns):+.4f}%")
            report.append(f"  最小: {np.min(daily_returns):+.4f}%")
            report.append("")

        report.append("=" * 80)
        report.append("レポート終了")
        report.append("=" * 80)

        return "\n".join(report)

    def save_report(self, filename: str = None):
        """
        レポートをファイルに保存

        Args:
            filename: ファイル名（指定しない場合は自動生成）
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"portfolio_report_{timestamp}.txt"

        report_content = self.generate_summary_report()

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report_content)

        print(f"レポートを保存しました: {filename}")
        return filename

    def print_report(self):
        """レポートを画面に表示"""
        print(self.generate_summary_report())


class PerformanceAnalyzer:
    """パフォーマンス分析ツール"""

    def __init__(self, simulation_results: List[Dict]):
        """
        Args:
            simulation_results: シミュレーション結果
        """
        self.results = simulation_results

    def analyze_drawdown_periods(self) -> List[Dict]:
        """ドローダウン期間を分析"""
        if not self.results:
            return []

        values = [r['portfolio_value'] for r in self.results]
        drawdown_periods = []
        peak = values[0]
        peak_day = 0
        in_drawdown = False
        dd_start = 0

        for i, value in enumerate(values):
            if value > peak:
                # 新高値更新
                if in_drawdown:
                    # ドローダウン終了
                    drawdown_periods.append({
                        'start_day': dd_start,
                        'end_day': i - 1,
                        'duration': i - dd_start,
                        'max_drawdown': ((peak - min(values[dd_start:i])) / peak * 100)
                    })
                    in_drawdown = False

                peak = value
                peak_day = i
            elif value < peak:
                if not in_drawdown:
                    # ドローダウン開始
                    in_drawdown = True
                    dd_start = peak_day

        return drawdown_periods

    def analyze_volatility_clustering(self, window: int = 20) -> List[Dict]:
        """ボラティリティクラスタリングを分析"""
        if len(self.results) < window:
            return []

        import numpy as np
        returns = [r['daily_return'] for r in self.results]
        volatility_series = []

        for i in range(window, len(returns)):
            window_returns = returns[i-window:i]
            vol = np.std(window_returns)
            volatility_series.append({
                'day': i,
                'volatility': vol,
                'avg_return': np.mean(window_returns)
            })

        return volatility_series

    def get_best_and_worst_days(self, n: int = 5) -> Dict:
        """
        最良・最悪の日を取得

        Args:
            n: 取得する日数

        Returns:
            最良・最悪の日の情報
        """
        if not self.results:
            return {'best': [], 'worst': []}

        sorted_by_return = sorted(self.results, key=lambda x: x['daily_return'], reverse=True)

        return {
            'best': sorted_by_return[:n],
            'worst': sorted_by_return[-n:][::-1]
        }

    def print_analysis(self):
        """分析結果を表示"""
        print("\n" + "="*60)
        print("パフォーマンス分析")
        print("="*60)

        # ドローダウン分析
        drawdowns = self.analyze_drawdown_periods()
        if drawdowns:
            print("\nドローダウン期間:")
            print(f"  総ドローダウン回数: {len(drawdowns)}")

            max_dd_period = max(drawdowns, key=lambda x: x['max_drawdown'])
            print(f"  最大ドローダウン: {max_dd_period['max_drawdown']:.2f}%")
            print(f"    期間: Day {max_dd_period['start_day']} - {max_dd_period['end_day']} "
                  f"({max_dd_period['duration']}日)")

            longest_dd_period = max(drawdowns, key=lambda x: x['duration'])
            print(f"  最長ドローダウン期間: {longest_dd_period['duration']}日")
            print(f"    最大下落: {longest_dd_period['max_drawdown']:.2f}%")

        # 最良・最悪の日
        extremes = self.get_best_and_worst_days(3)
        print("\n最良の3日:")
        for i, day in enumerate(extremes['best'], 1):
            print(f"  {i}. Day {day['day']}: {day['daily_return']:+.2f}% "
                  f"(資産価値: ¥{day['portfolio_value']:,.2f})")

        print("\n最悪の3日:")
        for i, day in enumerate(extremes['worst'], 1):
            print(f"  {i}. Day {day['day']}: {day['daily_return']:+.2f}% "
                  f"(資産価値: ¥{day['portfolio_value']:,.2f})")

        print("="*60 + "\n")

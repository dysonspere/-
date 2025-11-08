/**
 * 資産運用シミュレーションエンジン
 */
import { Portfolio } from './Portfolio';
import { Stock } from '../models/Stock';
import { Bond } from '../models/Bond';

export interface SimulationResult {
  day: number;
  date: Date;
  portfolioValue: number;
  dailyReturn: number;
  cumulativeReturn: number;
  cash: number;
  holdingsValue: number;
}

export interface SimulationStatistics {
  totalDays: number;
  initialValue: number;
  finalValue: number;
  minValue: number;
  maxValue: number;
  avgValue: number;
  totalReturn: number;
  avgDailyReturn: number;
  volatility: number;
  maxDrawdown: number;
  sharpeRatio: number;
}

export class Simulator {
  portfolio: Portfolio;
  simulationResults: SimulationResult[];

  constructor(portfolio: Portfolio) {
    this.portfolio = portfolio;
    this.simulationResults = [];
  }

  /**
   * シミュレーションを実行
   */
  run(days: number = 252, onProgress?: (day: number, total: number) => void): SimulationResult[] {
    this.simulationResults = [];
    const initialValue = this.portfolio.getTotalValue();

    for (let day = 0; day < days; day++) {
      const dayStartValue = this.portfolio.getTotalValue();

      // 株式価格の更新
      this.portfolio.holdings.forEach(({ asset, quantity }) => {
        if (asset instanceof Stock) {
          const newPrice = asset.simulatePriceChange(1);
          asset.updatePrice(newPrice);

          // 配当金の支払い（四半期ごと）
          if (day > 0 && day % 63 === 0) {
            const dividend = asset.payDividend(quantity) * 63;
            this.portfolio.cash += dividend;
          }
        } else if (asset instanceof Bond) {
          // 債券の時間経過処理
          asset.timeStep();

          // 金利変動のシミュレーション（月次）
          if (day > 0 && day % 21 === 0) {
            const yieldChange = this.randomNormal() * 0.001;
            const newYield = Math.max(0.001, asset.currentYield + yieldChange);
            asset.updateYield(newYield);
          }

          // クーポン支払い（四半期ごと）
          if (day > 0 && day % 63 === 0) {
            const coupon = asset.payCoupon(quantity) * 63;
            this.portfolio.cash += coupon;
          }
        }
      });

      // 日次結果を記録
      const dayEndValue = this.portfolio.getTotalValue();
      const dailyReturn =
        dayStartValue > 0 ? ((dayEndValue - dayStartValue) / dayStartValue) * 100 : 0;
      const cumulativeReturn =
        initialValue > 0 ? ((dayEndValue - initialValue) / initialValue) * 100 : 0;

      this.simulationResults.push({
        day,
        date: new Date(Date.now() + day * 24 * 60 * 60 * 1000),
        portfolioValue: dayEndValue,
        dailyReturn,
        cumulativeReturn,
        cash: this.portfolio.cash,
        holdingsValue: dayEndValue - this.portfolio.cash,
      });

      if (onProgress) {
        onProgress(day + 1, days);
      }
    }

    return this.simulationResults;
  }

  /**
   * シミュレーション結果の統計情報を取得
   */
  getStatistics(): SimulationStatistics | null {
    if (this.simulationResults.length === 0) {
      return null;
    }

    const values = this.simulationResults.map(r => r.portfolioValue);
    const returns = this.simulationResults.map(r => r.dailyReturn);

    return {
      totalDays: this.simulationResults.length,
      initialValue: values[0],
      finalValue: values[values.length - 1],
      minValue: Math.min(...values),
      maxValue: Math.max(...values),
      avgValue: this.mean(values),
      totalReturn:
        values[0] > 0 ? ((values[values.length - 1] - values[0]) / values[0]) * 100 : 0,
      avgDailyReturn: this.mean(returns),
      volatility: this.standardDeviation(returns),
      maxDrawdown: this.calculateMaxDrawdown(values),
      sharpeRatio: this.calculateSharpeRatio(returns),
    };
  }

  /**
   * 最大ドローダウンを計算
   */
  private calculateMaxDrawdown(values: number[]): number {
    let peak = values[0];
    let maxDD = 0;

    for (const value of values) {
      if (value > peak) {
        peak = value;
      }
      const dd = ((peak - value) / peak) * 100;
      if (dd > maxDD) {
        maxDD = dd;
      }
    }

    return maxDD;
  }

  /**
   * シャープレシオを計算
   */
  private calculateSharpeRatio(returns: number[], riskFreeRate: number = 0.01): number {
    if (returns.length === 0) {
      return 0;
    }

    const dailyRF = riskFreeRate / 252;
    const excessReturns = returns.map(r => r / 100 - dailyRF);
    const avgExcessReturn = this.mean(excessReturns);
    const stdExcessReturn = this.standardDeviation(excessReturns);

    if (stdExcessReturn === 0) {
      return 0;
    }

    // 年率換算
    return (avgExcessReturn / stdExcessReturn) * Math.sqrt(252);
  }

  /**
   * 標準正規分布の乱数を生成
   */
  private randomNormal(): number {
    const u1 = Math.random();
    const u2 = Math.random();
    return Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * u2);
  }

  /**
   * 平均値を計算
   */
  private mean(values: number[]): number {
    return values.reduce((sum, val) => sum + val, 0) / values.length;
  }

  /**
   * 標準偏差を計算
   */
  private standardDeviation(values: number[]): number {
    const avg = this.mean(values);
    const squareDiffs = values.map(value => Math.pow(value - avg, 2));
    const avgSquareDiff = this.mean(squareDiffs);
    return Math.sqrt(avgSquareDiff);
  }
}

export interface MonteCarloResults {
  simulations: SimulationResult[][];
  percentiles: {
    p5: number;
    p25: number;
    p50: number;
    p75: number;
    p95: number;
  };
  statistics: {
    meanFinalValue: number;
    medianFinalValue: number;
    stdFinalValue: number;
    minFinalValue: number;
    maxFinalValue: number;
  };
}

/**
 * モンテカルロシミュレーター
 */
export class MonteCarloSimulator {
  portfolioTemplate: Portfolio;
  allSimulations: SimulationResult[][];

  constructor(portfolio: Portfolio) {
    this.portfolioTemplate = portfolio;
    this.allSimulations = [];
  }

  /**
   * モンテカルロシミュレーションを実行
   */
  run(
    numSimulations: number = 1000,
    days: number = 252,
    onProgress?: (current: number, total: number) => void
  ): MonteCarloResults {
    this.allSimulations = [];

    for (let i = 0; i < numSimulations; i++) {
      const simPortfolio = this.portfolioTemplate.clone();
      const simulator = new Simulator(simPortfolio);
      const results = simulator.run(days);
      this.allSimulations.push(results);

      if (onProgress) {
        onProgress(i + 1, numSimulations);
      }
    }

    return this.getResults();
  }

  /**
   * モンテカルロ結果を取得
   */
  private getResults(): MonteCarloResults {
    const finalValues = this.allSimulations.map(sim => sim[sim.length - 1].portfolioValue);
    finalValues.sort((a, b) => a - b);

    const getPercentile = (p: number): number => {
      const index = Math.floor((finalValues.length * p) / 100);
      return finalValues[index];
    };

    return {
      simulations: this.allSimulations,
      percentiles: {
        p5: getPercentile(5),
        p25: getPercentile(25),
        p50: getPercentile(50),
        p75: getPercentile(75),
        p95: getPercentile(95),
      },
      statistics: {
        meanFinalValue: this.mean(finalValues),
        medianFinalValue: getPercentile(50),
        stdFinalValue: this.standardDeviation(finalValues),
        minFinalValue: Math.min(...finalValues),
        maxFinalValue: Math.max(...finalValues),
      },
    };
  }

  private mean(values: number[]): number {
    return values.reduce((sum, val) => sum + val, 0) / values.length;
  }

  private standardDeviation(values: number[]): number {
    const avg = this.mean(values);
    const squareDiffs = values.map(value => Math.pow(value - avg, 2));
    const avgSquareDiff = this.mean(squareDiffs);
    return Math.sqrt(avgSquareDiff);
  }
}

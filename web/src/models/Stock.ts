/**
 * 株式クラス
 */
import { Asset } from './Asset';

export class Stock extends Asset {
  expectedReturn: number;
  volatility: number;
  dividendYield: number;

  constructor(
    symbol: string,
    name: string,
    currentPrice: number,
    expectedReturn: number = 0.08,
    volatility: number = 0.20,
    dividendYield: number = 0.02
  ) {
    super(symbol, name, currentPrice);
    this.expectedReturn = expectedReturn;
    this.volatility = volatility;
    this.dividendYield = dividendYield;
  }

  calculateExpectedReturn(): number {
    return this.expectedReturn;
  }

  calculateRisk(): number {
    return this.volatility;
  }

  /**
   * 幾何ブラウン運動を使用して価格変動をシミュレート
   */
  simulatePriceChange(days: number = 1): number {
    const dt = days / 252; // 年率を日次に変換（営業日252日）

    // 幾何ブラウン運動: S_t = S_0 * exp((μ - σ²/2)t + σ√t * Z)
    const drift = (this.expectedReturn - 0.5 * this.volatility ** 2) * dt;
    const shock = this.volatility * Math.sqrt(dt) * this.randomNormal();

    const priceRatio = Math.exp(drift + shock);
    const newPrice = this.currentPrice * priceRatio;

    return Math.max(newPrice, 0.01); // 価格は正の値を保つ
  }

  /**
   * 標準正規分布の乱数を生成（Box-Muller変換）
   */
  private randomNormal(): number {
    const u1 = Math.random();
    const u2 = Math.random();
    return Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * u2);
  }

  /**
   * 配当金を計算
   */
  payDividend(shares: number): number {
    const annualDividend = this.currentPrice * this.dividendYield;
    return (annualDividend * shares) / 252; // 日次配当（簡易計算）
  }

  clone(): Stock {
    return new Stock(
      this.symbol,
      this.name,
      this.currentPrice,
      this.expectedReturn,
      this.volatility,
      this.dividendYield
    );
  }
}

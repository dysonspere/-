/**
 * ポートフォリオ管理クラス
 */
import { Asset } from '../models/Asset';

export interface Holding {
  asset: Asset;
  quantity: number;
}

export interface Transaction {
  timestamp: Date;
  type: 'BUY' | 'SELL';
  symbol: string;
  quantity: number;
  price: number;
  total: number;
}

export interface PortfolioSummary {
  totalValue: number;
  cash: number;
  returns: number;
  expectedReturn: number;
  risk: number;
  sharpeRatio: number;
  assetAllocation: Record<string, number>;
  numHoldings: number;
}

export class Portfolio {
  cash: number;
  initialCash: number;
  holdings: Map<string, Holding>;
  transactionHistory: Transaction[];
  valueHistory: Array<{ timestamp: Date; value: number }>;

  constructor(initialCash: number = 0) {
    this.cash = initialCash;
    this.initialCash = initialCash;
    this.holdings = new Map();
    this.transactionHistory = [];
    this.valueHistory = [];
    this.recordValue();
  }

  /**
   * 資産を購入
   */
  buy(symbol: string, asset: Asset, quantity: number): boolean {
    const totalCost = asset.currentPrice * quantity;

    if (totalCost > this.cash) {
      console.error(
        `資金不足: 必要額 ¥${totalCost.toLocaleString()}, 保有現金 ¥${this.cash.toLocaleString()}`
      );
      return false;
    }

    this.cash -= totalCost;

    const existing = this.holdings.get(symbol);
    if (existing) {
      this.holdings.set(symbol, {
        asset,
        quantity: existing.quantity + quantity,
      });
    } else {
      this.holdings.set(symbol, { asset, quantity });
    }

    this.recordTransaction('BUY', symbol, quantity, asset.currentPrice);
    return true;
  }

  /**
   * 資産を売却
   */
  sell(symbol: string, quantity: number): boolean {
    const holding = this.holdings.get(symbol);
    if (!holding) {
      console.error(`エラー: ${symbol} を保有していません`);
      return false;
    }

    if (quantity > holding.quantity) {
      console.error(
        `エラー: 保有数量不足（保有: ${holding.quantity}, 売却希望: ${quantity}）`
      );
      return false;
    }

    const totalProceeds = holding.asset.currentPrice * quantity;
    this.cash += totalProceeds;

    const newQuantity = holding.quantity - quantity;
    if (newQuantity === 0) {
      this.holdings.delete(symbol);
    } else {
      this.holdings.set(symbol, { asset: holding.asset, quantity: newQuantity });
    }

    this.recordTransaction('SELL', symbol, quantity, holding.asset.currentPrice);
    return true;
  }

  /**
   * ポートフォリオの総価値を計算
   */
  getTotalValue(): number {
    let assetsValue = 0;
    this.holdings.forEach(({ asset, quantity }) => {
      assetsValue += asset.currentPrice * quantity;
    });
    return this.cash + assetsValue;
  }

  /**
   * 資産配分を計算（パーセンテージ）
   */
  getAssetAllocation(): Record<string, number> {
    const totalValue = this.getTotalValue();
    if (totalValue === 0) {
      return {};
    }

    const allocation: Record<string, number> = {
      CASH: (this.cash / totalValue) * 100,
    };

    this.holdings.forEach(({ asset, quantity }, symbol) => {
      const assetValue = asset.currentPrice * quantity;
      allocation[symbol] = (assetValue / totalValue) * 100;
    });

    return allocation;
  }

  /**
   * 累積リターンを計算（パーセンテージ）
   */
  getReturns(): number {
    if (this.initialCash === 0) {
      return 0;
    }

    const currentValue = this.getTotalValue();
    return ((currentValue - this.initialCash) / this.initialCash) * 100;
  }

  /**
   * ポートフォリオ全体のリスク（加重平均ボラティリティ）を計算
   */
  getPortfolioRisk(): number {
    const totalValue = this.getTotalValue();
    if (totalValue === 0) {
      return 0;
    }

    let weightedRisk = 0;
    this.holdings.forEach(({ asset, quantity }) => {
      const assetValue = asset.currentPrice * quantity;
      const weight = assetValue / totalValue;
      weightedRisk += weight * asset.calculateRisk();
    });

    return weightedRisk;
  }

  /**
   * ポートフォリオの期待リターン（加重平均）を計算
   */
  getPortfolioExpectedReturn(): number {
    const totalValue = this.getTotalValue();
    if (totalValue === 0) {
      return 0;
    }

    let weightedReturn = 0;
    this.holdings.forEach(({ asset, quantity }) => {
      const assetValue = asset.currentPrice * quantity;
      const weight = assetValue / totalValue;
      weightedReturn += weight * asset.calculateExpectedReturn();
    });

    return weightedReturn;
  }

  /**
   * シャープレシオを計算
   */
  calculateSharpeRatio(riskFreeRate: number = 0.01): number {
    const portfolioReturn = this.getPortfolioExpectedReturn();
    const portfolioRisk = this.getPortfolioRisk();

    if (portfolioRisk === 0) {
      return 0;
    }

    return (portfolioReturn - riskFreeRate) / portfolioRisk;
  }

  /**
   * ポートフォリオのサマリー情報を取得
   */
  getSummary(): PortfolioSummary {
    return {
      totalValue: this.getTotalValue(),
      cash: this.cash,
      returns: this.getReturns(),
      expectedReturn: this.getPortfolioExpectedReturn(),
      risk: this.getPortfolioRisk(),
      sharpeRatio: this.calculateSharpeRatio(),
      assetAllocation: this.getAssetAllocation(),
      numHoldings: this.holdings.size,
    };
  }

  /**
   * 取引履歴を記録
   */
  private recordTransaction(
    type: 'BUY' | 'SELL',
    symbol: string,
    quantity: number,
    price: number
  ): void {
    this.transactionHistory.push({
      timestamp: new Date(),
      type,
      symbol,
      quantity,
      price,
      total: quantity * price,
    });
  }

  /**
   * ポートフォリオ価値の履歴を記録
   */
  private recordValue(): void {
    this.valueHistory.push({
      timestamp: new Date(),
      value: this.getTotalValue(),
    });
  }

  /**
   * ポートフォリオのクローンを作成
   */
  clone(): Portfolio {
    const newPortfolio = new Portfolio(this.cash);
    newPortfolio.initialCash = this.initialCash;

    this.holdings.forEach(({ asset, quantity }, symbol) => {
      newPortfolio.holdings.set(symbol, {
        asset: asset.clone(),
        quantity,
      });
    });

    return newPortfolio;
  }
}

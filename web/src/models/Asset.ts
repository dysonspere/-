/**
 * 資産の基底クラス
 */
export interface PriceHistory {
  timestamp: Date;
  price: number;
}

export abstract class Asset {
  symbol: string;
  name: string;
  currentPrice: number;
  priceHistory: PriceHistory[];

  constructor(symbol: string, name: string, currentPrice: number) {
    this.symbol = symbol;
    this.name = name;
    this.currentPrice = currentPrice;
    this.priceHistory = [{ timestamp: new Date(), price: currentPrice }];
  }

  protected addToHistory(price: number): void {
    this.priceHistory.push({ timestamp: new Date(), price });
  }

  updatePrice(newPrice: number): void {
    this.currentPrice = newPrice;
    this.addToHistory(newPrice);
  }

  getPriceHistory(): number[] {
    return this.priceHistory.map(h => h.price);
  }

  abstract calculateExpectedReturn(): number;
  abstract calculateRisk(): number;
  abstract clone(): Asset;
}

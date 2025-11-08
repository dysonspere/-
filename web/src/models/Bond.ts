/**
 * 債券クラス
 */
import { Asset } from './Asset';

export class Bond extends Asset {
  faceValue: number;
  couponRate: number;
  yearsToMaturity: number;
  currentYield: number;

  constructor(
    symbol: string,
    name: string,
    faceValue: number,
    couponRate: number,
    yearsToMaturity: number,
    currentYield?: number
  ) {
    const initialPrice = Bond.calculateBondPrice(
      faceValue,
      couponRate,
      yearsToMaturity,
      currentYield ?? couponRate
    );

    super(symbol, name, initialPrice);

    this.faceValue = faceValue;
    this.couponRate = couponRate;
    this.yearsToMaturity = yearsToMaturity;
    this.currentYield = currentYield ?? couponRate;
  }

  /**
   * 債券の現在価格を計算（現在価値法）
   */
  private static calculateBondPrice(
    faceValue: number,
    couponRate: number,
    yearsToMaturity: number,
    currentYield: number
  ): number {
    if (yearsToMaturity === 0) {
      return faceValue;
    }

    const couponPayment = faceValue * couponRate;
    let pvCoupons = 0;

    // クーポン支払いの現在価値
    for (let t = 1; t <= yearsToMaturity; t++) {
      pvCoupons += couponPayment / Math.pow(1 + currentYield, t);
    }

    // 額面の現在価値
    const pvFace = faceValue / Math.pow(1 + currentYield, yearsToMaturity);

    return pvCoupons + pvFace;
  }

  calculateExpectedReturn(): number {
    return this.currentYield;
  }

  calculateRisk(): number {
    // マコーレー・デュレーションの簡易計算
    const duration = this.calculateDuration();
    const interestRateVolatility = 0.01; // 金利変動を仮定（標準偏差1%程度）
    return duration * interestRateVolatility;
  }

  /**
   * マコーレー・デュレーションを計算
   */
  private calculateDuration(): number {
    if (this.yearsToMaturity === 0) {
      return 0;
    }

    const couponPayment = this.faceValue * this.couponRate;
    const bondPrice = this.currentPrice;
    let weightedCashFlows = 0;

    for (let t = 1; t <= this.yearsToMaturity; t++) {
      const cashFlow = t < this.yearsToMaturity
        ? couponPayment
        : couponPayment + this.faceValue;
      const pvCashFlow = cashFlow / Math.pow(1 + this.currentYield, t);
      weightedCashFlows += t * pvCashFlow;
    }

    return weightedCashFlows / bondPrice;
  }

  /**
   * 市場利回りを更新し、債券価格を再計算
   */
  updateYield(newYield: number): void {
    this.currentYield = newYield;
    const newPrice = Bond.calculateBondPrice(
      this.faceValue,
      this.couponRate,
      this.yearsToMaturity,
      newYield
    );
    this.updatePrice(newPrice);
  }

  /**
   * クーポン支払いを計算
   */
  payCoupon(quantity: number): number {
    const annualCoupon = this.faceValue * this.couponRate;
    return (annualCoupon * quantity) / 252; // 日次支払い（簡易計算）
  }

  /**
   * 時間経過（1日）を処理
   */
  timeStep(): void {
    this.yearsToMaturity -= 1 / 252;
    if (this.yearsToMaturity <= 0) {
      this.yearsToMaturity = 0;
      this.updatePrice(this.faceValue);
    }
  }

  clone(): Bond {
    return new Bond(
      this.symbol,
      this.name,
      this.faceValue,
      this.couponRate,
      this.yearsToMaturity,
      this.currentYield
    );
  }
}

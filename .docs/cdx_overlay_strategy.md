# Pilot Systematic CDX Overlay Strategy

## 1. Objective and Role

**Investment Objective:**  
The pilot aims to generate short-term tactical alpha by exploiting temporary dislocations in liquid credit indices, while also providing a liquidity hedge and modest convexity enhancement.  

**Relationship to Core Allocation:**  
This overlay is faster-reacting, capital-efficient, and designed to be largely uncorrelated with the slower-moving core credit allocation. It serves as a tactical enhancer rather than a strategic allocation change.  

**Investment Horizon & Turnover:**  
Typical holding period is **days to a few weeks**, with moderate turnover aligned to signal persistence. The strategy emphasizes nimble positioning while maintaining disciplined exposure limits.

---

## 2. Scope of Instruments

**Primary Tradeable Instruments:**  
- **CDX Investment Grade (IG)**: 5Y and 10Y tenors  
- **CDX High Yield (HY)**: 5Y tenor  
- **CDX North America ex-IG/XO (XO)**: 5Y tenor  

**Signal Proxies:**  
- ETFs such as **HYG** and **LQD** may be used for **signal generation only**, not direct trading, to capture market flow and basis information.  

**Liquidity & Clearing Considerations:**  
- Focus exclusively on indices with tight bid/ask spreads and reliable clearing.  
- Monitor DV01 and margin usage to ensure efficient capital deployment and compliance with clearinghouse requirements.

---

## 3. Core Signals

### 3.1 ETF vs CDX Basis  
**Rationale:** Pricing gaps between ETFs and CDX indices can indicate temporary mispricing caused by fund flows or liquidity constraints.  

**Trading Logic:**  
- **Long protection** when ETF spreads tighten relative to CDX (CDX cheap).  
- **Short protection** when ETF spreads widen relative to CDX (CDX expensive).  

**Normalization:**  
- Adjust for **ETF flows and volatility**, scaling the basis signal to capture persistent dislocations rather than transient noise.

### 3.2 VIX vs CDX Gap (Cross-Asset Risk Sentiment)  
**Rationale:** Divergences between equity implied volatility (VIX) and credit spreads reflect asymmetric cross-asset stress conditions.  

**Trading Logic:**  
- **Buy protection** when VIX spikes disproportionately to CDX spreads (equity stress outpacing credit).  
- **Sell protection** when CDX spreads spike relative to VIX (credit-specific stress).  

**Considerations:**  
- Differentiate **transient spikes** from sustained regime shifts using short-term averaging and persistence filters.

### 3.3 Short-Term Spread Momentum  
**Rationale:** CDX spreads exhibit measurable short-horizon momentum or mean-reversion.  

**Trading Logic:**  
- **Follow spread moves** when volatility-adjusted momentum signals continuation.  
- **Fade spread moves** when momentum is weak or shows reversion tendencies.  

**Horizon:** Typically **3–10 days**, with signals normalized for recent volatility.

---

## 4. Signal Integration & Positioning Logic

**Signal Standardization:**  
- Convert each signal into a **z-score or percentile rank** to allow comparability.  

**Aggregation:**  
- Combine the three signals using **weighted average**, with optional decay to account for signal half-life.  
- Target a **single tactical positioning score** dictating net CDX exposure.  

**Trade Expression:**  
- **Directional exposure:** Enter long or short protection positions when composite score exceeds thresholds.  
- **Neutral/reduced exposure:** When signals are weak or contradictory.  

**Update Frequency:**  
- Signals refreshed **daily**, with expected half-life of **3–7 days** depending on market regime.

---

## 5. Risk, Sizing, and Governance

**Position Sizing:**  
- Scale positions by **DV01** or **volatility**, ensuring gross/net risk limits are respected.  
- Typical gross risk: **0.5–2% DV01 of core portfolio**, with net directional limits tighter.  

**Stop-Loss & Signal Fade:**  
- Reduce or unwind positions when signals reverse or trigger pre-defined stop-loss levels.  

**Liquidity & Slippage:**  
- Assumes **tight CDX bid/ask spreads**, allowing rapid adjustment with minimal market impact.  

**Governance:**  
- Clear documentation and approval of positions separate from core allocation team.  
- Regular review ensures overlay remains tactical and does not replace strategic allocations.

---

## 6. Evaluation Framework

**Performance Metrics:**  
- Hit rate, **information ratio**, and **turnover-adjusted return**.  

**Diversification:**  
- Assess contribution to portfolio **risk-adjusted return** and correlation to core positions.  

**Stress Testing:**  
- Evaluate performance under macro shocks, volatility spikes, and ETF outflows.  

**Scaling Considerations:**  
- Lessons from pilot inform a **multi-signal production strategy**, including potential expansion of indices, tenors, and signal types.

---

This brief frames the pilot as a **capital-efficient, tactical overlay** that exploits temporary mispricings in liquid CDX indices, complements the core portfolio, and has robust risk and governance controls.


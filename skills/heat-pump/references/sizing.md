# Sizing reference

## Contents
1. Design outdoor temperature
2. Quick method: W/m² table
3. Fabric heat loss (U·A·ΔT)
4. Ventilation heat loss
5. Sanity checks against expected W/m²
6. Oversizing, modulation and choosing capacity
7. COP and SCOP
8. DHW tank

---

## 1. Design outdoor temperature

- **Default:** the city table of minimum temperatures for Croatia, e.g. Zagreb −13.4, Osijek −14.5, Split −3.5, Rijeka −4.8. Run `heat_calc.py cities` for all 54 cities. A custom design temperature (≤ −0.1 °C) can be used instead.
- **Choosing a less extreme value:** some countries require 100% (the average minimum over a period). Others allow 99.6% or 99%. 99.6% means 0.4% of the year is colder than the chosen temperature. For Zagreb, ASHRAE gives 100% = −12.6, 99.6% = −9.3 and 99% = −6.7 °C. Recorded minimums for Zagreb were −15 (last 5 years), −17 (10), −19 (20) and −21 (50). Designing for a few hours in 50 years makes no sense. Choose between 99 and 99.6%, because 100% leaves the heat pump oversized for most of the year. Look values up from the national authority or the ASHRAE website.
- In practice the house won't simply go cold at the design temperature. New builds especially have high thermal mass (screed, walls).
- Heat loss varies every day and hour. It's highest on the coldest day.

## 2. Quick method: W/m² table

Specific heat loss (W/m²) at indoor 20 °C:

| Insulation | −15 °C | −10 °C | −5 °C | 0 °C |
|---|---|---|---|---|
| uninsulated | 120 | 102 | 84 | 66 |
| poor (old building, minimal insulation) | 95 | 81 | 67 | 53 |
| average (basic insulation) | 55 | 47 | 39 | 31 |
| good (modern insulation) | 40 | 34 | 28 | 22 |
| passive (high-performance) | 22 | 19 | 16 | 13 |

- The table is interpolated linearly between columns, extrapolated linearly below −15 °C, and clamped to the 0 °C column at or above 0 °C.
- If indoor ≠ 20 °C, scale by (T_in − T_out) / (20 − T_out).
- Heat load [kW] = W/m² × area / 1000.
- **Required power = heat load × 1.15 for radiators, × 1.0 for underfloor.** Radiators run at higher temperatures, so +15% power is needed.
- Supported input ranges: area 20-500 m², occupants 1-10.
- Disclaimer: these are estimates for an average house. They may vary significantly with house shape, construction quality, intended purpose and other factors. For the final installation, consult certified HVAC professionals.

`heat_calc.py size` implements this method.

## 3. Fabric heat loss

`Q [W] = U × A × ΔT`

- ΔT = desired indoor − design outdoor temperature. A temperature difference is the same in K and °C.
- U-value: rate of heat transfer through a structure, in W/m²K. Lower U means less heat flow.
- Example U-values given:

  | Element | U (W/m²K) |
  |---|---|
  | Single-glazed window | 5.2 |
  | Double-glazed window | 2.2 |
  | Poorly insulated roof | 1.0 |
  | Well-insulated roof | 0.25 |
  | Insulated roof | 0.5 |
  | Cavity brick external wall | 1.0 |
  | Well-insulated floor | 0.4 |

- Typical distribution of building heat loss shown: roof 35%, walls 25%, ground 15%, door 15%, windows 10%.
- Worked numbers: 2 m² single glazing at ΔT 20 → 5.2 × 20 × 2 = 208 W. U 5 at ΔT 30 → 150 W/m². Halve U (2.5) → 75 W/m². U 2.5 at ΔT 15 (5 °C outside, 20 °C inside) → 37.5 W/m².
- You can't change ΔT (it depends on climate), but you can change U by insulating.
- **Room by room:** list each surface's dimensions and U-value. **Subtract window areas from the wall they sit in.** Walls to rooms at the same temperature have ΔT = 0, so no heat loss. Divide the room total by floor area to get W/m².

`heat_calc.py fabric` implements this, plus ventilation (§4).

## 4. Ventilation heat loss

`Q_vent [W] = 0.33 × V [m³] × n [1/h] × ΔT`

- Two categories of heat loss: fabric (through surfaces) and ventilation (warm air replaced by cold air through chimneys, doors, windows, ducts).
- Typical air changes from norms: bathroom 1.5, other rooms 0.5. Follow national legislation.
- Ventilation is a bigger share in well-insulated houses. Example: a 4 kW house has 3 kW fabric + 1 kW ventilation (~25%). A 10 kW house has 1-1.5 kW ventilation (~10%).
- **Likely overestimated:** nobody keeps 1.5 / 0.5 air changes (windows open) when it's −10 °C outside. A blower-door test measures the real value.
- **MVHR** (mechanical ventilation with heat recovery) cuts ventilation loss by its recovery efficiency. With 80% efficiency, 1,000 W becomes 200 W. Recommended for new builds with good insulation and new windows.

## 5. Sanity checks against expected W/m²

- A new 200 m² well-insulated house at −10/20 °C needs 9 kW (45 W/m²). At +7 °C it needs only 3.9 kW (~20 W/m²).
- Croatian new builds must meet NZEB (nearly zero energy building) maximum U-values. Such houses hardly exceed ~60 W/m² at −6/−7/−10 °C. More than 100 W/m² isn't legal for a new build, and even reconstructions rarely reach it, because almost every house has new windows or some insulation.
- Few houses exceed 16 kW heat loss, which is about the maximum residential heat pump capacity.
- Systems on Heat Pump Monitor range from 19 to 76 W/m², old and new.
- **Software check:** if software gives 30 kW for a 250 m² new build (>100 W/m²), suspect wrong input, such as missing or wrong window values. Know what result to expect before trusting software or Excel. Real case: designed at 30 kW, but the energy certificate said ~9.5 kW (even 15 kW would be half).
- Once you know the load at one temperature: `W/K = load / (T_in − T_design)`. Example: 9.78 kW at −12.6/20 → 300 W/K, so 8.79 kW at −9.3 and 8.0 kW at −6.7. Choosing −6.7 instead of −12.6 removes ~1.8 kW.

`heat_calc.py modulation --load … --at …` does this.

## 6. Oversizing, modulation and choosing capacity

- **Oversizing is the usual problem**, not undersizing. Installers bring gas/pellet habits, where oversizing did no harm.
- The compressor has a limited modulation range. Example: Panasonic 9 kW T-CAP (9 kW down to −15 °C) modulates 3-9 kW at −7 °C but only 4.5-9 kW at +7 °C. A house needing ~4 kW at +7 °C is at the edge. A 12 kW unit there might only go down to 5-6 kW, so it cycles on and off and the system is inefficient.
- **Better to be on the edge with capacity and let heating elements cover the lowest temperatures.**
- Insufficient flow rate effectively needs a bigger unit and causes on/off running (see hydraulics.md).
- **Minimum output** is usually 25-35% of nominal (30-40% as a working figure), depending on outdoor temperature, manufacturer and algorithm. Above the outdoor temperature where the load falls below the minimum output, the unit cycles on and off. Example: 6.8 kW at 21/−3 → 0.283 kW/K. With a 3.14 kW minimum, the load matches at ΔT ≈ 11 K, so outdoor ≈ 10 °C. Use `heat_calc.py modulation --min-output`.
- **Acceptable vs harmful oversizing:** 10-30% is fine when equipment steps force it. 50, 60, 100 or 300% means a bad system and high consumption. A 30 kW unit has a minimum of ~7-9 kW, above the whole house's design load, so it always cycles. It also costs more, needs more space, is noisier and needs bigger pipes.
- **Overpowered thresholds:** reject units ≥ 2× the required power. Warn for units ≥ 1.5×: significantly overpowered and may introduce short cycling.
- **Defrost exception:** many manufacturers don't include defrost in capacity. A 10 kW unit may deliver 9 kW, losing 1 kW to defrost. In defrost-heavy climates (design temperature near 0 °C, e.g. UK), slightly oversize by 10-20%.

## 7. COP and SCOP

- COP = useful heat delivered ÷ electricity used (mainly the compressor; pumps, fans and sensors are minor).
- COP depends on two temperatures, the heating system (flow) and the source. It doesn't depend on insulation. Insulation changes running cost, not efficiency. Poorly designed new houses can have low COP, and well-designed uninsulated houses can have good COP.
- Panasonic 9 kW 3-phase table: A7/W35 9 kW / 1.86 kW → COP 4.8. A7/W55 9 / 3.06 → 2.94 (64% difference). A−7/W35 9 / 3.16 → 2.85.
- **Each +1 °C of flow temperature costs ~2-3% more electricity.** At ~2%/K, lowering flow by 7.5 K gains ~15%.
- Use **SCOP** (seasonal) for calculations, not single-point COP. The average heating-season temperature is around 0 °C, which is why norms quote COP at W35/A7.
- Compare **SCOP low** (lower-temperature system) for underfloor and **SCOP high** (higher-temperature system) for radiators.
- Heat Pump Monitor top 20 by SCOP: every system with SCOP > 4 is single-zone with flow ≤ 45 °C. Design matters more than manufacturer, and refrigerant (R290 vs R32) makes little difference. Top performers often have no DHW, because DHW runs at higher flow.

## 8. DHW tank

- Volume: 40-50 L per person. Use **45 L/person**. Example: 4 people → 200 L.
- Coil: a heat pump needs a large coil surface, 0.2 m² per kW, minimum 1.5 m² for small models. A gas boiler coil can be ~1 m², which isn't enough.
- Heat-up energy `E = m × 4186 J/kgK × ΔT`. 200 L from 10 to 50 °C ≈ 33 MJ. Time = E / P: 7 kW → ~80 min, 12 kW → ~46.5 min. This only matters for the first fill.
- Reheat: with a −8 K reheat setting and a 50 °C setpoint, the heat pump reheats when the tank drops below 42 °C.

`heat_calc.py dhw` implements the energy and time calculation.

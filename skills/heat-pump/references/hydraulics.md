# Hydraulics reference: flow, ΔT, pipes, volume, buffers, balancing

## Contents
1. Flow rate and ΔT
2. Pipe sizing
3. Underfloor circuits without buffer
4. Buffer or not
5. System volume
6. Cooling and fan coils
7. Radiator balancing

---

## 1. Flow rate and ΔT

- `P [kW] = ṁ [kg/s] × c [kJ/kgK] × ΔT [K]`. For water, c ≈ 4.2 kJ/kgK.
- 9 kW at ΔT 5 K → 0.42-0.43 kg/s ≈ **25.8 L/min**. At ΔT 20 (condensing boiler) → ~0.1 kg/s ≈ 6 L/min, four times less.
- **Quick rule:** flow [L/min] ≈ 3 × capacity [kW] at ΔT 5.
- **Why ΔT 5 for heat pumps:** the compressor is most efficient at ΔT 5. It measures the return and tries to hold 5 K rather than rushing to the setpoint. Condensing boilers run ΔT ~20 by design (older boilers and pellets 15-20).
- For the same mean radiator temperature of 42.5 °C: boiler 52.5/32.5, heat pump 45/40. That's 7.5 K lower flow, ≈ 15% gain at ~2%/K.
- **Half the flow** (12.9 L/min for 9 kW) needs ΔT 10 for the same capacity. That means lower comfort and the compressor working harder. The pump must reach the rated flow at the system's pressure drop.
- The whole system (UFH or radiators) must run at the heat pump's ΔT. You can't design one room at ΔT 5, another at 7 and a floor at 10-11, because all pipes return to the same generator.

`heat_calc.py flow <kW…> --dt 5` gives the flow per load and the total.

## 2. Pipe sizing

- Ideal velocity is **~1 m/s**.
- Pipe too small → high velocity, noise, high pressure drop/friction and more pump energy. Pipe too big → too slow, dirt settles and air gets trapped. Too small is the bigger problem.
- Copper-table results quoted, at ~1 m/s:

  | Load | ΔT | Flow | Copper pipe |
  |---|---|---|---|
  | 9 kW | 5 | 0.42 kg/s | 28 mm |
  | 7 kW | 5 | — | 22 mm |
  | 3 kW (3 × 1 kW radiators) | 5 | 0.14 kg/s | 15 mm |
  | 1 kW (last radiator) | 5 | 0.047 kg/s | 10 mm |
  | 9 kW | 20 (boiler) | 0.1 kg/s | 15 mm |

- **Plastic pipe: go one size bigger** than copper (e.g. 35 instead of 28).
- The primary pipe carries the whole load. Each branch is sized for the load it serves.
- Smaller pipes still work, but with more noise, more pressure drop and more pump energy.

## 3. Underfloor circuits without buffer

- If the heat pump's circulator delivers the rated flow at the system pressure drop, no buffer is needed.
- With direct connection, avoid room thermostats/motor valves, except maybe one or two in bedrooms. Closing circuits drops the flow, and the compressor can't modulate low enough, especially around 0 °C and up. Most efficient: an open-loop system, no buffer, no thermostats.
- Get different room temperatures (bedroom 20, living room 24, bathroom 25) by **balancing circuit flows**, not with motor valves.
- Method: calculate each room's heat loss, then flow per circuit at ΔT 5 with c = 4.2. Example: 9 kW, 13 circuits, total 25.8 L/min. A 1 kW circuit → 2.9 L/min. A 400 W circuit → 1.1 L/min. Give a room more flow to make it warmer.
- Check the pump curve: the Panasonic 9 kW circulator at 25.8 L/min gives 31 kPa at nominal speed, up to 100 kPa at maximum. The highest UFH circuit pressure drop is around 15 kPa.

## 4. Buffer or not

- Probably not needed for ~90% of installations. Exceptions include big cascade systems and some cooling systems with big pressure drops.
- The common belief that the internal pump is too weak is not true. Panasonic pump curve: ~140 kPa available at zero flow (maximum curve) and ~100 kPa at 10-20 L/min. The 16 kW model at its nominal ~45 L/min still has ~60 kPa available. A well-designed UFH primary needs ≤ 30 kPa (40 at most). Radiators are similar, except very old microbore (8/10 mm) systems.
- The same pump serves the 9 and 12 kW models (nominal 20-25 L/min), so it can run on a lower curve.
- The maximum speed is only the design point (< 1% of the year). The pump and compressor modulate, so pump consumption is low most of the year. Old boiler-system pumps typically had ~60 kPa nominal.
- A buffer makes it hard to maintain flow on both the primary and secondary sides. With a single zone (only UFH or only radiators), modulate with the pump instead.
- Buffers and microbore can still perform well if the system is designed and balanced.
- If you have one, a buffer is better in cooling and a volumiser better in heating.

## 5. System volume

- Rule of thumb: **15-20 L per kW** of heat pump (5 kW → 75-100 L).
- 75% of installers on Heat Pump Monitor don't calculate system volume.
- Mandatory individual room regulation reduces volume and causes cycling (lower COP, more consumption). A volumiser or bypass valves can help.
- **Volume for a given number of compressor starts per hour:** `V [L] = minimum flow [L/h] / starts per hour`. Example: 7 kW unit, minimum 9 L/min = 540 L/h. 5 starts/h → 108 L, so an existing open 100 L system is fine. 2 starts/h → 270 L, so add 170 L. This is a basic formula. Real behaviour depends on the unit's algorithm and on pump and compressor modulation.
- Volume only counts if it's open. Closed zones reduce effective volume.
- **When cycling comes from closing valves:** keep valves open, turn the heat pump down rather than closing valves, and balance the radiators (§7).
- Volume supplies the energy for **defrost**. With low volume, defrost takes longer, with no heating or DHW meanwhile and unstable operation. Some new Panasonic models defrost from the DHW side. "Volume is like fuel for a car."
- One single zone outperforms multi-zone. TRVs or regulation are fine in bedrooms or small zones. Keep the other zones open.

`heat_calc.py volume` implements the starts-per-hour formula.

## 6. Cooling and fan coils

Real case: a 15-16 kW unit, 200 L heating buffer, 100 L cooling volumiser on the return, fan coils. Heating consumption was high, and in cooling the unit never worked (constant errors).

- Refrigerant pipes were 22 mm instead of 16/10 mm over ~25 m. The oversized gas line needs additional refrigerant charge.
- In cooling there were repeated "flow rate too low" errors, and the indoor **plate heat exchanger froze and broke** (around 0 °C or lower).
- Test: valves closed to the fan coils, cooling only the 200 L buffer (from ~20 °C, setpoint 10). It reached 8 °C in ~20 min, return ~13 °C, ΔT 5, with the compressor modulating. The unit was fine.
- The fan coils' secondary pump only reached ~10 L/min with all three fan coils on (enough for one 3.5 kW fan coil). They needed **38 L/min for 13.5 kW**. The fan coils had internal motor valves nobody accounted for, and the installer had changed the pipes.
- **Fix: a bypass (differential) valve** that opens when flow is too low. For a 16 kW unit, 10 L/min is well below minimum, so set it to around 13 L/min.
- The internal pump follows the unit's algorithm and needs a minimum flow. The secondary pump can run lower, so "the internal pump is too weak" was the wrong conclusion.
- In heating, low volume or flow mainly causes cycling. In cooling, low flow can destroy the unit. The basics for every system: **ensure flow rate and system volume**.

## 7. Radiator balancing

- Definitions, weakest to best:
  1. Same flow to every radiator. Disliked.
  2. Same ΔT across every radiator (5, 5, 5). Better.
  3. **Each room at the right temperature relative to the others.** Radiators may need different ΔTs (e.g. one at 7, another at 3). The balance point shifts with solar gains.
- TRV problem: the TRV senses heat near the radiator and shuts off. Better to sense room temperature where people sit.
- **If the house is too hot, turn the heat pump down rather than closing valves.** Never shut all radiators. Keep volume in the system.
- A radiator that's always wide open while the others throttle back is the limiting one. Upgrading it allows a lower flow temperature. Rank radiators worst to best and weigh the upgrade cost against the saving.
- Controls mentioned: weather compensation curve, load compensation, tariff compensation. Modbus connection to the heat pump is becoming the standard.

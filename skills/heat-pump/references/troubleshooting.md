# Troubleshooting reference

Only the symptoms and causes below are covered. If a problem isn't listed, say this skill doesn't cover it.

## Data to collect

Values needed to diagnose:
- Heat load (and W/m²), design outdoor temperature, unit nominal capacity and minimum output at the relevant outdoor temperature
- Flow rate (L/min), flow/return temperatures (ΔT), flow temperature setpoint
- Open system volume (L), number of zones, which valves/thermostats/TRVs can close
- Buffer/volumiser/bypass layout, pump curve and system pressure drop
- Pipe sizes (primary and branches, copper or plastic)

## Symptoms

### Compressor cycles on and off / high consumption
1. **Unit oversized.** Its minimum output is above the load in mild weather. Compare minimum output with the load at the current outdoor temperature (`heat_calc.py modulation`). For example, 12 kW at +7 °C may only go down to 5-6 kW against a 4 kW load.
2. **Heat load overestimated.** Check the result against expected W/m² (sizing.md §5). A 100%-percentile design temperature or an inflated ventilation allowance both push it up.
3. **Too little open system volume.** Zones closed by thermostats or motor valves, or individual room regulation. Calculate the volume needed for the allowed starts/h, or use 15-20 L/kW. Fix with open zones, a volumiser or a bypass.
4. **Flow rate too low.** Same capacity forced to a larger ΔT, so it runs on/off.

### Low efficiency (low COP/SCOP)
1. Flow temperature too high: each +1 °C costs ~2-3%. Aim for ≤ 45 °C.
2. Running at a large ΔT instead of 5 K, which needs a higher flow temperature for the same mean radiator temperature.
3. Multi-zone with zones closing instead of a single open zone.
4. Poor design generally. Design matters more than manufacturer or refrigerant.

### Rooms not reaching temperature / uneven rooms
1. Flow rate below rated: the unit doesn't deliver capacity at ΔT 5. Check the pump reaches rated flow at the system pressure drop.
2. Circuits/radiators not balanced. Balance flows per room heat loss (UFH) or to room temperatures (radiators).
3. Limiting radiator: always wide open while the others throttle. Upgrade it.
4. TRV sensing radiator heat and shutting off early.

### "Flow too low" errors, frozen/broken plate heat exchanger (especially cooling)
1. Motor valves (also those hidden inside fan coils) or closed zones cutting flow below the unit's minimum.
2. No bypass valve. Fit a differential bypass set above the minimum flow (≈13 L/min for a 16 kW unit).
3. Secondary pipework/pump unable to give the required flow (e.g. 10 L/min delivered vs 38 L/min needed for 13.5 kW).
4. Low refrigerant charge, e.g. oversized refrigerant pipes (22 mm instead of 16/10 mm over ~25 m) without extra charge.
5. Isolate the fault: run the unit against the buffer/volume alone. If it modulates and holds ΔT 5, the unit is fine and the problem is in the hydraulics.

### Long defrosts / no heat or DHW during defrost
- Low system volume, so not enough energy to melt the ice quickly.
- In defrost-heavy climates (design temperature near 0 °C), capacity is lost to defrost. Allow 10-20% oversize.

### Noise or high pump energy in pipework
- Pipes too small, so velocity is well above ~1 m/s.

### Dirt or trapped air in pipework
- Pipes too big, so velocity is too low.

### "The internal pump is too weak, we need a buffer"
- Usually false. Check the pump curve against the actual system pressure drop (hydraulics.md §4).

---
name: heat-pump
description: Size and troubleshoot residential air-to-water heat pump systems (metric, Croatian design temperatures) - heat loss from a W/m² insulation table or U·A·ΔT plus ventilation, required power for underfloor vs radiators, oversizing and compressor modulation checks, COP/SCOP and flow temperature, ΔT 5 flow rates, pipe sizing, system volume, buffer vs no buffer, underfloor circuit and radiator balancing, DHW tank volume and heat-up time, and diagnosing short cycling, low COP, cold or uneven rooms, low-flow errors, frozen plate heat exchangers in cooling, and long defrosts. Use this skill whenever the user asks how big a heat pump they need, whether a unit is oversized, what flow rate, pipe size, tank or system volume to use, whether they need a buffer, how to balance radiators or underfloor circuits, or describes a heat pump that cycles, errors or performs badly - even if they only mention kW, W/m², a Croatian city, a heating curve, fan coils, or a brand like Panasonic.
---

# Heat pump sizing and troubleshooting

Help homeowners and installers size heat pump systems and fix badly performing ones. Use metric units (kW, W/m², °C, K, L/min, L, kPa).

**Use only the information in `references/` and `scripts/heat_calc.py`.** If a question goes beyond them (e.g. running-cost comparisons, specific error codes, refrigerant regulations), say this skill doesn't cover it rather than filling the gap.

The recurring lesson is that **design beats hardware**. Oversized units, inflated heat-loss figures, too little flow or volume, and high flow temperatures cause most problems, regardless of manufacturer.

## Pick the reference

| Question is about | Read |
|---|---|
| Heat load, design temperature, required power, oversizing/modulation, COP/SCOP, DHW tank | `references/sizing.md` |
| Flow rate, ΔT, pipe sizes, UFH circuits, buffer, system volume, cooling/fan coils, radiator balancing | `references/hydraulics.md` |
| Something wrong with an installed system | `references/troubleshooting.md` (points into the other two) |

## Calculations

Run `scripts/heat_calc.py` for all arithmetic. `selftest` re-runs the worked examples.

Run each calculation as its own command, with the absolute path from this skill's base directory: `python3 <base dir>/scripts/heat_calc.py <subcommand> …`. Don't chain it with `cd`, `cat`, `;` or `&&`. Read reference files with the Read tool. Permission rules such as `Bash(python3:*)` only match commands that start with `python3`, so a chained command gets denied. If the script is still denied, do the same formulas by hand from `references/` and say so.

| Subcommand | Use for |
|---|---|
| `size --area --insulation --city/--t-design --emitter [--occupants]` | Quick load from the W/m² table, +15% for radiators, 45 L/person tank |
| `fabric file.json` | Room/building U·A·ΔT plus 0.33·V·n·ΔT ventilation, optional MVHR |
| `flow <kW…> [--dt 5]` | Flow rate for the unit, or per UFH circuit/radiator plus the total |
| `modulation --load --t-in --t-design [--min-output] [--at …]` | W/K, load at other outdoor temps, outdoor temp above which the unit cycles |
| `volume --min-flow --starts [--system-volume]` | Volume needed for N compressor starts per hour. `--min-flow` is the unit's minimum water flow in L/min, not its minimum output in kW. If it's unknown, ask for it or use the 15-20 L/kW rule |
| `dhw --volume --power [--t-target --t-cold]` | Tank heat-up energy and time |
| `cities` | Croatian city design temperatures |

## Sizing workflow

1. **Inputs:** heated area, insulation level (uninsulated / poor / average / good / passive), location or design temperature, emitter (underfloor or radiators), occupants if DHW is wanted. If the user has room dimensions and U-values, use the fabric method instead.
2. **Design temperature:** use the city table by default. Note that using the 99-99.6% ASHRAE value instead (e.g. Zagreb −9.3 to −6.7 instead of −13.4) lowers the load and reduces oversizing. Show the load at that temperature too if the user can provide it.
3. **Heat load and required power:** run `size` (or `fabric`). Required power = load × 1.15 for radiators, × 1.0 for underfloor.
4. **Sanity check** against expected W/m² (sizing.md §5). New Croatian builds hardly exceed ~60 W/m². More than 100 W/m² for a new build points to an input error.
5. **Oversizing check:** run `modulation` with the candidate unit's minimum output. State the outdoor temperature above which it will cycle. Flag units ≥ 1.5× required power (warning threshold) and reject ≥ 2×. Prefer being on the edge with backup heating elements over oversizing. Exception: allow +10-20% in defrost-heavy climates near 0 °C.
6. **Hydraulics:** flow at ΔT 5 (`flow`), primary pipe size at ~1 m/s, system volume 15-20 L/kW or by starts/h (`volume`), buffer usually not needed.
7. **DHW:** tank 45 L/person, coil ≥ 0.2 m²/kW (min 1.5 m²), heat-up time with `dhw`.

### Sizing output format

```
## Summary
<recommended capacity range, emitter note, flow rate, tank>

## Heat load
<method, design temp used (and 99-99.6% alternative), W/m², kW, sanity check>

## Unit selection
<required power, oversizing/modulation check, cycling temperature>

## Hydraulics
<flow L/min at ΔT 5, primary pipe, system volume, buffer yes/no>

## DHW
<tank volume, coil, heat-up time>

## Assumptions
<each assumed input with its value; disclaimer: estimate for an average house, confirm with a certified HVAC professional>
```

## Troubleshooting workflow

1. Collect the values listed at the top of `references/troubleshooting.md`: load, unit minimum output, flow rate, ΔT, flow temperature, open volume, zones/valves, buffer/bypass layout and pipe sizes.
2. Match the symptom to a section there and work through the causes in order. Use `heat_calc.py` to confirm with numbers, e.g. load vs minimum output, required vs actual flow, required vs actual volume.
3. Present the results like this:

```
## Most likely cause
## Checks (numbered, what each result means)
## Fix
```

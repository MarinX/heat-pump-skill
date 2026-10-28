#!/usr/bin/env python3
"""Heat pump sizing arithmetic (metric). Prints JSON.

  size        quick load from W/m² table + DHW tank volume
  fabric      U·A·ΔT + ventilation 0.33·V·n·ΔT from a JSON file
  flow        flow rate per load at a given ΔT (whole unit or per circuit/radiator)
  modulation  W/K, load at other outdoor temps, temp above which unit cycles on/off
  volume      system volume needed for N compressor starts per hour
  dhw         energy and heat-up time of a DHW tank
  cities      list Croatian city design temperatures
  selftest    re-run the worked examples

Examples:
  heat_calc.py size --area 150 --insulation average --city Zagreb --emitter radiators --occupants 4
  heat_calc.py fabric room.json
  heat_calc.py flow 9 --dt 5
  heat_calc.py flow 1.0 0.4 0.8 --dt 5
  heat_calc.py modulation --load 6.8 --t-in 21 --t-design -3 --min-output 3.14
  heat_calc.py volume --min-flow 9 --starts 2 --system-volume 100
  heat_calc.py dhw --volume 200 --t-target 50 --t-cold 10 --power 7

fabric JSON: {"t_in": 20, "t_design": -10, "floor_area": 20,
              "elements": [{"name": "window", "u": 2.2, "area": 4}, ...],
              "volume": 60, "ach": 0.5, "mvhr_efficiency": 0.8}
  Wall areas must be net of windows/doors. Omit "volume" to skip ventilation.
"""
import argparse
import json
import sys

DESIGN_TEMPS = (-15, -10, -5, 0)
HEAT_LOSS_WM2 = {  # W/m² at indoor 20 °C, keyed by outdoor design temp
    "uninsulated": (120, 102, 84, 66),
    "poor": (95, 81, 67, 53),
    "average": (55, 47, 39, 31),
    "good": (40, 34, 28, 22),
    "passive": (22, 19, 16, 13),
}
RADIATOR_FACTOR = 1.15
TANK_L_PER_PERSON = 45

CITY_MIN_TEMP = {
    "Belje": -14.8, "Benkovac": -8.9, "Bjelovar": -12.5, "Čakovec": -13.2, "Čazma": -12.0,
    "Cres": -5.1, "Crikvenica": -5.4, "Đakovo": -14.0, "Daruvar": -13.5, "Delnice": -11.5,
    "Donja Stubica": -14.2, "Dubrovnik": -4.5, "Garešnica": -13.8, "Gospić": -10.2, "Hvar": -3.5,
    "Imotski": -7.1, "Jastrebarsko": -12.9, "Karlovac": -12.2, "Knin": -8.2, "Koprivnica": -13.0,
    "Križevci": -13.1, "Krk": -4.6, "Kutina": -13.4, "Lepoglava": -12.8, "Lipik": -13.6,
    "Makarska": -4.2, "Našice": -14.1, "Nova Gradiška": -13.5, "Ogulin": -11.8, "Opatija": -4.8,
    "Osijek": -14.5, "Pazin": -9.2, "Petrinja": -12.7, "Poreč": -5.0, "Požega": -13.8,
    "Pula": -5.2, "Rab": -4.4, "Rijeka": -4.8, "Rovinj": -4.9, "Senj": -6.0,
    "Šibenik": -4.5, "Sisak": -12.8, "Slavonski Brod": -14.0, "Slunj": -11.0, "Split": -3.5,
    "Topusko": -11.7, "Trogir": -3.6, "Varaždin": -14.2, "Veli Lošinj": -3.7, "Vinkovci": -14.8,
    "Virovitica": -14.0, "Vukovar": -14.6, "Zadar": -3.7, "Zagreb": -13.4,
}

WATER_CP = 4.186  # kJ/(kg·K)
AIR_FACTOR = 0.33  # W/(m³·K)


def wm2(level, t_out, t_in=20.0):
    """Interpolate the W/m² table: extrapolate below -15, clamp at/above 0."""
    q = HEAT_LOSS_WM2[level]
    t = DESIGN_TEMPS
    if t_out < t[0]:
        base = q[0] + (q[1] - q[0]) / (t[1] - t[0]) * (t_out - t[0])
    elif t_out >= t[-1]:
        base = q[-1]
    else:
        i = next(i for i in range(len(t) - 1) if t[i] <= t_out <= t[i + 1])
        base = q[i] + (t_out - t[i]) / (t[i + 1] - t[i]) * (q[i + 1] - q[i])
    if t_in == 20:
        return base
    d_base = 20 - t_out
    return base * max(0.0, (t_in - t_out) / d_base if d_base > 0 else 1)


def size(area, insulation, t_design, emitter, occupants=None, t_in=20.0):
    q = wm2(insulation, t_design, t_in)
    load = q * area / 1000
    out = {
        "t_design_C": t_design,
        "heat_loss_W_per_m2": round(q, 1),
        "heat_load_kW": round(load, 2),
        "required_power_kW": round(load * (RADIATOR_FACTOR if emitter == "radiators" else 1.0), 2),
        "scop_to_compare": "SCOPHigh" if emitter == "radiators" else "SCOPlow",
    }
    if occupants:
        out["tank_volume_L"] = occupants * TANK_L_PER_PERSON
    return out


def fabric(spec):
    dt = spec["t_in"] - spec["t_design"]
    per = {e["name"]: e["u"] * e["area"] * dt for e in spec["elements"]}
    total = sum(per.values())
    out = {"delta_T_K": dt, "per_element_W": {k: round(v, 1) for k, v in per.items()}, "fabric_W": round(total, 1)}
    if "volume" in spec:
        vent = AIR_FACTOR * spec["volume"] * spec.get("ach", 0.5) * dt
        vent *= 1 - spec.get("mvhr_efficiency", 0.0)
        out["ventilation_W"] = round(vent, 1)
        total += vent
    out["total_W"] = round(total, 1)
    if spec.get("floor_area"):
        out["W_per_m2"] = round(total / spec["floor_area"], 1)
    return out


def flow(kw, dt=5.0):
    kg_s = kw / (WATER_CP * dt)
    return {"kW": kw, "kg_per_s": round(kg_s, 3), "L_per_min": round(kg_s * 60, 1)}


def modulation(load_kw, t_in, t_design, min_output_kw=None, at=()):
    h = load_kw / (t_in - t_design)  # kW per K
    out = {"kW_per_K": round(h, 3), "load_at_kW": {str(t): round(h * (t_in - t), 2) for t in at}}
    if min_output_kw is not None:
        # above this outdoor temp the load is below the unit's minimum output -> on/off cycling
        out["cycles_above_outdoor_C"] = round(t_in - min_output_kw / h, 1)
    return out


def volume(min_flow_l_min, starts_per_hour, system_volume_l=None):
    need = min_flow_l_min * 60 / starts_per_hour
    out = {"required_volume_L": round(need)}
    if system_volume_l is not None:
        out["additional_volume_L"] = round(max(0.0, need - system_volume_l))
    return out


def dhw(volume_l, t_target, t_cold, power_kw):
    energy_j = volume_l * WATER_CP * 1000 * (t_target - t_cold)
    s = energy_j / (power_kw * 1000)
    return {"energy_MJ": round(energy_j / 1e6, 2), "energy_kWh": round(energy_j / 3.6e6, 2),
            "heat_up_s": round(s), "heat_up_min": round(s / 60, 1)}


def selftest():
    # interpolation, extrapolation, clamp, radiators +15 %, 45 L/person
    assert wm2("average", -10) == 47 and wm2("average", -12.5) == 51 and wm2("average", 5) == 31
    assert abs(wm2("average", -20) - 63) < 1e-9
    r = size(100, "average", -10, "radiators", 4)
    assert r["heat_load_kW"] == 4.7 and r["required_power_kW"] == 5.4 and r["tank_volume_L"] == 180, r
    # 2 m² single glazing, U 5.2, ΔT 20 -> 208 W
    assert fabric({"t_in": 20, "t_design": 0, "elements": [{"name": "w", "u": 5.2, "area": 2}]})["total_W"] == 208
    # 1000 W without MVHR -> 200 W with 80 % MVHR
    v = fabric({"t_in": 20, "t_design": -10, "elements": [], "volume": 1000 / (0.33 * 0.5 * 30), "ach": 0.5,
                "mvhr_efficiency": 0.8})
    assert abs(v["ventilation_W"] - 200) < 0.1, v
    # 9 kW at ΔT5 -> 25.8 L/min; ΔT10 halves it; ΔT20 -> ~0.1 kg/s
    assert flow(9)["L_per_min"] == 25.8 and flow(9, 10)["L_per_min"] == 12.9 and flow(9, 20)["kg_per_s"] == 0.108
    # 6.8 kW, 21/-3, min 3.14 kW -> 11 K difference -> cycles above ~10 °C
    m = modulation(6.8, 21, -3, 3.14)
    assert m["kW_per_K"] == 0.283 and m["cycles_above_outdoor_C"] == 9.9, m
    # 9.78 kW at -12.6 -> 300 W/K, 8.79 kW at -9.3, 8.0 kW at -6.7
    m = modulation(9.78, 20, -12.6, at=(-9.3, -6.7))
    assert m["kW_per_K"] == 0.3 and m["load_at_kW"] == {"-9.3": 8.79, "-6.7": 8.01}, m
    # 9 L/min, 5 starts -> 108 L; 2 starts -> 270 L, +170 L on a 100 L system
    assert volume(9, 5)["required_volume_L"] == 108 and volume(9, 2, 100)["additional_volume_L"] == 170
    # 200 L 10->50 °C ≈ 33 MJ; 7 kW ≈ 79.7 min; 12 kW ≈ 46.5 min
    d7, d12 = dhw(200, 50, 10, 7), dhw(200, 50, 10, 12)
    assert d7["energy_MJ"] == 33.49 and d7["heat_up_min"] == 79.7 and d12["heat_up_min"] == 46.5, (d7, d12)
    return {"selftest": "ok"}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("size")
    s.add_argument("--area", type=float, required=True, help="heated floor area m² (20-500)")
    s.add_argument("--insulation", choices=HEAT_LOSS_WM2, required=True)
    g = s.add_mutually_exclusive_group(required=True)
    g.add_argument("--city", help="Croatian city (see `cities`)")
    g.add_argument("--t-design", type=float, help="custom outdoor design temp °C")
    s.add_argument("--emitter", choices=("underfloor", "radiators"), required=True)
    s.add_argument("--occupants", type=int, help="1-10, for DHW tank volume")
    s.add_argument("--t-in", type=float, default=20.0)

    f = sub.add_parser("fabric")
    f.add_argument("spec", help="JSON file, see module docstring")

    fl = sub.add_parser("flow")
    fl.add_argument("kw", type=float, nargs="+", help="one or more loads in kW")
    fl.add_argument("--dt", type=float, default=5.0)

    m = sub.add_parser("modulation")
    m.add_argument("--load", type=float, required=True, help="heat load kW at design temp")
    m.add_argument("--t-in", type=float, required=True)
    m.add_argument("--t-design", type=float, required=True)
    m.add_argument("--min-output", type=float, help="unit minimum output kW")
    m.add_argument("--at", type=float, nargs="*", default=[7.0], help="outdoor temps to evaluate load at")

    v = sub.add_parser("volume")
    v.add_argument("--min-flow", type=float, required=True, help="unit minimum flow L/min")
    v.add_argument("--starts", type=float, required=True, help="allowed compressor starts per hour")
    v.add_argument("--system-volume", type=float, help="existing open system volume L")

    d = sub.add_parser("dhw")
    d.add_argument("--volume", type=float, required=True, help="tank L")
    d.add_argument("--t-target", type=float, default=50.0)
    d.add_argument("--t-cold", type=float, default=10.0)
    d.add_argument("--power", type=float, required=True, help="heat pump kW")

    sub.add_parser("cities")
    sub.add_parser("selftest")
    a = p.parse_args(argv)

    if a.cmd == "size":
        if not 20 <= a.area <= 500:
            p.error("--area must be 20-500 m²")
        if a.occupants is not None and not 1 <= a.occupants <= 10:
            p.error("--occupants must be 1-10")
        if a.city is not None and a.city not in CITY_MIN_TEMP:
            p.error(f"city {a.city!r} not in city table; pass --t-design instead")
        t = CITY_MIN_TEMP[a.city] if a.city else a.t_design
        out = size(a.area, a.insulation, t, a.emitter, a.occupants, a.t_in)
    elif a.cmd == "fabric":
        with open(a.spec) as fh:
            out = fabric(json.load(fh))
    elif a.cmd == "flow":
        rows = [flow(k, a.dt) for k in a.kw]
        out = rows[0] if len(rows) == 1 else {"circuits": rows, "total": flow(sum(a.kw), a.dt)}
    elif a.cmd == "modulation":
        out = modulation(a.load, a.t_in, a.t_design, a.min_output, a.at)
    elif a.cmd == "volume":
        out = volume(a.min_flow, a.starts, a.system_volume)
    elif a.cmd == "dhw":
        out = dhw(a.volume, a.t_target, a.t_cold, a.power)
    elif a.cmd == "cities":
        out = CITY_MIN_TEMP
    else:
        out = selftest()
    json.dump(out, sys.stdout, indent=2, ensure_ascii=False)
    print()


if __name__ == "__main__":
    main()

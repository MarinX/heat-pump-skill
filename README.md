<p align="center">
  <img src="assets/logo.jpg" alt="Heat Pump Skill for Claude: warmth, explained simply." width="100%">
</p>

# Heat Pump Skill

An agent skill that helps Claude **size and troubleshoot residential air-to-water heat pump systems**: heat loss, unit size, flow rates, pipes, system volume, buffers, balancing and hot water tanks. It uses Croatian design temperatures and metric units.

When a question goes beyond what the skill covers, Claude says so instead of guessing.

## Installation

### Claude Code plugin (recommended)

```text
/plugin install heat-pump --marketplace MarinX/heat-pump-skill
```

Updates come through the marketplace. The skill is available as `heat-pump:heat-pump`.

### Claude (desktop or web)

1. Download **[heat-pump.zip](https://github.com/MarinX/heat-pump-skill/releases/latest/download/heat-pump.zip)** from the [latest release](https://github.com/MarinX/heat-pump-skill/releases/latest).
2. In Claude, open **Settings > Features** and upload the ZIP under Skills.

This needs a Pro, Max, Team or Enterprise plan with **code execution** turned on, because the skill runs its calculator in Claude's code sandbox. Uploaded skills apply only to your account.

### Skills CLI (Claude Code, Cursor, OpenCode and other agents)

```bash
npx skills@latest add MarinX/heat-pump-skill
```

Restart or refresh your agent session afterwards.

### Manual (Claude Code)

```bash
git clone https://github.com/MarinX/heat-pump-skill ~/heat-pump-skill
ln -s ~/heat-pump-skill/skills/heat-pump ~/.claude/skills/heat-pump
```

To install for a single project only, link into `<project>/.claude/skills/heat-pump` instead.

### Updating

```bash
npx skills@latest update          # CLI install
git -C ~/heat-pump-skill pull         # manual install
```

## What it does

| Area | Covers |
|---|---|
| **Sizing** | Design outdoor temperature (54 Croatian cities or custom), heat load from a W/m² insulation table or U·A·ΔT + ventilation, required power for underfloor vs radiators, sanity checks against expected W/m² |
| **Oversizing** | Compressor minimum output vs load, the outdoor temperature above which a unit cycles on and off, overpowered thresholds |
| **Hydraulics** | Flow rate at ΔT 5, pipe sizing at ~1 m/s, system volume, buffer or no buffer, underfloor circuit flows, radiator balancing, cooling with fan coils |
| **Hot water** | Tank volume per person, coil surface, heat-up energy and time |
| **Troubleshooting** | Short cycling, low COP, cold or uneven rooms, low-flow errors, frozen plate heat exchangers in cooling, long defrosts |

## Usage

The skill triggers automatically on heat pump questions. Some example prompts:

```text
New house near Osijek, 180 m², good insulation, underfloor heating, 4 people.
What size heat pump, what flow rate, how big a hot water tank, and do we need a buffer?
```

```text
Installer put a 16 kW heat pump in our 150 m² house in Zagreb (radiators, TRVs everywhere).
It goes on and off constantly when it's mild outside. Is it oversized?
```

```text
12 kW heat pump with 4 fan coils with motorised valves, no buffer.
In cooling it keeps throwing low water flow errors. Is the internal pump too weak?
```

### Calculator

The skill does its arithmetic with a standalone Python script (standard library only, Python 3.8+). You can also run it yourself:

```bash
python3 skills/heat-pump/scripts/heat_calc.py size --area 150 --insulation average --city Zagreb --emitter radiators --occupants 4
python3 skills/heat-pump/scripts/heat_calc.py flow 9 --dt 5
python3 skills/heat-pump/scripts/heat_calc.py modulation --load 6.8 --t-in 21 --t-design -3 --min-output 3.14
python3 skills/heat-pump/scripts/heat_calc.py volume --min-flow 9 --starts 2 --system-volume 100
python3 skills/heat-pump/scripts/heat_calc.py dhw --volume 200 --power 7
python3 skills/heat-pump/scripts/heat_calc.py cities
python3 skills/heat-pump/scripts/heat_calc.py selftest   # re-runs the worked examples
```

Run `python3 skills/heat-pump/scripts/heat_calc.py --help` for all subcommands, including `fabric` for room-by-room U·A·ΔT from a JSON file.

## Structure

```
heat-pump-skill/
├── .github/workflows/release.yml   # On a vX.Y.Z tag: test, zip skills/heat-pump, publish a GitHub release
├── .claude-plugin/
│   ├── plugin.json              # Plugin manifest
│   └── marketplace.json         # Lets Claude Code install it from this repo
├── skills/heat-pump/
│   ├── SKILL.md                 # Trigger description and workflows (loaded when the skill activates)
│   ├── references/
│   │   ├── sizing.md            # Design temperature, heat loss, oversizing, COP/SCOP, hot water
│   │   ├── hydraulics.md        # Flow, ΔT, pipes, underfloor circuits, buffers, volume, balancing
│   │   └── troubleshooting.md   # Symptoms -> causes -> checks
│   └── scripts/heat_calc.py     # Calculator
├── evals/<case>/                # claude plugin eval cases: prompt.md + graders/*.md
└── assets/                      # logo.jpg, icon.jpg
```

## References

- **Heat pump calculator:** [kalkulator-dizalice-topline.com](https://kalkulator-dizalice-topline.com/)
- **Video materials:** [HVAC Education Hub on YouTube](https://www.youtube.com/@HVACEducationHub)

## Disclaimer

Results are estimates for an average house. They can vary significantly with the house's shape, construction quality, intended use and other factors. Before final installation, have the design confirmed by a certified HVAC professional.

## Contributing

Issues and pull requests are welcome. After changing the calculator, run `python3 skills/heat-pump/scripts/heat_calc.py selftest`. To check the skill end to end:

```bash
claude plugin eval . --allow-tools "Bash(python3:*)" --no-publish
```

The evals run the calculator inside Claude Code's sandbox. On Linux, that needs `bubblewrap` and `socat` installed.

### Releasing

Bump `version` in `.claude-plugin/plugin.json`, commit, then tag and push:

```bash
git tag v1.0.0 && git push origin v1.0.0
```

The release workflow checks the tag matches the plugin version, runs the calculator self-test, and publishes a GitHub release with `heat-pump.zip` attached.

## License

[MIT](LICENSE)

## Environment

OsdagBridge `dev` at `de8c692b9d346a2c7bc12255c3a3d498bbf4b3b5`, Debian 13 x86_64, Python 3.12.16, PySide6 6.11.3 and OpenSeesPy 3.8.0.0.

## Reproduction

1. Open the desktop plate-girder workflow. Use a 30 m span, 7.5 m carriageway, zero skew, no median or footpath, Custom design mode with default sections, and a 250 mm deck. Set custom weather to 39 m/s, seismic zone II, and 40 °C/10 °C.
2. Keep the default IRC 5 RCC crash barrier. Its saved area and unit weight are 0.3023 m² and 25 kN/m³.
3. Run Design. Compare the crash-barrier line load in the analysis log with the saved load and report Table 2.5.

**Expected:** The solver uses the saved 7.56 kN/m per barrier.

**Actual:** The Input and Output Dictionaries store `typical_section.crash_barrier.load = 7.56` and the report shows the same value, while the analysis log records 6.54 kN/m.

## Source trace and suggested correction

`PlateGirderBridge.add_dead_loads` passes the input dictionary to `crash_barrier_load_from_inputs` in `src/osdagbridge/core/bridge_components/super_structure/crash_barrier/geometry.py`. The helper reads the legacy `crash_barrier_load` key, so the solver receives no override and applies its default 6.54 kN/m. Prefer the canonical key and keep the legacy key for older callers. The isolated regression test checks the desktop key, legacy key, missing value and explicit zero.

[WP6 reproduction and test evidence](https://github.com/srivastavaprisha29-ops/OsdagBridge-Testing/tree/a7ecc136b978872583c3682f72044b64136c1b13/evidence/wp6)

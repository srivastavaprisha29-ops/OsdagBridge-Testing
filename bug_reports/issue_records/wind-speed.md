## Environment

OsdagBridge `dev` at `de8c692b9d346a2c7bc12255c3a3d498bbf4b3b5`, Debian 13 x86_64, Python 3.12.16, PySide6 6.11.3 and OpenSeesPy 3.8.0.0.

## Reproduction

1. Open the desktop plate-girder workflow. Use a 30 m span, 7.5 m carriageway, zero skew, no median or footpath, Custom design mode with default section dimensions, and a 250 mm deck.
2. Set project location to custom weather with basic wind speed 39 m/s, seismic zone II, and temperatures of 40 °C and 10 °C. Keep Plain Terrain and 10 m average exposed height.
3. Run Design. Compare the wind pressure in the analysis log against the saved/project-location wind inputs and report Table 3.4.

**Expected:** The solver uses the saved 39 m/s, giving approximately 647.65 N/m² hourly pressure for the selected terrain and height.

**Actual:** The normalized input stores `loading.wind_load.basic_wind_speed = 39`. The report shows 647.65 N/m², while the analysis log shows 463.7 N/m², consistent with a 33 m/s fallback. The report's displayed wind forces come from the solver.

## Source trace and suggested correction

`PlateGirderBridge.add_wind_loads` in `src/osdagbridge/core/bridge_types/plate_girder/plategirderbridge.py` reads the legacy key `basic_wind_speed`. Prefer the canonical desktop key, retain the legacy fallback, and preserve explicit zero for the existing skip branch. The isolated regression test checks desktop, legacy, fallback and zero values.

[WP6 reproduction and test evidence](https://github.com/srivastavaprisha29-ops/OsdagBridge-Testing/tree/a7ecc136b978872583c3682f72044b64136c1b13/evidence/wp6)

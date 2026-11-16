# Output validation

Compared the saved desktop design and generated PDF from the WP4 custom material run, plus the 300 mm deck case from WP5. The upstream revision is `de8c692b9d346a2c7bc12255c3a3d498bbf4b3b5`. The register contains 22 comparisons, with 16 passing and 6 failing. These are output and arithmetic checks on the captured fixtures.

| Check | Reference | Observed |
| --- | --- | --- |
| Slab loads | 0.25 m × 25 kN/m³ and 0.30 m × 25 kN/m³ | 6.25 and 7.50 kN/m² |
| Wearing course | 0.05 m × 25 kN/m³ | 1.25 kN/m² |
| Girder self-weight | 0.03853 m² × 78.5 kN/m³ = 3.024605 kN/m | 3.02470 kN/m |
| Girder self-weight with entered density | 0.03853 m² × 80 kN/m³ = 3.0824 kN/m | 3.02470 kN/m |
| Crash-barrier load | 0.3023 m² × 25 kN/m³ = 7.5575 kN/m | 6.54 kN/m |
| Overall bridge width | 7.5 m + 2 × 0.45 m = 8.4 m | 8.5 m in analysis |
| Wind pressure | 647.65 N/m² at the saved 39 m/s speed | 463.7 N/m² in analysis |
| Girder depth in report | 1.67 m × 1,000 = 1,670 mm | 1.67 mm |

The PDF reproduces span, girder spacing, deck thickness, overall width, three wind forces and two horizontal seismic forces from the Output Dictionary. This report agreement measures transcription. The crash-barrier load and wind-pressure rows belong to calculations using different inputs, as follows:

- **Crash barrier:** The input and report show 7.56 kN/m. The backend helper in `crash_barrier/geometry.py` reads `crash_barrier_load`, while the desktop sends `typical_section.crash_barrier.load`. The solver falls back to 6.54 kN/m.
- **Wind:** The report uses the saved 39 m/s project location value. The backend's `add_wind_loads` reads `basic_wind_speed`, while the desktop sends `loading.wind_load.basic_wind_speed`. The solver uses the 33 m/s fallback. Scaling 647.65 N/m² by (33/39)² yields 463.702 N/m², matching the logged pressure.
- **Stiffeners and CAD:** The G2 bearing-stiffener edit reached the capacity and CAD parameters. The G2 girder-web edit reached the analysis, but the CAD generator received one uniform segment. See [WP4 component evidence](../wp4-components/README.md).
- **Plots:** The three WP5 shear-force diagrams rendered from the current dataset. The virtual display introduced CAD screenshot artifacts. See [WP5 evidence](../wp5/README.md).

To reproduce the register with the full material run and extracted WP5 evidence:

```bash
python scripts/validation/check_output_parity.py /path/to/material-run /path/to/wp5-evidence test_cases/output_validation.csv
```

The arithmetic checks use saved dimensions, stated calculation assumptions and logged values. Independent code-clause and design-capacity verification remain outside this sample.

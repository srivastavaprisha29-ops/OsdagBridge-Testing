# WP7 defect investigation

Pinned upstream dev revision `de8c692b9d346a2c7bc12255c3a3d498bbf4b3b5`. The upstream issue review included open and closed results. Issue #17 asks about crash-barrier post-spacing controls and covers a different behavior from the load fallback. The existing girder-selection and stiffener-preview reports cover different views and interactions from the uniform 3D segment finding.

| Finding | Evidence and candidate correction |
| --- | --- |
| Wind-speed fallback | Desktop key reaches the dictionary but analysis reads a legacy key. Prefer the desktop key, preserve explicit zero, and keep the legacy fallback. |
| Crash-barrier line load fallback | Resolver reads a legacy key; prefer the desktop key and keep the legacy fallback. |
| Bridge width differs in solver | Reproduced on 20, 30 and 45 m fixtures. Use the resolved barrier width in the solver layout DTO. |
| Self-weight multiplier ignored | Saved 1.25, but the same-area girder retained the original line load. Pass the multiplier to the girder self-weight load path and check it is applied once. |
| Custom steel unit weight ignored | Saved 80 kN/m³ and applied 78.5 kN/m³. Resolve the custom material unit weight and use it consistently for applied girder self-weight and report wording. |
| G2 web thickness appears as a uniform CAD section | Analysis used the G2-only section. The CAD DTO exported a shared segment. Populate the per-girder segments from the resolved design sections. |
| Report section dimensions use the wrong units | Table 2.7 labels metre values as mm. Convert dimensions to mm at the report boundary and test the rendered table. |

The two load-key corrections are in [the proposed patch](issue_records/load-input-keys.patch). The other corrections above are source-backed proposals pending regression testing. The Unix socket failure observed during the original native desktop run is specific to the test host. The alternate support configuration remains inconclusive because this revision exposes no desktop controls for it.

## Regression procedure

With the project environment active, run the following once against the pinned source and again after applying the proposed patch in an isolated checkout. Put that checkout's `src` on `PYTHONPATH` if the editable installation points to a different source tree.

```bash
MPIR_CVAR_CH3_INTERFACE_HOSTNAME=127.0.0.1 python /path/to/OsdagBridge-Testing/scripts/validation/check_load_input_regressions.py
```

The isolated harness captures the actual wind speed passed into the grillage call and calls the actual barrier resolver. On the pinned source, four compatibility checks passed and five checks failed. The patch passed all nine checks.

The patched source completed the same 30 m desktop design using the spawn-worker workaround. The log recorded 647.6 N/m² wind pressure and 7,560 N/m per crash barrier. See the [desktop rerun evidence](issue_records/load-fix-desktop.json).

## Upstream reports

GitHub rejected issue creation on the upstream repository with HTTP 403 for both reports. The completed drafts are [wind speed](issue_records/wind-speed.md) and [crash-barrier load](issue_records/crash-barrier.md).

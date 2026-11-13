# First plate-girder baseline

Upstream `dev` at `de8c692b9d346a2c7bc12255c3a3d498bbf4b3b5`. The harness populates the desktop input dock with a synthetic fixture, initializes the additional-input dialog, and clicks Design. It captures dictionaries around the backend handoff. The location uses synthetic weather values, so this run needs no map service.

## Native run

OpenSees completed structural analysis, and the pipeline reached stage 7. The process pool then raised `PermissionError: [Errno 1] Operation not permitted` opening an `AF_UNIX` socket for Python's forkserver. The native run is inconclusive for full design completion. Its output dictionary is partial.

## Width mismatch

The handoff and normalized dictionaries record a 7.5 m carriageway, two 0.45 m crash barriers, and an overall width of 8.4 m. The analysis log reports 8.5 m. In `PlateGirderBridge._build_dtos`, the analysis DTO uses the 0.50 m `DEFAULT_CRASH_BARRIER_WIDTH`. The layout solver in `defaults.py` uses the barrier width from the dictionary. The 0.10 m difference equals twice the 0.05 m difference in barrier widths. This fails the width consistency check. The effect on design quantities still needs investigation.

The analysis also warned about the absent thermal load in several combinations. The backend skips thermal loading when `temperature_load_kN_m2` is absent or zero. This run did not establish the expected thermal behavior.

## Retry with spawn workers

Run the harness with `--spawn` to substitute a spawn-based process pool at runtime. The retry completed with no reported design or desktop error. The input dock locked, the results dataset contained 50 load cases, 126 nodes and 225 elements, and the desktop captured the rendered result. The width mismatch reproduced. The retry verifies workflow completion under the workaround. Report parity and independent engineering verification remain pending.

Run from the upstream checkout in the configured environment with a working display:

```bash
MPIR_CVAR_CH3_INTERFACE_HOSTNAME=127.0.0.1 python ../OsdagBridge-Testing/scripts/validation/run_baseline.py /tmp/osdag-baseline --spawn
```

The evidence ZIP contains the native traceback and partial results, plus the retry's completed output and desktop screenshot.

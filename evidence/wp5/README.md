# Consecutive desktop design runs

Upstream dev commit `de8c692b9d346a2c7bc12255c3a3d498bbf4b3b5`. The harness uses one desktop window and one backend instance. It clicks the real Design and Unlock buttons, supplies Continue to the unlock modal, and captures the CAD view and structural plot after each design. The backend runs with the spawn-worker workaround.

The controlled inputs are span, girder steel grade, deck concrete grade and deck thickness. The first run establishes the baseline. The second edits span and steel grade after unlocking. The third edits the concrete grade and deck thickness while retaining the second run's span and steel grade.

The register tests GUI and dictionary agreement, the resolved analysis span and material grades, CAD dimensions, plot binding, displacement data refresh and clearing when unlocking. Separate PNGs and full dictionaries were captured for each run. These checks exercise state refresh for the specified sequence.

From the upstream checkout with a working display and the configured environment:

```bash
MPIR_CVAR_CH3_INTERFACE_HOSTNAME=127.0.0.1 python ../OsdagBridge-Testing/scripts/validation/check_consecutive_runs.py /tmp/osdag-wp5
```

All three design checks, both unlock checks, and the displacement-array refresh check passed. The run 2 and run 3 displacement hashes differ even though their span and model size are the same. All plot screenshots show rendered shear-force diagrams. The CAD screenshots have graphics artifacts in the 3D viewport on the virtual display. CAD refresh was verified through populated model data, cleared model data after unlock, and current parameter values.

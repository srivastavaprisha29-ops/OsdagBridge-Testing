# Girder, deck, support and load checks

Upstream dev revision `de8c692b9d346a2c7bc12255c3a3d498bbf4b3b5`. The desktop harness used a 30 m span and 10 m carriageway. It edited deck thickness and self-weight factor in Additional Inputs, clicked Save, then clicked Design. The spawn-worker workaround was enabled. The first harness attempt assumed support widgets existed and stopped before design. The rerun recorded their absence and continued.

The Support Conditions tab is commented out in the active Additional Inputs schema. The input dictionary carries Pinned and Roller defaults. Alternate desktop support configurations were unavailable for testing.

The self-weight field explicitly promises to multiply the girder self-weight load case. With 1.25 saved, the analysis logged 3024.70 N/m for a girder with the same area as the baseline. Applying 1.25 to that baseline magnitude gives 3780.88 N/m. Source inspection confirms that `PlateGirderBridge.add_dead_loads` calls `create_self_weight_load` without the field and that the latter computes the load from section area and steel unit weight. The dead-load combination also adds the self-weight load entries without this factor.

Run from the upstream checkout with a working display:

```bash
MPIR_CVAR_CH3_INTERFACE_HOSTNAME=127.0.0.1 python ../OsdagBridge-Testing/scripts/validation/run_baseline.py /tmp/osdag-variations --spawn --variations
```

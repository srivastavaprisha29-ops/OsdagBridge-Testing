# Full desktop designs at the span limits

Both fixtures use a 7.5 m carriageway, zero skew, optimized design mode, and the baseline synthetic weather. Only the span changes. Upstream dev revision is `de8c692b9d346a2c7bc12255c3a3d498bbf4b3b5`.

Run from the upstream checkout with the configured environment and a working display:

```bash
export MPIR_CVAR_CH3_INTERFACE_HOSTNAME=127.0.0.1
python ../OsdagBridge-Testing/scripts/validation/run_baseline.py /tmp/span-20 --spawn --span 20
python ../OsdagBridge-Testing/scripts/validation/run_baseline.py /tmp/span-45 --spawn --span 45
```

The harness uses the spawn worker method and caps the process pool at four workers. A workflow pass requires a completed desktop design, a populated analysis dataset, and agreement among the input span, output span, grillage span and CAD parameter after unit conversion. This checks propagation and workflow completion. Structural code checks and independent engineering validation are outside this comparison.

Both runs passed the workflow and span checks. The 20 m run returned 50 load cases, 84 nodes and 148 elements. The 45 m run returned 50 load cases, 186 nodes and 335 elements. The earlier width mismatch reproduced in both runs (8.4 m in the input dictionary and 8.5 m in the analysis model).

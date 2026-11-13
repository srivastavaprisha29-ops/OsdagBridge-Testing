# Combined custom steel and concrete design

The harness selected Custom in both desktop material controls, populated the real material dialogs, emitted the user-edit signals, and used the dialogs' validation and save method before clicking Design. The first harness pass had omitted the user-edit signals and produced stale generated grade labels. The recorded run includes those signals and uses the spawn-worker workaround.

The checks compare the default desktop material fields, normalized input dictionary, output dictionary, and resolved calculation properties. Steel E is 194.6 GPa after the dialog's E/G/Poisson coupling recomputes it from 76 GPa and a Poisson ratio of 0.28. Steel unit weight is the exception. The dictionaries retain 80 kN/m³, but `_build_material_props` falls back to 78.5 kN/m³ for a custom grade. The girder self-weight calculation also uses the fixed steel unit-weight constant.

The nine register entries are assertions on one combined desktop run. Separate component customizations and PDF report comparison are pending.

From the upstream checkout with a working display:

```bash
MPIR_CVAR_CH3_INTERFACE_HOSTNAME=127.0.0.1 python ../OsdagBridge-Testing/scripts/validation/run_baseline.py /tmp/osdag-custom --spawn --custom-materials
```

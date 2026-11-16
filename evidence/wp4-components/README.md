# Component and report verification

Upstream dev commit `de8c692b9d346a2c7bc12255c3a3d498bbf4b3b5`. Python 3.12.16, PySide6 6.11.3, OpenSeesPy 3.8.0.0. The two component fixtures use a 30 m span, 7.5 m carriageway and Custom design mode. Each test changed a single G2 member through Additional Inputs and used the spawn-worker workaround.

- The G2 web changed from 10 to 20 mm in the saved inputs and capacity checks. The analysis web shear area doubled for G2 only. The Output Dictionary recorded the converted value in metres. The CAD DTO supplied a uniform 20 mm girder segment, with no per-girder section entries. The CAD generator uses that shared segment when per-girder entries are missing.
- The G2 bearing stiffener changed from 10 × 250 mm to 16 × 200 mm. The values reached the capacity calculator and G2 CAD parameters. Other girders retained 10 × 250 mm.
- The custom material report reproduced both grade labels. Its loads table labelled the entered 80 kN/m³ as applied, while the resolved material properties used 78.5 kN/m³. The report's section dimensions table also labelled metre values as millimetres. For example, it displayed 1.67 mm for the 1,670 mm girder depth. The figures were disabled for this numerical comparison.
- The initial component harness attempts treated thickness dropdowns as text fields. Those attempts stopped before design. The final runs used the real dropdown and text field signals.

From the upstream checkout with the project environment and a working display:

```bash
export MPIR_CVAR_CH3_INTERFACE_HOSTNAME=127.0.0.1
python ../OsdagBridge-Testing/scripts/validation/run_baseline.py /tmp/web --spawn --component girder
python ../OsdagBridge-Testing/scripts/validation/run_baseline.py /tmp/stiffener --spawn --component stiffener
python ../OsdagBridge-Testing/scripts/validation/run_baseline.py /tmp/material --spawn --custom-materials --report
```

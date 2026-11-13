# OsdagBridge environment and desktop launch

| Item | Observed value |
| --- | --- |
| Host | Debian GNU/Linux 13, x86_64 |
| Git | 2.52.0 |
| Miniconda | Conda 26.9.4 |
| VS Code | 1.146.0, x64, verified by its version command |
| Project Python | 3.12.16 |
| OsdagBridge | 1.0.0, editable installation |
| Osdag | 2026.04.0.0 |
| PySide6 | 6.11.3 |
| pythonocc-core | 8.0.1.2 |
| OpenSeesPy | 3.8.0.0 |
| Repository | osdag-admin/OsdagBridge |
| Branch and commit | dev at de8c692b9d346a2c7bc12255c3a3d498bbf4b3b5 |

The local checkout tracks `upstream/dev`. The requested fork could not be verified under the user's GitHub account, and the available GitHub actions did not expose fork creation. GitHub CLI had no signed-in account. A fork and its `origin` remote are pending.

## Installation and launch

The Miniconda bootstrap added the `defaults` channel to its base configuration. Conda initially stopped at the default-channel terms check. Replacing that base configuration's channel list with `conda-forge` allowed the unchanged project `environment.yml` to install using the declared `osdag`, `geompy`, and `conda-forge` channels. Conda and pip both completed successfully.

The default OpenSeesPy import aborted during MPI network interface discovery in this environment. The import succeeded after setting `MPIR_CVAR_CH3_INTERFACE_HOSTNAME=127.0.0.1`. A temporary OpenSeesPy 3.7.1.2 test reproduced the abort. The final launch used the original 3.8.0.0 dependencies.

Run from the checkout after activating the environment:

```bash
MPIR_CVAR_CH3_INTERFACE_HOSTNAME=127.0.0.1 python -m osdagbridge.desktop
```

On this host the smoke check used a virtual X.Org display with Mesa llvmpipe software rendering. The OsdagBridge window appeared, the OpenGL viewer initialized, and the process stayed up through screenshot capture. See the window tree, desktop log, and screenshot under `evidence/`. This establishes startup only. Bridge analysis and design outputs remain untested.

The full package inventory is in `package-versions.txt`.

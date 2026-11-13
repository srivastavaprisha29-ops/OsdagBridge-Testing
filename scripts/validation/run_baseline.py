"""Run a synthetic plate-girder fixture through the desktop Design button."""

import argparse
import json
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from osdagbridge.desktop.__main__ import CustomWindow, PlateGirderBridge
from osdagbridge.core.utils.common import (
    KEY_CARRIAGEWAY_WIDTH,
    KEY_PROJECT_LOCATION,
    KEY_SKEW_ANGLE,
    KEY_SPAN,
)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("evidence", type=Path)
    parser.add_argument("--spawn", action="store_true", help="Use the application's alternate worker start method")
    args = parser.parse_args()
    evidence = args.evidence
    if args.spawn:
        from osdagbridge.core.utils import connect

        def spawn_pool(max_workers):
            return ProcessPoolExecutor(
                max_workers=max_workers, mp_context=multiprocessing.get_context("spawn")
            )

        connect.design_pool = spawn_pool
    evidence.mkdir(parents=True, exist_ok=True)

    def save(name, data):
        (evidence / f"{name}.json").write_text(
            json.dumps(data, indent=2, default=str) + "\n"
        )

    class ObservedBridge(PlateGirderBridge):
        def set_input(self, inputs):
            save("input-handoff", inputs)
            super().set_input(inputs)
            save("input-normalized", self.input_dict)

    class ObservedWindow(CustomWindow):
        def _show_design_error(self, traceback):
            save("desktop-error", {"traceback": traceback})
            self._finish_loading()

        def _on_design_done(self, error, traceback, cancelled):
            save("design-status", {
                "error": str(error) if error else None,
                "traceback": traceback,
                "cancelled": cancelled,
            })
            save("output", dict(self.backend.output_dict))
            super()._on_design_done(error, traceback, cancelled)
            dataset = self.backend.get_results_dataset() if not error else None
            save("desktop-status", {
                "input_locked": self.input_dock.is_locked,
                "dataset_dimensions": dict(dataset.sizes) if dataset is not None else {},
            })
            self.grab().save(str(evidence / "desktop-result.png"))
            QTimer.singleShot(0, app.quit)

    app = QApplication([])
    window = ObservedWindow("OsdagBridge baseline", ObservedBridge)
    window.resize(1250, 760)
    window.show()

    def run():
        weather = {
            "wind_speed": 39, "zone": "II", "z_value": 0.1,
            "max_temp": 40, "min_temp": 10,
        }
        fixture = {
            **window.input_dict,
            KEY_SPAN: 30.0,
            KEY_CARRIAGEWAY_WIDTH: 7.5,
            KEY_SKEW_ANGLE: 0,
            KEY_PROJECT_LOCATION: {
                "method": "custom_data", "data": {}, "weather_data": weather,
                "custom_weather_data": weather, "display_text": "",
                "show_display": False,
            },
        }
        save("fixture", fixture)
        window.input_dock.populate_from_dict(fixture)
        window._get_additional_inputs().set_input_dictionary(window.input_dict)
        window.input_dock.design_btn.click()

    QTimer.singleShot(500, run)
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())

"""Check three designs and two confirmed unlocks in one desktop session."""

import argparse
import hashlib
import json
import multiprocessing
import os
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QLineEdit

from osdagbridge.core.utils import common, connect
from osdagbridge.desktop.__main__ import CustomWindow, PlateGirderBridge
from osdagbridge.desktop.ui.docks import input_dock


def spawn_pool(max_workers):
    return ProcessPoolExecutor(
        max_workers=min(max_workers, 4), mp_context=multiprocessing.get_context("spawn")
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("evidence", type=Path)
    root = parser.parse_args().evidence
    root.mkdir(parents=True, exist_ok=True)
    connect.design_pool = spawn_pool
    app = QApplication([])
    runs = []
    unlocks = []
    errors = []
    index = 0
    span_key = common.KEY_SPAN
    steel_key = common.KEY_GIRDER
    concrete_key = common.KEY_DECK_CONCRETE_GRADE_BASIC
    deck_key = common.KEY_TS_DECK_THICKNESS
    keys = (span_key, steel_key, concrete_key, deck_key)

    def write(path, data):
        path.write_text(json.dumps(data, indent=2, default=str) + "\n")

    def run_folder():
        folder = root / f"run-{index + 1}"
        folder.mkdir(exist_ok=True)
        return folder

    class ObservedBridge(PlateGirderBridge):
        def set_input(self, inputs):
            super().set_input(inputs)
            write(run_folder() / "inputs.json", self.input_dict)

    class ObservedWindow(CustomWindow):
        def _show_design_error(self, traceback):
            errors.append(traceback)
            self._finish_loading()

        def _on_design_done(self, error, traceback, cancelled):
            super()._on_design_done(error, traceback, cancelled)
            if error or cancelled:
                errors.append(traceback or str(error or "Cancelled"))
            QTimer.singleShot(0, finish_run)

    window = ObservedWindow("OsdagBridge consecutive runs", ObservedBridge)
    window.resize(1250, 760)
    window.show()
    dock = window.input_dock

    def finish_run():
        nonlocal index
        if errors:
            write(root / "errors.json", errors)
            app.exit(1)
            return
        folder = run_folder()
        backend = window.backend
        dataset = backend.get_results_dataset()
        plot = window.plots_widget
        cad = window.cad_3d_widget.generator
        params = backend.get_3d_cad_parameters()
        write(folder / "outputs.json", dict(backend.output_dict))
        window.grab().save(str(folder / "cad.png"))
        window.plots_view_toggle()
        plot.update_plot()
        app.processEvents()
        window.grab().save(str(folder / "plot.png"))

        runs.append({
            "run": index + 1,
            "pid": os.getpid(),
            "gui": {
                span_key: float(dock._w(span_key).text()),
                steel_key: dock._material_combo_map[steel_key].currentText(),
                concrete_key: dock._material_combo_map[concrete_key].currentText(),
            },
            "input": {key: backend.input_dict.get(key) for key in keys},
            "output": {key: backend.output_dict.get(key) for key in keys},
            "analysis_span_m": backend.grillage_geometry.L,
            "resolved_steel": backend.material_props.steel_prop.grade,
            "resolved_concrete": backend.material_props.concrete_prop.grade,
            "cad_span_mm": params.span_length_L,
            "cad_deck_mm": params.deck_thickness,
            "cad_generated": bool(cad.model_data),
            "plot_bound_to_current_dataset": plot._ds_all is dataset,
            "plot_axes_count": len(plot._fig.axes),
            "dataset_sizes": dict(dataset.sizes),
            "results_hashes": {name: hashlib.sha256(array.values.tobytes()).hexdigest()
                                for name, array in dataset.data_vars.items()},
            "locked": dock.is_locked,
        })
        write(root / "results.json", {"runs": runs, "unlocks": unlocks})
        if index == 2:
            app.quit()
            return

        original_dialog = input_dock.CustomMessageBox

        class ConfirmUnlock(original_dialog):
            def exec(self):
                return "Continue"

        input_dock.CustomMessageBox = ConfirmUnlock
        try:
            dock.lock_btn.click()
        finally:
            input_dock.CustomMessageBox = original_dialog
        unlocks.append({
            "after_run": index + 1,
            "unlocked": not dock.is_locked,
            "design_enabled": dock.design_btn.isEnabled(),
            "output_empty": not backend.output_dict,
            "analysis_cleared": backend.get_results_dataset() is None,
            "cad_cleared": not cad.model_data,
            "plot_dataset_cleared": plot._ds_all is None,
            "plot_axes_cleared": not plot._fig.axes,
        })
        write(root / "results.json", {"runs": runs, "unlocks": unlocks})
        index += 1
        QTimer.singleShot(0, start_run)

    def start_run():
        if index == 0:
            weather = {"wind_speed": 39, "zone": "II", "z_value": 0.1,
                       "max_temp": 40, "min_temp": 10}
            dock.populate_from_dict({
                **window.input_dict, span_key: 20, common.KEY_CARRIAGEWAY_WIDTH: 7.5,
                common.KEY_SKEW_ANGLE: 0,
                common.KEY_PROJECT_LOCATION: {
                    "method": "custom_data", "data": {}, "weather_data": weather,
                    "custom_weather_data": weather, "display_text": "", "show_display": False,
                },
            })
            window._get_additional_inputs().set_input_dictionary(window.input_dict)
        elif index == 1:
            span = dock._w(span_key)
            span.setText("25")
            span.editingFinished.emit()
            dock._material_combo_map[steel_key].setCurrentText("E 250A")
        else:
            dock._material_combo_map[concrete_key].setCurrentText("M45")
            window.common_design_func("Additional Inputs")
            dialog = window._get_additional_inputs()
            field = dialog.findChild(QLineEdit, deck_key)
            field.setText("300")
            field.editingFinished.emit()
            from osdagbridge.desktop.ui.dialogs.additional_input import additional_inputs
            original_dialog = additional_inputs.CustomMessageBox

            class AcknowledgeSave(original_dialog):
                def exec(self):
                    return "OK"

            additional_inputs.CustomMessageBox = AcknowledgeSave
            try:
                dialog.save_button.click()
            finally:
                additional_inputs.CustomMessageBox = original_dialog
            dialog.close()
        dock.design_btn.click()

    QTimer.singleShot(500, start_run)
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())

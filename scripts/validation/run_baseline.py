"""Run a synthetic plate-girder fixture through the desktop Design button."""

import argparse
import json
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QComboBox, QLineEdit, QWidget

from osdagbridge.desktop.__main__ import CustomWindow, PlateGirderBridge
from osdagbridge.core.utils.common import (
    KEY_CARRIAGEWAY_WIDTH,
    KEY_PROJECT_LOCATION,
    KEY_SKEW_ANGLE,
    KEY_SPAN,
    KEY_DESIGN_MODE,
    KEY_MP_GD_SELECT_GIRDER,
    KEY_MP_GIRDER_WEB_THICKNESS,
    KEY_MP_STIFFENER_SELECT_MEMBER_ID,
    KEY_MP_STIFFENER_BEARING_THICKNESS,
    KEY_MP_STIFFENER_BEARING_OUTSTAND,
    KEY_GIRDER,
    KEY_DECK_CONCRETE_GRADE_BASIC,
    KEY_PL_SELF_WEIGHT_FACTOR,
    KEY_SC_LEFT_SUPPORT,
    KEY_SC_RIGHT_SUPPORT,
    KEY_TS_DECK_THICKNESS,
)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("evidence", type=Path)
    parser.add_argument("--spawn", action="store_true", help="Use the application's alternate worker start method")
    parser.add_argument("--span", type=float, default=30.0, help="Span in metres")
    parser.add_argument("--variations", action="store_true", help="Exercise geometry and additional inputs")
    parser.add_argument("--custom-materials", action="store_true")
    parser.add_argument("--component", choices=("girder", "stiffener"))
    parser.add_argument("--report", action="store_true")
    args = parser.parse_args()
    evidence = args.evidence
    if args.spawn:
        from osdagbridge.core.utils import connect

        def spawn_pool(max_workers):
            return ProcessPoolExecutor(
                max_workers=min(max_workers, 4), mp_context=multiprocessing.get_context("spawn")
            )

        connect.design_pool = spawn_pool
    evidence.mkdir(parents=True, exist_ok=True)

    def save(name, data):
        (evidence / f"{name}.json").write_text(
            json.dumps(data, indent=2, default=str) + "\n"
        )

    class ObservedBridge(PlateGirderBridge):
        def _build_material_props(self):
            properties = super()._build_material_props()
            save("calculation-materials", {
                "steel": vars(properties.steel_prop),
                "concrete": vars(properties.concrete_prop),
            })
            return properties

        def _run_dcr_checks(self, dataset):
            if not args.component:
                return super()._run_dcr_checks(dataset)
            from osdagbridge.core.bridge_types.plate_girder import designer

            calculator = designer.IRC22CapacityCalculator
            applied = []

            class ObservedCalculator(calculator):
                def compute_all(self, *values, **options):
                    applied.append({
                        "section": vars(self.cfg.section),
                        "stiffener": vars(self.cfg.stiffener),
                    })
                    return super().compute_all(*values, **options)

            designer.IRC22CapacityCalculator = ObservedCalculator
            try:
                return super()._run_dcr_checks(dataset)
            finally:
                designer.IRC22CapacityCalculator = calculator
                save("calculation-components", applied)

        def setup_grillage(self):
            super().setup_grillage()
            if args.component:
                save("analysis-sections", [vars(section) for section in self.grillage_model.girder_props])

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
            cad = self.backend.get_3d_cad_parameters() if not error and not cancelled else None
            save("desktop-status", {
                "cad_girders": cad.num_girders if cad else None,
                "cad_deck_mm": cad.deck_thickness if cad else None,
                "analysis_grid_lines": self.backend.grillage_geometry.n_l if dataset is not None else None,
                "analysis_span_m": self.backend.grillage_geometry.L if dataset is not None else None,
                "cad_span_mm": cad.span_length_L if cad is not None else None,
                "input_locked": self.input_dock.is_locked,
                "dataset_dimensions": dict(dataset.sizes) if dataset is not None else {},
            })
            if args.component and cad:
                save("component-cad", {
                    "web_mm": cad.girder_section_tw,
                    "girder_segments": cad.girder_segments_dict,
                    "stiffeners": cad.stiffeners_dict,
                })
            self.grab().save(str(evidence / "desktop-result.png"))
            QTimer.singleShot(0, export_report if args.report and cad else app.quit)

    app = QApplication([])
    window = ObservedWindow("OsdagBridge baseline", ObservedBridge)
    window.resize(1250, 760)
    window.show()

    def export_report():
        from osdagbridge.core.reports.report_generator import ReportMetadata, ReportOptions, ReportRequest

        request = ReportRequest(
            ReportMetadata("Custom Material Test", "", "", "", ""),
            ReportOptions(["loads"], False, False, True),
            str(evidence), "Custom_Material_Design_Report",
        )
        try:
            result = window.backend.generate_design_report(request, {})
            save("report-status", {"pdf": bool(result.pdf_path), "tex": bool(result.tex_path)})
        finally:
            app.quit()

    def run():
        weather = {
            "wind_speed": 39, "zone": "II", "z_value": 0.1,
            "max_temp": 40, "min_temp": 10,
        }
        fixture = {
            **window.input_dict,
            KEY_SPAN: args.span,
            **({KEY_DESIGN_MODE: "Custom"} if args.component else {}),
            KEY_CARRIAGEWAY_WIDTH: 10.0 if args.variations else 7.5,
            KEY_SKEW_ANGLE: 0,
            KEY_PROJECT_LOCATION: {
                "method": "custom_data", "data": {}, "weather_data": weather,
                "custom_weather_data": weather, "display_text": "",
                "show_display": False,
            },
        }
        save("fixture", fixture)
        window.input_dock.populate_from_dict(fixture)
        if args.variations or args.component:
            from osdagbridge.desktop.ui.dialogs.additional_input import additional_inputs

            class RecordDialog:
                def __init__(self, **details):
                    messages.append({"title": details["title"], "text": details["text"]})

                def exec(self):
                    return 0

            messages = []
            additional_inputs.CustomMessageBox = RecordDialog
            if args.component:
                window.input_dock._on_design_mode_changed("Custom")
            else:
                window.common_design_func("Additional Inputs")
            dialog = window._get_additional_inputs()
            changes = ((KEY_TS_DECK_THICKNESS, "300"), (KEY_PL_SELF_WEIGHT_FACTOR, "1.25"))
            if args.component == "girder":
                selector = dialog.findChild(QComboBox, KEY_MP_GD_SELECT_GIRDER)
                selector.setCurrentIndex(1)
                changes = ((KEY_MP_GIRDER_WEB_THICKNESS, "20"),)
            if args.component == "stiffener":
                selector = dialog.findChild(QComboBox, KEY_MP_STIFFENER_SELECT_MEMBER_ID)
                selector.setCurrentText("G2M1")
                if selector.currentText() != "G2M1":
                    raise RuntimeError("Could not select bearing stiffener G2M1")
                changes = ((KEY_MP_STIFFENER_BEARING_THICKNESS, "16"),
                           (KEY_MP_STIFFENER_BEARING_OUTSTAND, "200"))
            if args.component:
                save("component-defaults", {
                    key: [dialog.working_input_dict.get(f"{key}.G{i}.M1") for i in range(1, 5)]
                    for key, _ in changes
                })
            for key, value in changes:
                field = dialog.findChild(QWidget, key)
                if not isinstance(field, (QLineEdit, QComboBox)):
                    field = field.currentWidget()
                if isinstance(field, QComboBox):
                    if field.findText(value) < 0:
                        raise ValueError(f"{key} has no option {value}")
                    field.setCurrentText(value)
                else:
                    field.setText(value)
                    field.editingFinished.emit()

            support_options = {}
            for key in (KEY_SC_LEFT_SUPPORT, KEY_SC_RIGHT_SUPPORT):
                combo = dialog.findChild(QComboBox, key)
                if combo is None:
                    support_options[key] = {"selected": window.input_dict.get(key), "widget_available": False}
                    continue
                support_options[key] = {
                    "selected": combo.currentText(),
                    "enabled": [combo.itemText(i) for i in range(combo.count())
                                if combo.model().item(i).isEnabled()],
                }
            dialog.save_button.click()
            save("additional-inputs", {
                "supports": support_options, "messages": messages,
                "deck_mm": window.input_dict[KEY_TS_DECK_THICKNESS],
                "self_weight_factor": window.input_dict[KEY_PL_SELF_WEIGHT_FACTOR],
            })
            dialog.close()
        else:
            window._get_additional_inputs().set_input_dictionary(window.input_dict)
        if args.custom_materials:
            from osdagbridge.desktop.ui.docks import input_dock

            custom_fields = {
                KEY_GIRDER: {
                    "material.girder.fy": "345", "material.girder.fu": "510",
                    "material.girder.e": "195", "material.girder.density": "80",
                    "material.girder.poisson": "0.28", "material.girder.g": "76",
                },
                KEY_DECK_CONCRETE_GRADE_BASIC: {
                    "material.deck.fck": "42", "material.deck.fctm": "3.4",
                    "material.deck.ecm": "34",
                },
            }
            dock = window.input_dock
            dock._prime_material_inputs()
            save("default-materials", {
                key: value for key, value in window.input_dict.items()
                if key.startswith("material.")
            })

            class FixtureMaterialDialog(input_dock.MaterialPropertiesDialog):
                def exec(self):
                    for key, value in custom_fields[self.member].items():
                        self.field_inputs[key].setText(value)
                        self.field_inputs[key].textEdited.emit(value)
                    self._validate_and_save()
                    return self.result()

            input_dock.MaterialPropertiesDialog = FixtureMaterialDialog
            for member in custom_fields:
                combo = dock._material_combo_map[member]
                combo.setCurrentText(input_dock.MATERIAL_CUSTOM_OPTION)
                if combo.currentText() == input_dock.MATERIAL_CUSTOM_OPTION:
                    raise RuntimeError(f"Custom material was not saved for {member}")

        window.input_dock.design_btn.click()

    QTimer.singleShot(500, run)
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())

"""Exercise desktop geometry edit signals and the OSI validation gate."""

import csv
from pathlib import Path
import sys

from PySide6.QtWidgets import QApplication
from osdagbridge.desktop.__main__ import CustomWindow, PlateGirderBridge
from osdagbridge.desktop.ui.docks import input_dock
from osdagbridge.core.utils.common import KEY_SPAN, KEY_CARRIAGEWAY_WIDTH, KEY_INCLUDE_MEDIAN
from osdagbridge.core.utils.osi_validator import validate_osi_inputs


def main():
    cases = [
        ("F04", KEY_SPAN, "20", "No", 20, False),
        ("F05", KEY_SPAN, "45", "No", 45, False),
        ("F06", KEY_SPAN, "19.99", "No", 20, True),
        ("F07", KEY_SPAN, "45.01", "No", 45, True),
        ("F08", KEY_SPAN, "0", "No", 20, True),
        ("F09", KEY_SPAN, "-1", "No", 20, True),
        ("F10", KEY_CARRIAGEWAY_WIDTH, "4.25", "No", 4.25, False),
        ("F11", KEY_CARRIAGEWAY_WIDTH, "23.61", "No", 23.6, True),
        ("F12", KEY_CARRIAGEWAY_WIDTH, "4.25", "Yes", 7.5, True),
    ]
    app = QApplication([])
    window = CustomWindow("Geometry validation", PlateGirderBridge)
    dock = window.input_dock
    warnings = []

    class RecordWarning:
        def __init__(self, **details):
            warnings.append(details["text"])

        def exec(self):
            return 0

    # Capture the modal message without blocking the automated test.
    input_dock.CustomMessageBox = RecordWarning
    initial = dict(window.input_dict)
    output = Path(sys.argv[1]).open("w", newline="")
    writer = csv.writer(output)
    writer.writerow(["id", "field", "entered_m", "median", "expected_m",
                     "expected_warning", "actual_widget_m", "actual_dict_m",
                     "warning", "osi_accepted", "result"])
    for case_id, key, entered, median, expected, should_warn in cases:
        values = {**initial, KEY_SPAN: 30, KEY_CARRIAGEWAY_WIDTH: 7.5,
                  KEY_INCLUDE_MEDIAN: median}
        dock.populate_from_dict(values)
        warnings.clear()
        field = dock._w(key)
        field.setText(entered)
        field.editingFinished.emit()
        actual = field.text()
        stored = window.input_dict[key]
        osi_accepted = validate_osi_inputs({**values, key: entered}).is_valid
        passed = (float(actual) == float(stored) == expected
                  and bool(warnings) == should_warn
                  and osi_accepted != should_warn)
        writer.writerow([case_id, key, entered, median, expected, should_warn,
                         actual, stored, " | ".join(warnings), osi_accepted,
                         "Pass" if passed else "Fail"])
    output.close()
    window.close()
    app.quit()


if __name__ == "__main__":
    main()

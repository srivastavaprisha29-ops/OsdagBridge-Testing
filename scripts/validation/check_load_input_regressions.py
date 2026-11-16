"""Exercise desktop load keys at the wind and crash-barrier backend boundaries."""

import json
import math
from types import SimpleNamespace

from osdagbridge.core.bridge_components.super_structure.crash_barrier.geometry import (
    crash_barrier_dead_load_kN_m,
    crash_barrier_load_from_inputs,
)
from osdagbridge.core.bridge_types.plate_girder.plategirderbridge import PlateGirderBridge
from osdagbridge.core.utils import common
from osdagbridge.core.utils.codes.irc6_2017 import IRC6_2017


def wind_speed(fields):
    observed = []
    bridge = SimpleNamespace(
        additional_inputs=fields,
        input_dict={common.KEY_TS_NO_OF_GIRDERS: 4, common.KEY_TS_GIRDER_SPACING: 2.1},
        grillage_model=SimpleNamespace(
            create_wind_load=lambda **options: observed.append(options["basic_wind_speed"])
        ),
        _girder_count=lambda: 4,
        _girder_value=lambda key, index: 1.67,
    )
    PlateGirderBridge.add_wind_loads(bridge)
    return observed[0] if observed else None


def barrier_load(fields):
    return crash_barrier_dead_load_kN_m(crash_barrier_load_from_inputs(fields))


def main():
    wind_key = common.KEY_WL_BASIC_WIND_SPEED
    barrier_key = common.KEY_CB_LOAD
    desktop_speed = wind_speed({wind_key: 39})
    cases = [
        ("desktop wind speed", 39, desktop_speed),
        ("legacy wind speed", 37, wind_speed({"basic_wind_speed": 37})),
        ("missing wind speed", 33, wind_speed({})),
        ("explicit zero wind skips load", None, wind_speed({wind_key: 0})),
        ("desktop barrier load", 7.56, barrier_load({barrier_key: 7.56})),
        ("legacy barrier load", 5.5, barrier_load({"crash_barrier_load": 5.5})),
        ("missing barrier load", 6.54, barrier_load({})),
        ("explicit zero barrier load", 0, barrier_load({barrier_key: 0})),
    ]
    pressure = IRC6_2017.table_12(10, "plain", desktop_speed)["Pz"]
    cases.append(("pressure from desktop wind speed", 647.65, round(pressure, 2)))
    results = []
    for name, expected, observed in cases:
        passed = expected == observed if expected is None or observed is None else math.isclose(expected, observed)
        results.append({"check": name, "expected": expected, "observed": observed, "pass": passed})
    print(json.dumps(results, indent=2))
    return 0 if all(case["pass"] for case in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())

# -*- coding: utf-8 -*-
"""Normalize governance controls and retain legacy environment aliases."""

TRUE_VALUES = ("1", "true", "yes", "on")
FALSE_VALUES = ("0", "false", "no", "off")
SCANNERS = ("window", "signature", "callback", "supplement")
SCAN_FLAGS = {
    "window": "DIAGNOSTICS_WINDOW_SCAN_ENABLED",
    "signature": "DIAGNOSTICS_SIGNATURE_SCAN_ENABLED",
    "callback": "DIAGNOSTICS_CALLBACK_SCAN_ENABLED",
    "supplement": "DIAGNOSTICS_SUPPLEMENT_SCAN_ENABLED",
}


def _legacy_bool(environ, name):
    return environ.get("BKAPP_" + name, "0").lower() in TRUE_VALUES


def _choice(environ, key, choices):
    value = environ[key].strip().lower()
    if value not in choices:
        raise ValueError("{} must be one of: {}".format(key, ", ".join(choices)))
    return value


def _check_legacy(environ, key, expected, control, boolean=True):
    if key not in environ:
        return
    actual = environ[key].lower() in TRUE_VALUES if boolean else environ[key].strip().lower()
    if actual != expected:
        raise ValueError("{} conflicts with {}; remove the old setting or make it consistent".format(key, control))


def _detection(environ, result):
    control = "BKAPP_DIAGNOSTICS_DETECTION_ENABLED"
    selection = "BKAPP_DIAGNOSTICS_SCANNERS"
    result["DIAGNOSTICS_DETECTION_ENABLED"] = None
    result["DIAGNOSTICS_SCANNERS"] = None
    legacy_scan = result["DIAGNOSTICS_SCAN_ENABLED"]
    # Retire sampling; its old environment flag now enables window scanning.
    result["DIAGNOSTICS_SCAN_ENABLED"] = False
    # Legacy supplemental detection runs even when all the old scan flags are off.
    result["DIAGNOSTICS_SUPPLEMENT_SCAN_ENABLED"] = True
    if control not in environ:
        if selection in environ:
            raise ValueError("{} requires {}".format(selection, control))
        result["DIAGNOSTICS_WINDOW_SCAN_ENABLED"] = result["DIAGNOSTICS_WINDOW_SCAN_ENABLED"] or legacy_scan
        return
    enabled = _choice(environ, control, TRUE_VALUES + FALSE_VALUES) in TRUE_VALUES
    selected = tuple(
        dict.fromkeys(item.strip() for item in environ.get(selection, ",".join(SCANNERS)).split(",") if item.strip())
    )
    if set(selected) - set(SCANNERS):
        raise ValueError("{} only accepts: {}".format(selection, ", ".join(SCANNERS)))
    result["DIAGNOSTICS_DETECTION_ENABLED"] = enabled
    result["DIAGNOSTICS_SCANNERS"] = selected
    # Old SCAN=0 never vetoed WINDOW=1. Only an explicitly enabled alias conflicts
    # with new controls that disable windows.
    if legacy_scan:
        _check_legacy(environ, "BKAPP_DIAGNOSTICS_SCAN_ENABLED", enabled and "window" in selected, control)
    for scanner, name in SCAN_FLAGS.items():
        value = enabled and scanner in selected
        if scanner != "supplement":
            _check_legacy(environ, "BKAPP_" + name, value, control)
        result[name] = value


def _fence(environ, result):
    control = "BKAPP_PIPELINE_FENCE_MODE"
    result["PIPELINE_FENCE_MODE"] = None
    if control not in environ:
        return
    mode = _choice(environ, control, ("off", "observe", "enforce"))
    result["PIPELINE_FENCE_MODE"] = mode
    # Record synchronous progress in observe/enforce, independently of periodic
    # detection. Pausing scans must not drop ownership checks for in-flight work.
    for name, value in (
        ("PIPELINE_FENCE_EMIT_ENABLED", mode != "off"),
        ("PIPELINE_FENCE_ENFORCE", mode == "enforce"),
        ("PIPELINE_SYNC_ADVANCE_CHECKPOINT_ENABLED", mode != "off"),
        ("DIAGNOSTICS_SYNC_ADVANCE_ENABLED", mode != "off"),
    ):
        _check_legacy(environ, "BKAPP_" + name, value, control)
        result[name] = value


def _recovery(environ, result):
    # Do not reinterpret the existing MODE=preview/apply environment variable.
    control = "BKAPP_DIAGNOSTICS_RECOVERY_POLICY"
    result["DIAGNOSTICS_RECOVERY_POLICY"] = None
    if control not in environ:
        return
    policy = _choice(environ, control, ("off", "preview", "auto"))
    enabled, mode = policy != "off", "apply" if policy == "auto" else "preview"
    _check_legacy(environ, "BKAPP_DIAGNOSTICS_RECOVERY_ENABLED", enabled, control)
    _check_legacy(environ, "BKAPP_DIAGNOSTICS_RECOVERY_MODE", mode, control, boolean=False)
    result["DIAGNOSTICS_RECOVERY_POLICY"] = policy
    result["DIAGNOSTICS_RECOVERY_ENABLED"] = enabled
    result["DIAGNOSTICS_RECOVERY_MODE"] = mode


def _manual_apply(environ, result):
    control = "BKAPP_DIAGNOSTICS_MANUAL_APPLY_ENABLED"
    enabled = result["DIAGNOSTICS_APPLY_ENABLED"]
    if control in environ:
        enabled = _choice(environ, control, TRUE_VALUES + FALSE_VALUES) in TRUE_VALUES
        _check_legacy(environ, "BKAPP_DIAGNOSTICS_APPLY_ENABLED", enabled, control)
    result["DIAGNOSTICS_MANUAL_APPLY_ENABLED"] = enabled
    # The runtime and existing console operations still consume this setting.
    result["DIAGNOSTICS_APPLY_ENABLED"] = enabled


def _observability(environ, result):
    control = "BKAPP_DIAGNOSTICS_OBSERVABILITY_MODE"
    result["DIAGNOSTICS_OBSERVABILITY_MODE"] = None
    if control not in environ:
        return
    mode = _choice(environ, control, ("off", "alerts", "full"))
    result["DIAGNOSTICS_OBSERVABILITY_MODE"] = mode
    for name, enabled in (("DIAGNOSTICS_EVENT_ENABLED", mode == "full"), ("DIAGNOSTICS_ALERT_ENABLED", mode != "off")):
        _check_legacy(environ, "BKAPP_" + name, enabled, control)
        result[name] = enabled


def resolve_switches(environ):
    names = (
        "DIAGNOSTICS_SCAN_ENABLED",
        "DIAGNOSTICS_WINDOW_SCAN_ENABLED",
        "DIAGNOSTICS_SIGNATURE_SCAN_ENABLED",
        "DIAGNOSTICS_CALLBACK_SCAN_ENABLED",
        "PIPELINE_FENCE_EMIT_ENABLED",
        "PIPELINE_FENCE_ENFORCE",
        "DIAGNOSTICS_RECOVERY_ENABLED",
        "DIAGNOSTICS_APPLY_ENABLED",
        "PIPELINE_SYNC_ADVANCE_CHECKPOINT_ENABLED",
        "DIAGNOSTICS_SYNC_ADVANCE_ENABLED",
        "DIAGNOSTICS_EVENT_ENABLED",
        "DIAGNOSTICS_ALERT_ENABLED",
    )
    result = {name: _legacy_bool(environ, name) for name in names}
    result["DIAGNOSTICS_RECOVERY_MODE"] = environ.get("BKAPP_DIAGNOSTICS_RECOVERY_MODE", "preview").strip().lower()
    _detection(environ, result)
    _fence(environ, result)
    _recovery(environ, result)
    _manual_apply(environ, result)
    _observability(environ, result)
    return result

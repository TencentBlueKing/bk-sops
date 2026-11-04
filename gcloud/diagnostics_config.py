# -*- coding: utf-8 -*-
"""Normalize opt-in governance controls without changing legacy environment semantics."""

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
    # Legacy supplemental detection runs even when all the old scan flags are off.
    result["DIAGNOSTICS_SUPPLEMENT_SCAN_ENABLED"] = True
    if control not in environ:
        if selection in environ:
            raise ValueError("{} requires {}".format(selection, control))
        return
    enabled = _choice(environ, control, TRUE_VALUES + FALSE_VALUES) in TRUE_VALUES
    selected = tuple(
        dict.fromkeys(item.strip() for item in environ.get(selection, ",".join(SCANNERS)).split(",") if item.strip())
    )
    if set(selected) - set(SCANNERS):
        raise ValueError("{} only accepts: {}".format(selection, ", ".join(SCANNERS)))
    result["DIAGNOSTICS_DETECTION_ENABLED"] = enabled
    result["DIAGNOSTICS_SCANNERS"] = selected
    # Unified detection uses window scanning; the old sampler remains legacy-only.
    _check_legacy(environ, "BKAPP_DIAGNOSTICS_SCAN_ENABLED", False, control)
    result["DIAGNOSTICS_SCAN_ENABLED"] = False
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
    for name, value in (("PIPELINE_FENCE_EMIT_ENABLED", mode != "off"), ("PIPELINE_FENCE_ENFORCE", mode == "enforce")):
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


def resolve_switches(environ):
    names = (
        "DIAGNOSTICS_SCAN_ENABLED",
        "DIAGNOSTICS_WINDOW_SCAN_ENABLED",
        "DIAGNOSTICS_SIGNATURE_SCAN_ENABLED",
        "DIAGNOSTICS_CALLBACK_SCAN_ENABLED",
        "PIPELINE_FENCE_EMIT_ENABLED",
        "PIPELINE_FENCE_ENFORCE",
        "DIAGNOSTICS_RECOVERY_ENABLED",
    )
    result = {name: _legacy_bool(environ, name) for name in names}
    result["DIAGNOSTICS_RECOVERY_MODE"] = environ.get("BKAPP_DIAGNOSTICS_RECOVERY_MODE", "preview").strip().lower()
    _detection(environ, result)
    _fence(environ, result)
    _recovery(environ, result)
    return result

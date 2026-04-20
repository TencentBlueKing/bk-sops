import pathlib
import unittest

REQUIREMENTS_FILE = pathlib.Path(__file__).resolve().parents[2] / "requirements.txt"


def _get_requirement_version(package_name):
    for raw_line in REQUIREMENTS_FILE.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        name, _, version = line.partition("==")
        if name == package_name and version:
            return version
    raise AssertionError(f"{package_name} is not pinned in requirements.txt")


def _version_tuple(version):
    return tuple(int(part) for part in version.split("."))


class TestRequirementsSecurityVersions(unittest.TestCase):
    def test_protobuf_pinned_to_patched_release(self):
        version = _get_requirement_version("protobuf")
        self.assertGreaterEqual(_version_tuple(version), (5, 29, 6))

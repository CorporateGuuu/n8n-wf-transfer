"""Regression checks for the public Apigee reference, without live services."""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[1]

class ApigeeReferenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        shutil.copytree(SOURCE / "integrations/apigee", self.root / "integrations/apigee")
        (self.root / "scripts").mkdir()
        shutil.copy(SOURCE / "scripts/validate_apigee.py", self.root / "scripts/validate_apigee.py")

    def check(self, expected):
        result = subprocess.run([sys.executable, str(self.root / "scripts/validate_apigee.py")], capture_output=True, text=True)
        self.assertEqual(result.returncode == 0, expected, result.stdout + result.stderr)

    def mutate(self, relative, before, after):
        path = self.root / "integrations/apigee/apiproxy" / relative
        source = path.read_text()
        self.assertIn(before, source)
        path.write_text(source.replace(before, after))

    def test_valid_bundle(self):
        self.check(True)

    def test_target_reference_missing_policy(self):
        self.mutate("targets/default.xml", "<Name>Assign-Fault-Response</Name>", "<Name>Missing</Name>")
        self.check(False)

    def test_fault_enforcement_disabled(self):
        self.mutate("proxies/default.xml", "<AlwaysEnforce>true</AlwaysEnforce>", "<AlwaysEnforce>false</AlwaysEnforce>")
        self.check(False)

    def test_real_hostname_with_placeholder_path(self):
        self.mutate("targets/default.xml", "https://ops-api.example.invalid", "https://live.example.com/example.invalid")
        self.check(False)

    def test_real_hostname_with_placeholder_prefix(self):
        self.mutate("targets/default.xml", "https://ops-api.example.invalid", "https://example.invalid.live.example.com")
        self.check(False)

    def test_jwks_real_host(self):
        self.mutate("policies/Verify-JWT.xml", "identity.example.invalid", "identity.example.com")
        self.check(False)

    def test_status_override_rejected(self):
        self.mutate("policies/Assign-Fault-Response.xml", "<Set>", "<Set><StatusCode>500</StatusCode>")
        self.check(False)

    def test_missing_fault_policy(self):
        (self.root / "integrations/apigee/apiproxy/policies/Assign-Fault-Response.xml").unlink()
        self.check(False)

if __name__ == "__main__":
    unittest.main()

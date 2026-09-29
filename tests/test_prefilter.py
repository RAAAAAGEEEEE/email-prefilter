"""Tests hors ligne de scripts/prefilter_emails.py (DNS simule, aucun reseau)."""
import contextlib
import csv
import io
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import dns.exception  # noqa: E402
import dns.resolver  # noqa: E402

import prefilter_emails as pf  # noqa: E402


class FakeRR:
    def __init__(self, exchange):
        self.exchange = exchange


class FakeResolver:
    """Remplace dns.resolver.Resolver : renvoie ou leve ce que dit `outcome`."""

    outcome = None

    def __init__(self):
        self.timeout = None
        self.lifetime = None

    def resolve(self, domain, rdtype):
        if isinstance(FakeResolver.outcome, Exception):
            raise FakeResolver.outcome
        return FakeResolver.outcome


def check(outcome):
    FakeResolver.outcome = outcome
    pf._mx_cache.clear()
    with mock.patch.object(dns.resolver, "Resolver", FakeResolver):
        return pf._check_mx("exemple.example")


class Syntax(unittest.TestCase):
    def test_valid_and_invalid_addresses(self):
        for ok in ("a@b.fr", "jean.dupont+pro@sous.domaine.com", "x_y%z@a-b.co"):
            self.assertTrue(pf.EMAIL_REGEX.match(ok), ok)
        for bad in ("", "sans-arobase.fr", "a@@b.fr", "a@b", "a b@c.fr", "a@b.f", "@b.fr"):
            self.assertFalse(pf.EMAIL_REGEX.match(bad), bad)

    def test_domain_is_lowercased(self):
        self.assertEqual(pf._domain_of("Jean@GMAIL.com"), "gmail.com")

    def test_personal_domain_is_flagged_not_rejected(self):
        self.assertEqual(pf._classify_domain("gmail.com"), "perso_b2c")
        self.assertIsNone(pf._classify_domain("atelier.example"))
        self.assertNotIn("gmail.com", pf.DISPOSABLE_DOMAINS)
        self.assertIn("mailinator.com", pf.DISPOSABLE_DOMAINS)


class MxResult(unittest.TestCase):
    def test_answer_with_mail_server_is_ok(self):
        self.assertEqual(check([FakeRR("mail.exemple.example.")]), "ok")

    def test_nxdomain_and_noanswer_are_absent(self):
        self.assertEqual(check(dns.resolver.NXDOMAIN()), "absent")
        self.assertEqual(check(dns.resolver.NoAnswer()), "absent")

    def test_null_mx_is_absent(self):
        self.assertEqual(check([FakeRR(".")]), "absent")

    def test_null_mx_mixed_with_real_server_is_ok(self):
        self.assertEqual(check([FakeRR("."), FakeRR("mail.exemple.example.")]), "ok")

    def test_timeout_and_network_errors_are_uncertain_not_rejected(self):
        self.assertEqual(check(dns.exception.Timeout()), "incertain")
        self.assertEqual(check(dns.resolver.NoNameservers()), "incertain")
        self.assertEqual(check(RuntimeError("reseau coupe")), "incertain")

    def test_result_is_cached_per_domain(self):
        FakeResolver.outcome = [FakeRR("mail.exemple.example.")]
        pf._mx_cache.clear()
        with mock.patch.object(dns.resolver, "Resolver", FakeResolver):
            pf._check_mx("exemple.example")
            FakeResolver.outcome = dns.resolver.NXDOMAIN()
            self.assertEqual(pf._check_mx("exemple.example"), "ok")


class Pipeline(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        pf._mx_cache.clear()

    def write(self, name, content, binary=False):
        path = Path(self.tmp) / name
        if binary:
            path.write_bytes(content)
        else:
            path.write_text(content, encoding="utf-8", newline="")
        return path

    def run_prefilter(self, path, stub, **kw):
        def fake(domain, timeout=5.0):
            pf._mx_cache[domain] = stub.get(domain, "incertain")
            return pf._mx_cache[domain]
        out = io.StringIO()
        with mock.patch.object(pf, "_check_mx", fake), contextlib.redirect_stdout(out), \
                contextlib.redirect_stderr(io.StringIO()):
            pf.prefilter(path, **kw)
        return out.getvalue()

    def read(self, name, delimiter=","):
        with (Path(self.tmp) / name).open(newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f, delimiter=delimiter))

    def test_kept_and_rejected_files(self):
        path = self.write("in.csv", "email,nom\nok@bon.example,A\nx@mort.example,B\nnope,C\nt@yopmail.com,D\n")
        self.run_prefilter(path, {"bon.example": "ok", "mort.example": "absent"})
        kept = self.read("emails_a_verifier.csv")
        rejected = {r["nom"]: r["raison_rejet"] for r in self.read("emails_rejetes.csv")}
        self.assertEqual([r["nom"] for r in kept], ["A"])
        self.assertEqual(kept[0]["statut_mx"], "ok")
        self.assertEqual(kept[0]["type_domaine"], "pro")
        self.assertEqual(rejected, {"B": "pas_de_mx", "C": "syntaxe_invalide", "D": "domaine_jetable"})

    def test_other_columns_are_preserved(self):
        path = self.write("in.csv", "ville,email,tel\nLyon,a@bon.example,0102030405\n")
        self.run_prefilter(path, {"bon.example": "ok"})
        row = self.read("emails_a_verifier.csv")[0]
        self.assertEqual((row["ville"], row["tel"]), ("Lyon", "0102030405"))

    def test_uncertain_dns_keeps_the_row(self):
        path = self.write("in.csv", "email\na@flou.example\n")
        self.run_prefilter(path, {"flou.example": "incertain"})
        self.assertEqual(self.read("emails_a_verifier.csv")[0]["statut_mx"], "incertain")

    def test_semicolon_delimiter_and_bom(self):
        path = self.write("in.csv", b"\xef\xbb\xbfSociete;E-mail\r\nA;a@bon.example\r\n", binary=True)
        self.run_prefilter(path, {"bon.example": "ok"}, email_column="E-mail", delimiter=";")
        self.assertEqual(self.read("emails_a_verifier.csv", ";")[0]["Societe"], "A")

    def test_bom_with_default_comma(self):
        path = self.write("in.csv", b"\xef\xbb\xbfemail\na@bon.example\n", binary=True)
        self.run_prefilter(path, {"bon.example": "ok"})
        self.assertEqual(len(self.read("emails_a_verifier.csv")), 1)

    def test_missing_column_exits_with_code_1_and_writes_nothing(self):
        path = self.write("in.csv", "societe,contact\nA,a@bon.example\n")
        with self.assertRaises(SystemExit) as cm:
            self.run_prefilter(path, {})
        self.assertEqual(cm.exception.code, 1)
        self.assertFalse((Path(self.tmp) / "emails_a_verifier.csv").exists())
        self.assertFalse((Path(self.tmp) / "emails_rejetes.csv").exists())

    def test_empty_file_writes_nothing(self):
        path = self.write("in.csv", "email\n")
        out = self.run_prefilter(path, {})
        self.assertIn("vide", out)
        self.assertFalse((Path(self.tmp) / "emails_a_verifier.csv").exists())

    def test_one_dns_lookup_per_distinct_domain(self):
        path = self.write("in.csv", "email\na@bon.example\nb@bon.example\nc@bon.example\n")
        calls = []

        def fake(domain, timeout=5.0):
            calls.append(domain)
            pf._mx_cache[domain] = "ok"
            return "ok"

        with mock.patch.object(pf, "_check_mx", fake), contextlib.redirect_stdout(io.StringIO()), \
                contextlib.redirect_stderr(io.StringIO()):
            pf.prefilter(path)
        self.assertEqual(calls, ["bon.example"])

    def test_summary_is_printed(self):
        path = self.write("in.csv", "email\na@bon.example\nnope\n")
        out = self.run_prefilter(path, {"bon.example": "ok"})
        self.assertIn("=== Resume ===", out)
        self.assertIn("syntaxe_invalide: 1", out)


class NoSmtp(unittest.TestCase):
    def test_script_never_imports_smtplib_or_opens_sockets(self):
        source = Path(ROOT, "scripts", "prefilter_emails.py").read_text(encoding="utf-8")
        self.assertNotIn("smtplib", source)
        self.assertNotIn("import socket", source)


if __name__ == "__main__":
    unittest.main()

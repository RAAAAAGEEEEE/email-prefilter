"""Tests hors ligne de evals/evals.json : structure et rejeu des cas 'pipeline'.

Le DNS est simule (`mx_stub`) : aucun acces reseau. Ils ne lancent pas
Claude ; les assertions de type 'humain' se jugent a la lecture.
"""
import contextlib
import csv
import io
import json
import os
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
EVALS_DIR = os.path.join(ROOT, "evals")
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import prefilter_emails as pf  # noqa: E402


def load():
    with io.open(os.path.join(EVALS_DIR, "evals.json"), encoding="utf-8") as fh:
        return json.load(fh)


def run_case(case, tmp):
    src = Path(EVALS_DIR, case["input_file"])
    dst = Path(tmp) / src.name
    shutil.copy(src, dst)
    stub = case.get("mx_stub", {})

    def fake(domain, timeout=5.0):
        pf._mx_cache[domain] = stub.get(domain, "incertain")
        return pf._mx_cache[domain]

    pf._mx_cache.clear()
    out = io.StringIO()
    code = 0
    with mock.patch.object(pf, "_check_mx", fake), contextlib.redirect_stdout(out), \
            contextlib.redirect_stderr(io.StringIO()):
        try:
            pf.prefilter(dst, email_column=case["cli"]["email_column"], delimiter=case["cli"]["delimiter"])
        except SystemExit as exc:
            code = exc.code
    return out.getvalue(), code


def read(tmp, name, delimiter):
    with (Path(tmp) / name).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter=delimiter))


class Structure(unittest.TestCase):
    def test_at_least_three_realistic_cases(self):
        self.assertGreaterEqual(len(load()["evals"]), 3)

    def test_each_case_is_complete_and_ids_are_unique(self):
        ids = set()
        for case in load()["evals"]:
            self.assertNotIn(case["id"], ids)
            ids.add(case["id"])
            for key in ("prompt", "expected_output", "assertions", "should_trigger"):
                self.assertIn(key, case, case["id"])
            for a in case["assertions"]:
                self.assertIn(a["kind"], ("humain", "pipeline"), case["id"])

    def test_input_files_exist(self):
        for case in load()["evals"]:
            if "input_file" in case:
                self.assertTrue(os.path.isfile(os.path.join(EVALS_DIR, case["input_file"])))

    def test_only_fictional_domains_in_fixtures(self):
        real_ok = {"gmail.com", "orange.fr", "mailinator.com", "yopmail.fr"}
        pattern = re.compile(r"[\w.+-]+@([\w.-]+)", re.I)
        for name in os.listdir(os.path.join(EVALS_DIR, "fixtures")):
            text = Path(EVALS_DIR, "fixtures", name).read_bytes().decode("utf-8", "replace")
            for domain in pattern.findall(text):
                domain = domain.lower().rstrip(".")
                self.assertTrue(domain.endswith(".example") or domain in real_ok or "." not in domain, (name, domain))


class Replay(unittest.TestCase):
    def test_pipeline_cases_match_expected_outputs(self):
        for case in load()["evals"]:
            if case.get("type") != "pipeline":
                continue
            with tempfile.TemporaryDirectory() as tmp:
                _, code = run_case(case, tmp)
                self.assertEqual(code, 0, case["id"])
                d = case["cli"]["delimiter"]
                key = case["key_column"]
                kept = {r[key]: r for r in read(tmp, "emails_a_verifier.csv", d)}
                rejected = {r[key]: r for r in read(tmp, "emails_rejetes.csv", d)}
                self.assertEqual(set(kept), set(case["expected_kept"]), case["id"])
                self.assertEqual(set(rejected), set(case["expected_rejected"]), case["id"])
                for name, expected in case["expected_kept"].items():
                    for col, value in expected.items():
                        self.assertEqual(kept[name][col], value, (case["id"], name, col))
                for name, reason in case["expected_rejected"].items():
                    self.assertEqual(rejected[name]["raison_rejet"], reason, (case["id"], name))

    def test_cli_error_cases(self):
        for case in load()["evals"]:
            if case.get("type") != "cli-error":
                continue
            with tempfile.TemporaryDirectory() as tmp:
                out, code = run_case(case, tmp)
                self.assertEqual(code, case["expected_exit_code"], case["id"])
                self.assertIn(case["expected_stdout_contains"], out)
                self.assertFalse((Path(tmp) / "emails_a_verifier.csv").exists())
                self.assertFalse((Path(tmp) / "emails_rejetes.csv").exists())


if __name__ == "__main__":
    unittest.main()

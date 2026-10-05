"""Tests for tools/wiki.py. Run: python3 -m unittest discover -s tests -v"""

import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, "tools", "wiki.py")
sys.path.insert(0, os.path.join(ROOT, "tools"))
import wiki as W  # noqa: E402


def run(*args, root=None, script=SCRIPT):
    cmd = [sys.executable, script] + (["--root", root] if root else []) + list(args)
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def page(title, ptype, body, summary="A page.", extra=""):
    return "---\ntitle: %s\ntype: %s\nsummary: %s\nupdated: 2026-10-05\n%s---\n\n# %s\n\n%s\n" % (
        title, ptype, summary, extra, title, body)


class WikiTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="wiki-test-")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def new_wiki(self, name, wid):
        path = os.path.join(self.tmp, name)
        code, out = run("new", path, "--id", wid, "--name", name, "--description", "Test wiki",
                        "--scope-in", "testing", "--no-git", "-y", root=ROOT)
        self.assertEqual(code, 0, out)
        return path


class TestNew(WikiTestCase):
    def test_new_wiki_is_clean(self):
        path = self.new_wiki("alpha-wiki", "alpha")
        for args in (("lint",), ("sync", "--check"), ("index", "--check")):
            code, out = run(*args, root=path)
            self.assertEqual(code, 0, out)
        cfg = W.load_config(path)
        self.assertEqual(cfg["id"], "alpha")
        self.assertNotIn("template", cfg)
        self.assertEqual(cfg["scope"]["in"], ["testing"])
        self.assertFalse(os.path.exists(os.path.join(path, "tests")))
        self.assertTrue(os.path.exists(os.path.join(path, ".codex", "agents", "wiki-ingester.toml")))
        self.assertIn("# alpha-wiki", W.read(os.path.join(path, "README.md")))

    def test_template_is_clean(self):
        for args in (("lint",), ("sync", "--check"), ("index", "--check")):
            code, out = run(*args, root=ROOT)
            self.assertEqual(code, 0, out)


class TestIndexAndPending(WikiTestCase):
    def test_index_lint_and_pending(self):
        path = self.new_wiki("beta-wiki", "beta")
        write(os.path.join(path, "raw", "report.md"), "raw text")
        write(os.path.join(path, "raw", "other.md"), "raw text")
        write(os.path.join(path, "wiki", "sources", "src-2026-10-05-report.md"),
              page("Report", "source", "About [[acme]].", extra="raw: raw/report.md\n"))
        write(os.path.join(path, "wiki", "entities", "acme.md"),
              page("Acme", "entity", "Acme grew ([[src-2026-10-05-report]]). See [[missing-page]].",
                   summary="Example company."))
        code, out = run("pending", root=path)
        self.assertEqual(out.strip(), "raw/other.md")
        code, out = run("index", "--check", root=path)
        self.assertEqual(code, 1)
        run("index", root=path)
        index = W.read(os.path.join(path, "wiki", "index.md"))
        self.assertIn("- [[acme]] — Example company. (1 source, updated 2026-10-05)", index)
        self.assertIn("[[src-2026-10-05-report]]", index)
        code, out = run("lint", root=path)
        self.assertEqual(code, 0, out)
        self.assertIn("missing page [[missing-page]]", out)
        self.assertIn("raw file not ingested: raw/other.md", out)
        code, out = run("search", "acme", root=path)
        self.assertIn("[[acme]]", out.splitlines()[0])

    def test_split_index(self):
        path = self.new_wiki("big-wiki", "big")
        cfg = os.path.join(path, "wiki.config.yaml")
        write(cfg, W.read(cfg).replace("split_after: 300", "split_after: 2"))
        for i in range(3):
            write(os.path.join(path, "wiki", "concepts", "c%d.md" % i), page("C%d" % i, "concept", "x"))
        run("index", root=path)
        self.assertIn("[[index-concepts]]", W.read(os.path.join(path, "wiki", "index.md")))
        self.assertTrue(os.path.exists(os.path.join(path, "wiki", "_meta", "index-concepts.md")))
        write(cfg, W.read(cfg).replace("split_after: 2", "split_after: 300"))
        run("index", root=path)
        self.assertFalse(os.path.exists(os.path.join(path, "wiki", "_meta", "index-concepts.md")))


class TestLinkedWikis(WikiTestCase):
    def test_sibling_discovery_and_xlinks(self):
        a = self.new_wiki("platform-wiki", "platform")
        b = self.new_wiki("security-wiki", "security")
        shutil.copytree(ROOT, os.path.join(self.tmp, "llm-wiki"),
                        ignore=shutil.ignore_patterns(".git"))  # template sibling must be ignored
        write(os.path.join(b, "wiki", "concepts", "zero-trust.md"), page("Zero Trust", "concept", "x"))
        write(os.path.join(a, "wiki", "concepts", "mesh.md"),
              page("Mesh", "concept", "See [[security:zero-trust]] and [[security:nope]]."))
        code, out = run("wikis", root=a)
        self.assertEqual(code, 0, out)
        self.assertIn("security", out)
        self.assertNotIn("my-wiki", out)
        code, out = run("xlinks", root=a)
        self.assertEqual(code, 1)
        self.assertIn("OK    wiki/concepts/mesh.md: [[security:zero-trust]]", out)
        self.assertIn("[[security:nope]] page not found", out)
        write(os.path.join(a, "wiki", "concepts", "mesh.md"), page("Mesh", "concept", "See [[ghost:x]]."))
        code, out = run("lint", "--quick", root=a)
        self.assertEqual(code, 1)
        self.assertIn("unknown wiki 'ghost'", out)


class TestUpgrade(WikiTestCase):
    def test_upgrade_from_local(self):
        path = self.new_wiki("gamma-wiki", "gamma")
        agents = os.path.join(path, "AGENTS.md")
        write(agents, "locally modified")
        write(os.path.join(path, "templates", "decision.md"), "custom template")
        write(os.path.join(path, "wiki", "concepts", "keep.md"), page("Keep", "concept", "x"))
        code, out = run("upgrade", "--from", ROOT, root=path)
        self.assertEqual(code, 0, out)
        self.assertIn("updated  AGENTS.md", out)
        self.assertIn("kept     templates/decision.md", out)
        self.assertEqual(W.read(agents), W.read(os.path.join(ROOT, "AGENTS.md")))
        self.assertTrue(os.path.exists(os.path.join(path, "wiki", "concepts", "keep.md")))
        self.assertTrue(os.path.exists(os.path.join(path, ".agents", "framework.lock")))
        self.assertEqual(W.load_config(path)["id"], "gamma")
        self.assertIn("upgrade | Framework", W.read(os.path.join(path, "wiki", "log.md")))

    def test_upgrade_refuses_template(self):
        code, out = run("upgrade", "--from", ROOT, "--dry-run", root=ROOT)
        self.assertNotEqual(code, 0)


class TestLogAndYaml(WikiTestCase):
    def test_log_add(self):
        path = self.new_wiki("delta-wiki", "delta")
        code, out = run("log", "add", "ingest", "Some source", "-m", "Created: [[a]]", root=path)
        self.assertEqual(code, 0, out)
        code, out = run("log", "-n", "1", root=path)
        self.assertRegex(out.strip(), r"^## \[\d{4}-\d{2}-\d{2}\] ingest \| Some source$")
        code, out = run("log", "add", "bogus", "x", root=path)
        self.assertNotEqual(code, 0)

    def test_yaml_subset(self):
        cfg = W.load_yaml(
            'id: x  # comment\nscope:\n  in:\n    - "a: b"\n    - c\nlinked_wikis:\n'
            '  - id: y\n    path: ../y\nflag: true\nn: 3\nlist: [a, b]\ndesc: >\n  one\n  two\n')
        self.assertEqual(cfg["id"], "x")
        self.assertEqual(cfg["scope"]["in"], ["a: b", "c"])
        self.assertEqual(cfg["linked_wikis"], [{"id": "y", "path": "../y"}])
        self.assertIs(cfg["flag"], True)
        self.assertEqual(cfg["n"], 3)
        self.assertEqual(cfg["list"], ["a", "b"])
        self.assertEqual(cfg["desc"], "one two")


if __name__ == "__main__":
    unittest.main()

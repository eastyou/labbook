"""测试命令行入口。"""

from __future__ import annotations

import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from labbook.cli import main

EXAMPLE = Path(__file__).resolve().parent.parent / "examples" / "experiments.csv"


def run_cli(args: list) -> tuple:
    stdout, stderr = io.StringIO(), io.StringIO()
    with redirect_stdout(stdout), redirect_stderr(stderr):
        code = main(args)
    return code, stdout.getvalue(), stderr.getvalue()


class CliTests(unittest.TestCase):
    def test_generates_from_example(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "lab.html"
            code, stdout, _ = run_cli(["-i", str(EXAMPLE), "-o", str(output)])
            self.assertEqual(code, 0)
            self.assertTrue(output.exists())
            content = output.read_text(encoding="utf-8")
            self.assertEqual(content.count('class="sheet"'), 4)
            self.assertIn("已生成", stdout)

    def test_missing_input(self) -> None:
        code, _, stderr = run_cli(["-i", "/tmp/none.csv", "-o", "/tmp/x.html"])
        self.assertEqual(code, 2)
        self.assertIn("文件不存在", stderr)

    def test_invalid_rows(self) -> None:
        code, _, stderr = run_cli(["-i", str(EXAMPLE), "--rows", "20"])
        self.assertEqual(code, 2)
        self.assertIn("记录行数", stderr)

    def test_write_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            code, _, stderr = run_cli(["-i", str(EXAMPLE), "-o", tmp])
            self.assertEqual(code, 1)
            self.assertIn("写入文件失败", stderr)

    def test_custom_title(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "lab.html"
            run_cli(["-i", str(EXAMPLE), "-o", str(output), "--title", "初二物理实验"])
            self.assertIn("初二物理实验", output.read_text(encoding="utf-8"))


if __name__ == "__main__":  # pragma: no cover
    unittest.main()

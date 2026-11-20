"""测试 CSV 加载、分隔符与错误提示。"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from labbook.loader import load_experiments
from labbook.model import Experiment, LabError

EXAMPLE = Path(__file__).resolve().parent.parent / "examples" / "experiments.csv"


def write_temp(text: str, encoding: str = "utf-8") -> Path:
    handle = tempfile.NamedTemporaryFile(
        mode="w", suffix=".csv", delete=False, encoding=encoding
    )
    handle.write(text)
    handle.close()
    return Path(handle.name)


class LoaderTests(unittest.TestCase):
    def test_loads_example_file(self) -> None:
        experiments = load_experiments(str(EXAMPLE))
        self.assertEqual(len(experiments), 4)
        first = experiments[0]
        self.assertEqual(first.name, "探究凸透镜成像规律")
        self.assertEqual(len(first.steps), 4)
        self.assertIn("光具座", first.equipment)
        self.assertTrue(first.safety)

    def test_supports_bom(self) -> None:
        source = write_temp(
            "\ufeff名称,目的,器材,步骤\n测试,验证,尺子,第一步|第二步\n",
            encoding="utf-8",
        )
        try:
            experiments = load_experiments(str(source))
            self.assertEqual(experiments[0].name, "测试")
            self.assertEqual(experiments[0].steps, ("第一步", "第二步"))
        finally:
            source.unlink()

    def test_equipment_separators(self) -> None:
        source = write_temp("名称,目的,器材,步骤\nA,目的,甲、乙;丙,一步\n")
        try:
            experiments = load_experiments(str(source))
            self.assertEqual(experiments[0].equipment, ("甲", "乙", "丙"))
        finally:
            source.unlink()

    def test_missing_column(self) -> None:
        source = write_temp("名称,目的,器材\nA,目的,尺子\n")
        try:
            with self.assertRaises(LabError) as context:
                load_experiments(str(source))
            self.assertIn("缺少必需的列", str(context.exception))
            self.assertIn("步骤", str(context.exception))
        finally:
            source.unlink()

    def test_missing_name_reports_line(self) -> None:
        source = write_temp("名称,目的,器材,步骤\n,目的,尺子,一步\n")
        try:
            with self.assertRaises(LabError) as context:
                load_experiments(str(source))
            self.assertIn("第 2 行", str(context.exception))
        finally:
            source.unlink()

    def test_missing_steps(self) -> None:
        source = write_temp("名称,目的,器材,步骤\nA,目的,尺子,\n")
        try:
            with self.assertRaises(LabError) as context:
                load_experiments(str(source))
            self.assertIn("缺少实验步骤", str(context.exception))
        finally:
            source.unlink()

    def test_skips_blank_rows(self) -> None:
        source = write_temp("名称,目的,器材,步骤\nA,目的,尺子,一步\n,,,\n")
        try:
            experiments = load_experiments(str(source))
            self.assertEqual(len(experiments), 1)
        finally:
            source.unlink()

    def test_missing_file(self) -> None:
        with self.assertRaises(LabError) as context:
            load_experiments("/tmp/不存在的实验清单.csv")
        self.assertIn("文件不存在", str(context.exception))

    def test_directory_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(LabError) as context:
                load_experiments(tmp)
            self.assertIn("目录", str(context.exception))

    def test_invalid_encoding(self) -> None:
        handle = tempfile.NamedTemporaryFile(mode="wb", suffix=".csv", delete=False)
        handle.write(b"\xff\xfe\x00\x00")
        handle.close()
        source = Path(handle.name)
        try:
            with self.assertRaises(LabError) as context:
                load_experiments(str(source))
            self.assertIn("UTF-8", str(context.exception))
        finally:
            source.unlink()

    def test_empty_file(self) -> None:
        source = write_temp("")
        try:
            with self.assertRaises(LabError) as context:
                load_experiments(str(source))
            self.assertIn("CSV 为空", str(context.exception))
        finally:
            source.unlink()


class ModelTests(unittest.TestCase):
    def test_empty_steps_rejected(self) -> None:
        with self.assertRaises(LabError):
            Experiment(name="A", purpose="B", equipment=(), steps=())

    def test_empty_name_rejected(self) -> None:
        with self.assertRaises(LabError):
            Experiment(name="  ", purpose="B", equipment=(), steps=("一步",))


if __name__ == "__main__":  # pragma: no cover
    unittest.main()

"""测试记录单 HTML 输出。"""

from __future__ import annotations

import unittest

from labbook.model import Experiment, LabError
from labbook.render import render_page

EXPERIMENTS = (
    Experiment(
        name="探究凸透镜成像规律",
        purpose="观察物距变化时像的变化",
        equipment=("凸透镜", "光屏"),
        steps=("组装光具座", "移动光屏找清晰的像"),
        safety="注意用火安全",
    ),
    Experiment(
        name="测量物体质量",
        purpose="学会使用托盘天平",
        equipment=("托盘天平",),
        steps=("调节平衡螺母", "加砝码并读数"),
    ),
)


class RenderTests(unittest.TestCase):
    def test_renders_each_experiment(self) -> None:
        page = render_page(EXPERIMENTS)
        self.assertEqual(page.count('class="sheet"'), 2)
        self.assertIn("实验 01", page)
        self.assertIn("实验 02", page)
        self.assertIn("探究凸透镜成像规律", page)

    def test_steps_and_equipment(self) -> None:
        page = render_page(EXPERIMENTS)
        self.assertIn("组装光具座", page)
        self.assertIn('class="chip">凸透镜', page)

    def test_safety_only_when_present(self) -> None:
        page = render_page(EXPERIMENTS)
        self.assertEqual(page.count('class="safety"'), 1)

    def test_rows_configured(self) -> None:
        page = render_page(EXPERIMENTS, rows=6)
        # 每个实验 6 行，两个实验共 12 行
        self.assertEqual(page.count('class="line"'), 12)

    def test_conclusion_lines(self) -> None:
        page = render_page(EXPERIMENTS, conclusion_lines=3)
        self.assertEqual(page.count('<div class="lines"><div></div><div></div><div></div>'), 2)

    def test_two_columns(self) -> None:
        page = render_page(EXPERIMENTS, columns=2)
        self.assertIn("--cols: 2", page)

    def test_title_is_escaped(self) -> None:
        page = render_page(EXPERIMENTS, title="<b>记录单</b>")
        self.assertNotIn("<b>记录单</b>", page)
        self.assertIn("&lt;b&gt;", page)

    def test_invalid_parameters(self) -> None:
        invalid_calls = [
            {"rows": 0},
            {"rows": 13},
            {"columns": 3},
            {"conclusion_lines": 0},
            {"title": "  "},
        ]
        for arguments in invalid_calls:
            with self.subTest(arguments=arguments):
                with self.assertRaises(LabError):
                    render_page(EXPERIMENTS, **arguments)

    def test_empty_experiments(self) -> None:
        with self.assertRaises(LabError):
            render_page([])

    def test_count_in_footer(self) -> None:
        self.assertIn("共 2 个实验", render_page(EXPERIMENTS))


if __name__ == "__main__":  # pragma: no cover
    unittest.main()

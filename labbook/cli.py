"""命令行入口：把实验清单 CSV 转成可打印的实验记录单。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional, Sequence

from .loader import load_experiments
from .model import LabError
from .render import render_page


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="labbook",
        description="实验记录单生成器：读实验清单 CSV，输出可打印的 A4 记录单",
    )
    parser.add_argument("--version", action="version", version="labbook 0.1.0")
    parser.add_argument("-i", "--input", required=True, help="实验清单 CSV 路径")
    parser.add_argument(
        "-o", "--output", default="实验记录单.html", help="输出 HTML 路径"
    )
    parser.add_argument("--title", default="实验记录单", help="记录单标题")
    parser.add_argument(
        "--rows", type=int, default=4, help="观察记录表的行数，1~12，默认 4"
    )
    parser.add_argument(
        "--columns", type=int, default=1, help="每行排几个实验，1 或 2，默认 1"
    )
    parser.add_argument(
        "--conclusion-lines", type=int, default=2, help="实验结论的书写行数，默认 2"
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        experiments = load_experiments(args.input)
        meta = "共 %d 个实验 · 表头：名称 / 目的 / 器材 / 步骤 / 安全（可选）" % len(
            experiments
        )
        page = render_page(
            experiments,
            title=args.title,
            rows=args.rows,
            columns=args.columns,
            meta=meta,
            conclusion_lines=args.conclusion_lines,
        )
    except LabError as exc:
        print("错误: %s" % exc, file=sys.stderr)
        return 2

    try:
        Path(args.output).write_text(page, encoding="utf-8")
    except OSError as exc:
        print("错误: 写入文件失败: %s" % exc, file=sys.stderr)
        return 1

    print("已生成 %s：%d 个实验" % (args.output, len(experiments)))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

"""读取实验清单 CSV。

约定表头：``名称, 目的, 器材, 步骤``，可选 ``安全``。
器材用 ``;`` 或 ``、`` 分隔，步骤用 ``|`` 或换行分隔。
"""

from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

from .model import Experiment, LabError

REQUIRED_COLUMNS = ("名称", "目的", "器材", "步骤")
OPTIONAL_COLUMNS = ("安全",)

EQUIPMENT_SEPARATORS = re.compile(r"[;；、]")
STEP_SEPARATORS = re.compile(r"[|｜\n]")


def _split_equipment(value: str) -> Tuple[str, ...]:
    parts = [item.strip() for item in EQUIPMENT_SEPARATORS.split(value)]
    return tuple(item for item in parts if item)


def _split_steps(value: str) -> Tuple[str, ...]:
    parts = [item.strip() for item in STEP_SEPARATORS.split(value)]
    return tuple(item for item in parts if item)


def load_experiments(path: str) -> List[Experiment]:
    """读取并校验 CSV，返回实验列表。

    :raises LabError: 文件不存在、编码错误、表头缺失或单元格为空。
    """
    source = Path(path)
    if not source.exists():
        raise LabError("文件不存在: %s" % path)
    if source.is_dir():
        raise LabError("这是一个目录，需要 CSV 文件: %s" % path)

    try:
        text = source.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError:
        raise LabError("无法以 UTF-8 读取 %s，请另存为 UTF-8 编码" % path) from None
    except OSError as exc:
        raise LabError("读取文件失败: %s" % exc) from exc

    reader = csv.DictReader(text.splitlines())
    fieldnames = [name.strip() for name in (reader.fieldnames or [])]
    if not fieldnames:
        raise LabError("CSV 为空，第一行应为表头：%s" % ", ".join(REQUIRED_COLUMNS))

    missing = [name for name in REQUIRED_COLUMNS if name not in fieldnames]
    if missing:
        raise LabError(
            "缺少必需的列: %s（当前表头: %s）"
            % ("、".join(missing), "、".join(fieldnames))
        )

    experiments: List[Experiment] = []
    for row in reader:
        clean: Dict[str, str] = {}
        for key, value in row.items():
            if key is None or value is None:
                continue
            clean[key.strip()] = value.strip()

        if not any(clean.get(name, "") for name in REQUIRED_COLUMNS):
            continue  # 跳过空行

        line = reader.line_num
        name = clean.get("名称", "")
        if not name:
            raise LabError("第 %d 行缺少实验名称" % line)
        purpose = clean.get("目的", "")
        if not purpose:
            raise LabError("第 %d 行《%s》缺少实验目的" % (line, name))
        steps = _split_steps(clean.get("步骤", ""))
        if not steps:
            raise LabError("第 %d 行《%s》缺少实验步骤" % (line, name))

        experiments.append(
            Experiment(
                name=name,
                purpose=purpose,
                equipment=_split_equipment(clean.get("器材", "")),
                steps=steps,
                safety=clean.get("安全", ""),
            )
        )

    if not experiments:
        raise LabError("没有读取到任何实验，请检查 CSV 内容")
    return experiments


def describe_columns(columns: Sequence[str]) -> str:
    """把列名拼成便于阅读的中文提示。"""
    return "、".join(columns)

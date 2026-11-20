"""实验记录单的数据结构与异常定义。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple


class LabError(ValueError):
    """实验清单格式错误或参数不合法。"""


@dataclass(frozen=True)
class Experiment:
    """一个实验的基本信息。

    ``equipment`` 与 ``steps`` 在加载阶段已经拆分好，渲染时直接使用。
    """

    name: str
    purpose: str
    equipment: Tuple[str, ...]
    steps: Tuple[str, ...]
    safety: str = ""

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise LabError("实验名称不能为空")
        if not self.purpose.strip():
            raise LabError("实验目的不能为空")
        if not self.steps:
            raise LabError("实验步骤不能为空")

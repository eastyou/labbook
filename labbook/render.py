"""把实验清单渲染成一页可打印的 A4 实验记录单。"""

from __future__ import annotations

import html
from typing import List, Sequence

from .model import Experiment, LabError

PAGE_TEMPLATE = """<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__</title>
<style>
  :root { color-scheme: light; }
  * { box-sizing: border-box; }
  body {
    margin: 0;
    padding: 18px 22px 24px;
    background: #f8fafc;
    color: #0f172a;
    font-family: "PingFang SC", "Microsoft YaHei", "Noto Sans CJK SC", sans-serif;
  }
  header {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    gap: 16px;
    border-bottom: 2px solid #0f172a;
    padding-bottom: 10px;
    margin-bottom: 14px;
  }
  h1 { font-size: 21px; margin: 0; letter-spacing: 1px; }
  .meta { color: #64748b; font-size: 12px; margin-top: 4px; }
  .fields {
    display: flex;
    gap: 16px;
    color: #334155;
    font-size: 12px;
    white-space: nowrap;
  }
  .fields span { border-bottom: 1px solid #94a3b8; padding: 0 18px 2px 4px; }
  .sheets {
    display: grid;
    grid-template-columns: repeat(var(--cols), minmax(0, 1fr));
    gap: 14px;
  }
  .sheet {
    background: #fff;
    border: 1px solid #cbd5e1;
    border-radius: 10px;
    padding: 12px 14px 14px;
    break-inside: avoid;
  }
  .sheet-head {
    display: flex;
    align-items: baseline;
    gap: 10px;
    border-bottom: 1px dashed #cbd5e1;
    padding-bottom: 8px;
    margin-bottom: 10px;
  }
  .sheet-head .index {
    font-size: 11px;
    color: #0369a1;
    background: #e0f2fe;
    border-radius: 999px;
    padding: 2px 9px;
    white-space: nowrap;
  }
  .sheet-head h2 { font-size: 16px; margin: 0; }
  .block { margin-bottom: 9px; font-size: 12px; line-height: 1.6; }
  .block > b {
    display: block;
    font-size: 11px;
    color: #0369a1;
    letter-spacing: 0.5px;
    margin-bottom: 2px;
  }
  .block p { margin: 0; color: #1e293b; }
  .chips { display: flex; flex-wrap: wrap; gap: 5px; }
  .chip {
    border: 1px solid #e2e8f0;
    background: #f8fafc;
    border-radius: 6px;
    padding: 1px 7px;
    font-size: 11px;
    color: #334155;
  }
  ol.steps { margin: 0; padding-left: 18px; color: #1e293b; }
  ol.steps li { margin-bottom: 2px; }
  .safety {
    border: 1px solid #fed7aa;
    background: #fff7ed;
    color: #9a3412;
    border-radius: 7px;
    padding: 6px 9px;
    font-size: 11px;
    line-height: 1.55;
    margin-bottom: 9px;
  }
  .table-title {
    font-size: 11px;
    color: #0369a1;
    letter-spacing: 0.5px;
    margin-bottom: 4px;
  }
  table { width: 100%; border-collapse: collapse; font-size: 11px; }
  th, td { border: 1px solid #cbd5e1; padding: 5px 7px; }
  th { background: #f1f5f9; color: #475569; font-weight: 600; text-align: left; }
  td.line { height: 22px; }
  .conclusion { margin-top: 9px; }
  .conclusion .lines { margin-top: 4px; }
  .conclusion .lines div {
    border-bottom: 1px solid #cbd5e1;
    height: 22px;
  }
  footer {
    margin-top: 14px;
    color: #94a3b8;
    font-size: 11px;
    display: flex;
    justify-content: space-between;
  }
  @page { size: A4 portrait; margin: 10mm; }
  @media print {
    body { background: #fff; padding: 0; }
    .sheet { border-color: #94a3b8; border-radius: 0; }
    * { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  }
</style>
</head>
<body>
<header>
  <div>
    <h1>__TITLE__</h1>
    <div class="meta">__META__</div>
  </div>
  <div class="fields">
    <div>班级<span>&nbsp;</span></div>
    <div>姓名<span>&nbsp;</span></div>
    <div>日期<span>&nbsp;</span></div>
  </div>
</header>
<div class="sheets" style="--cols: __COLS__">
__SHEETS__
</div>
<footer>
  <span>labbook · 共 __COUNT__ 个实验</span>
  <span>A4 纵向打印，建议缩放 100%</span>
</footer>
</body>
</html>
"""

SHEET_TEMPLATE = """<article class="sheet">
  <div class="sheet-head">
    <span class="index">实验 __INDEX__</span>
    <h2>__NAME__</h2>
  </div>
  <div class="block"><b>实验目的</b><p>__PURPOSE__</p></div>
  __EQUIPMENT__
  <div class="block"><b>实验步骤</b><ol class="steps">__STEPS__</ol></div>
  __SAFETY__
  <div class="table-title">观察与记录</div>
  <table>
    <thead><tr><th style="width:26%">记录次数</th><th>观察到的现象 / 数据</th></tr></thead>
    <tbody>__ROWS__</tbody>
  </table>
  <div class="conclusion">
    <div class="table-title">实验结论</div>
    <div class="lines">__LINES__</div>
  </div>
</article>"""


def _render_equipment(equipment: Sequence[str]) -> str:
    if not equipment:
        return ""
    chips = "".join(
        '<span class="chip">%s</span>' % html.escape(item) for item in equipment
    )
    return '<div class="block"><b>实验器材</b><div class="chips">%s</div></div>' % chips


def _render_sheet(
    index: int, experiment: Experiment, rows: int, conclusion_lines: int
) -> str:
    steps = "".join("<li>%s</li>" % html.escape(step) for step in experiment.steps)
    record_rows = "".join(
        '<tr><td>%d</td><td class="line"></td></tr>' % number
        for number in range(1, rows + 1)
    )
    conclusion = "".join("<div></div>" for _ in range(conclusion_lines))
    safety = ""
    if experiment.safety:
        safety = '<div class="safety">安全提示：%s</div>' % html.escape(
            experiment.safety
        )

    sheet = SHEET_TEMPLATE
    replacements = {
        "__INDEX__": "%02d" % index,
        "__NAME__": html.escape(experiment.name),
        "__PURPOSE__": html.escape(experiment.purpose),
        "__EQUIPMENT__": _render_equipment(experiment.equipment),
        "__STEPS__": steps,
        "__SAFETY__": safety,
        "__ROWS__": record_rows,
        "__LINES__": conclusion,
    }
    for key, value in replacements.items():
        sheet = sheet.replace(key, value)
    return sheet


def render_page(
    experiments: Sequence[Experiment],
    title: str = "实验记录单",
    rows: int = 4,
    columns: int = 1,
    meta: str = "",
    conclusion_lines: int = 2,
) -> str:
    """生成整页 HTML；参数越界或实验为空时抛出 ``LabError``。"""
    if not title.strip():
        raise LabError("标题不能为空")
    if not experiments:
        raise LabError("至少需要一个实验才能生成记录单")
    if not 1 <= rows <= 12:
        raise LabError("记录行数必须在 1 到 12 之间")
    if not 1 <= columns <= 2:
        raise LabError("列数只能是 1 或 2")
    if not 1 <= conclusion_lines <= 4:
        raise LabError("结论行数必须在 1 到 4 之间")

    sheets: List[str] = [
        _render_sheet(index, experiment, rows, conclusion_lines)
        for index, experiment in enumerate(experiments, start=1)
    ]

    page = PAGE_TEMPLATE
    replacements = {
        "__TITLE__": html.escape(title.strip()),
        "__META__": html.escape(meta.strip()),
        "__COLS__": str(columns),
        "__SHEETS__": "\n".join(sheets),
        "__COUNT__": str(len(experiments)),
    }
    for key, value in replacements.items():
        page = page.replace(key, value)
    return page

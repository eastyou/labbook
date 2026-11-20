# labbook

[![CI](https://github.com/eastyou/labbook/actions/workflows/ci.yml/badge.svg)](https://github.com/eastyou/labbook/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9%2B-brightgreen.svg)](pyproject.toml)

给理科老师用的实验记录单生成器：用 Excel 维护一份实验清单，一条命令生成可打印的 A4 记录单，每个实验都有目的、器材、步骤、安全提示和手写记录区。**零依赖，不联网，单文件 HTML。**

不用再为每节实验课复制粘贴 Word 模板，也不用担心安全提示漏写。

## 特性

- **一份 CSV 管所有实验**：名称、目的、器材、步骤、安全提示
- **自动排版**：每个实验一张卡片，包含编号、器材标签、带序号的步骤
- **手写记录区**：观察记录表行数可调，实验结论预留书写横线
- **安全提示醒目**：有内容才显示橙色提示条，没有就自动隐藏
- **单页或双栏**：实验少时一页一个，实验多时可排成两栏
- **中文报错**：表头缺失、名称为空、步骤为空都会指出具体行号
- **28 个单元测试**：覆盖 CSV 解析、BOM、分隔符、HTML 输出与命令行

## 安装

```bash
pip install labbook
```

也可以下载源码后直接运行：

```bash
python -m labbook --help
```

## CSV 格式

第一行是表头，必须包含 `名称`、`目的`、`器材`、`步骤`，可选 `安全`：

| 名称 | 目的 | 器材 | 步骤 | 安全 |
| --- | --- | --- | --- | --- |
| 探究凸透镜成像规律 | 观察物距变化时像的变化 | 凸透镜; 光具座; 光屏 | 固定蜡烛和凸透镜\|移动光屏找到清晰的像 | 注意用火安全 |

- 器材用 `;`、`；` 或 `、` 分隔
- 步骤用 `|`、`｜` 或单元格内换行分隔
- 文件需保存为 UTF-8 编码（带不带 BOM 都可以）

仓库里的 [examples/experiments.csv](examples/experiments.csv) 包含 4 个初中物理、化学、生物实验，可以直接改。

## 用法

用示例文件生成记录单：

```bash
labbook -i examples/experiments.csv -o 实验记录单.html
```

每个实验留 6 行观察记录，标题改成班级名称：

```bash
labbook -i 实验清单.csv -o 记录单.html --rows 6 --title "初二(3)班物理实验记录"
```

实验较多时排成两栏，便于在一页内放下更多内容：

```bash
labbook -i 实验清单.csv -o 记录单.html --columns 2 --conclusion-lines 1
```

## 参数

| 参数 | 默认值 | 说明 |
| --- | --- | --- |
| `-i, --input` | 必填 | 实验清单 CSV 路径 |
| `-o, --output` | `实验记录单.html` | 输出 HTML 路径 |
| `--title` | `实验记录单` | 页面标题 |
| `--rows` | `4` | 观察记录表行数，1~12 |
| `--columns` | `1` | 每行排几个实验，1 或 2 |
| `--conclusion-lines` | `2` | 实验结论书写行数，1~4 |

## 打印

浏览器打开生成的 HTML，按 `Ctrl/Cmd + P`：

- 纸张：A4 纵向
- 缩放：100%
- 勾选「背景图形」，卡片边框和标签底色才会显示

每张实验卡片都设置了 `break-inside: avoid`，不会从中间被切到两页。

## 开发

```bash
python -m unittest discover -s tests -v
```

## License

[MIT](LICENSE) © 2026 eastyou

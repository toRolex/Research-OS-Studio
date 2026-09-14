# 幻灯片模板：Beamer 与可编辑 PPTX

用于单一 `paper-talk` 入口的按需参考，不是第二个 skill、通用运行器或内容推断接口。改编自 Orchestra Research 的 `presenting-conference-talks` / `references/slide-templates.md`（MIT）；沿用主交付中的上游来源与许可记录。

## 使用契约：先确认 Markdown，再实例化

1. 先在演讲 Markdown 中确认：论文版本、受众、talk type、净演讲时间与 Q&A、逐页论点、证据位置、图源、讲稿和备份页。页码按 **logical slide** 编号；每页记录预计秒数和下一页转场。完成条件：大纲获确认，未决事实单列。
2. 主执行者按大纲逐页填充以下模板；大纲需要多少页，就显式实例化多少页。模板标题只是位置提示，不是论文结论，不从标题自动生成正文。增删、合并页面须回写 Markdown。完成条件：Markdown 与导出源每页一一对应。
3. 所有 `UNFILLED`、`待填`、示例路径及示例页标题都属于 **模板未填，不可交付**；只有从论文或用户确认资料核实后才能替换。未知 chair 不写；作者、单位、venue 不猜。论文/代码 URL 未知则明确在 Markdown 报告并省略相应链接及二维码；二维码只编码已核实地址。完成条件：正文、图注、notes 中无未填标记，缺项均有处理结论。
4. 仅使用现有工具。依赖、字体、主题、图文件或转换工具缺失时，停止相应导出并报告；Markdown 草稿仍可交付为草稿。没有图不画虚构曲线、没有数据不填假结果。完成条件：区分源已生成、导出已完成、内容已验收三种状态。

### 类型、页数与时间

以下保留上游建议范围，不是会场官方规则。会场时长优先；范围外需在 Markdown 记录并确认理由，而不是补空页凑数。主讲页含标题与结尾，不含 appendix、Q&A 备份，也不把 overlay 算作新论点。

| 类型 | 参考时长 | 主讲 logical slides | 内容深度 | 常见单页时间 |
|---|---|---|---|---|
| poster-talk | 3–5 分钟 | 5–8 | 问题、洞见、概览、主结果、takeaway | 30–60 秒 |
| spotlight | 5–8 分钟 | 8–12 | 问题、动机、方法亮点、实验、结论 | 30–45 秒 |
| oral | 15–20 分钟 | 15–22 | 完整论证、设计取舍、实验重点 | 45–90 秒 |
| invited | 30–45 分钟 | 25–40 | 加背景、历史、多个 walkthrough/demo、深入分析 | 60–120 秒 |

单页时间与页数不可机械相乘后冒充总时长：逐页排练求和，给现场切换留余量，Q&A 单独预算。短讲可采用上游的 6 页 poster / 12 页 spotlight 结构；oral 下列模板保留完整各部分；invited 显式增加真实背景、分析与备份，不复制标题充页。

## Beamer Template：完整口头演讲（16:9）

保留上游的 theme、配色、元数据、notes、outline、problem、motivation、insight、architecture、design overlay、setup、results、ablation、systems demo、summary、thank-you 与 appendix；补齐上游 SKILL 的 oral 页位。以下是**完整模板，不是可直接交付的演讲**。所有 `\U{...}` 都显式显示为未填；`\MissingFigure` 缺图时显示红色占位。编译出 PDF 仍不能越过验收。

使用现有 LaTeX 工具链与已安装包；此处英文模板标记保证基础字体可见，填中文时须沿用已经验证的中文排版方案，不在本参考里配置研究环境。配色只是审美建议，并非官方会场视觉规范。

```latex
\documentclass[aspectratio=169,12pt]{beamer}

% 主题与表格、图像、标注；依赖缺失时报告，保持源文件可审阅。
\usetheme{metropolis}
\metroset{sectionpage=none} % 避免隐式章节封面改变 logical slide 计数
\usepackage{appendixnumberbeamer}
\usepackage{booktabs}
\usepackage{graphicx}
\usepackage{xcolor}
\usepackage{tikz}
\usepackage{pgfpages}
\definecolor{primary}{HTML}{003366}
\definecolor{accent}{HTML}{CC0000}
\setbeamercolor{frametitle}{bg=primary,fg=white}
\setbeamercolor{progress bar}{fg=accent}

% 所有 U 参数均为模板位置说明，不能当作已核实内容。
\newcommand{\U}[1]{\textcolor{red}{\textbf{UNFILLED: #1}}}
\newcommand{\MissingFigure}[2]{%
  \IfFileExists{#1}{%
    \includegraphics[width=\linewidth,height=.51\textheight,keepaspectratio]{#1}%
  }{%
    \PackageWarning{paper-talk}{Missing required figure: #1}%
    \fbox{\parbox{.88\linewidth}{\U{missing asset: \detokenize{#1}}}}%
  }\\[-.2em]
  {\scriptsize #2}% 图注要有论文图号/页码、指标单位、条件与改绘说明
}
\newcommand{\TalkNote}[5]{%
  \note{Timing: #1. Key point: #2. Evidence: #3.
  Action / boundary: #4. Transition: #5.}%
}

\title{\U{verified paper title}}
\subtitle{\U{verified venue and year}}
\author{\U{verified author list}}
\institute{\U{verified affiliations}}
\date{}
\graphicspath{{figures/}}

% 听众版隐藏 notes；演讲者版替换为下一行，勿同时启用。
\setbeameroption{hide notes}
% \setbeameroption{show notes on second screen=right}
% 输出演讲者版时使用不同文件名，勿混入会场听众文件。

\begin{document}

% 01 标题：不依赖隐式 maketitle，确保标题页也有 notes。
\begin{frame}[plain]
  \titlepage
  \TalkNote{\U{seconds}}{\U{opening thesis and presenter identity}}
    {\U{paper version}}{\U{pronunciation; chair only if verified}}
    {\U{transition to roadmap}}
\end{frame}

% 02 路线图，可在确认大纲时省略。
\begin{frame}{\U{Outline}}
  \tableofcontents
  \TalkNote{\U{seconds}}{\U{problem to evidence to conclusion}}
    {\U{scope of this talk}}{\U{what the audience should remember}}
    {\U{transition to context}}
\end{frame}

\section{Problem}
% 03 问题背景。
\begin{frame}{\U{Problem Context}}
  \begin{itemize}
    \item \U{domain importance with sourced numbers}
    \item \U{scale and impact}
    \item \U{why the audience should care}
  \end{itemize}
  \TalkNote{\U{seconds}}{\U{one concrete motivating example}}
    {\U{source for context numbers}}{\U{boundary of the example}}
    {\U{transition to precise problem}}
\end{frame}

% 04 明确挑战，不只展示领域背景。
\begin{frame}{\U{Problem Statement}}
  \begin{block}{\U{Research question}}
    \U{input, desired outcome, constraints and scope}
  \end{block}
  \U{one running example used again in the architecture walkthrough}
  \TalkNote{\U{seconds}}{\U{state the problem in one sentence}}
    {\U{paper section and formal definition}}{\U{excluded cases}}
    {\U{transition to existing limitations}}
\end{frame}

% 05 证据支持的差距；不把“现有工作都不能”当作默认事实。
\begin{frame}{\U{Motivation: Gaps in Existing Systems}}
  \begin{columns}[T]
    \begin{column}{.46\textwidth}
      \textbf{\U{Gap 1}}: \U{claim and citation}\\[.5em]
      \textbf{\U{Gap 2}}: \U{claim and citation}\\[.5em]
      \textbf{\U{Gap 3}}: \U{claim and citation}
    \end{column}
    \begin{column}{.50\textwidth}
      \MissingFigure{figures/UNFILLED-motivation.pdf}{\U{caption and provenance}}
    \end{column}
  \end{columns}
  \TalkNote{\U{seconds}}{\U{walk through supported gaps}}
    {\U{point to limitation in figure}}{\U{avoid overgeneralizing prior work}}
    {\U{transition to insight}}
\end{frame}

\section{Our Approach}
% 06 核心洞见。
\begin{frame}{\U{Key Insight}}
  \begin{center}
    \Large\textbf{\U{system or method improves Y under Z}}
  \end{center}
  \begin{itemize}
    \item \U{one-line explanation}
    \item \U{why this enables a better design, with scope}
  \end{itemize}
  \TalkNote{\U{seconds}}{\U{memorable thesis sentence}}
    {\U{paper support}}{\U{pause; distinguish insight from result}}
    {\U{transition to architecture}}
\end{frame}

% 07 架构：沿一个真实请求走完数据流。
\begin{frame}{\U{System Architecture}}
  \centering
  \MissingFigure{figures/UNFILLED-architecture.pdf}{\U{components, arrows, source and adaptations}}
  \TalkNote{\U{seconds}}{\U{concrete request end to end}}
    {\U{paper architecture figure}}{\U{highlight novel components and data flow}}
    {\U{transition to component A}}
\end{frame}

% 08 一个 logical slide，三个 overlay；各次 reveal 的动作也写进 notes。
\begin{frame}{\U{Design: Component A}}
  \begin{itemize}
    \item<1-> \U{component responsibility}
    \item<2-> \U{choice X and evidence-based reason}
    \item<3-> \U{alternative Y and trade-off}
  \end{itemize}
  \only<3>{\begin{block}{\U{Key Trade-off}}
    \U{property sacrificed, property gained, and acceptable conditions}
  \end{block}}
  \TalkNote{\U{total seconds across all three overlays}}
    {\U{why the central mechanism works}}{\U{paper design section}}
    {\U{overlay 1 responsibility; 2 choice; 3 trade-off}}
    {\U{transition to component B}}
\end{frame}

% 09 / 10 进一步设计；不适用时由已确认大纲删去。
\begin{frame}{\U{Design: Component B}}
  \U{mechanism, input/output and one concrete walkthrough}
  \TalkNote{\U{seconds}}{\U{design point B}}{\U{paper support}}
    {\U{boundary and failure cases}}{\U{transition to component C}}
\end{frame}
\begin{frame}{\U{Design: Component C}}
  \U{mechanism, interaction with A/B and one concrete walkthrough}
  \TalkNote{\U{seconds}}{\U{design point C}}{\U{paper support}}
    {\U{boundary and failure cases}}{\U{transition to alternatives}}
\end{frame}

% 11 设计替代方案。
\begin{frame}{\U{Design Alternatives}}
  \begin{tabular}{lll}
    \toprule
    \U{choice} & \U{benefit} & \U{cost / condition}\\
    \midrule
    \U{selected design} & \U{evidence} & \U{trade-off}\\
    \U{alternative} & \U{evidence} & \U{trade-off}\\
    \bottomrule
  \end{tabular}
  \TalkNote{\U{seconds}}{\U{why this choice for this workload}}
    {\U{comparison source}}{\U{when the alternative is preferable}}
    {\U{transition to implementation}}
\end{frame}

% 12 工程实现。
\begin{frame}{\U{Implementation}}
  \begin{itemize}
    \item \U{engineering highlights actually described in paper}
    \item \U{implementation boundary, overhead and availability}
  \end{itemize}
  \TalkNote{\U{seconds}}{\U{implementation lesson}}{\U{paper section}}
    {\U{separate prototype from production claims}}{\U{transition to evaluation}}
\end{frame}

\section{Evaluation}
% 13 实验设置。
\begin{frame}{\U{Evaluation Setup}}
  \begin{columns}[T]
    \begin{column}{.48\textwidth}
      \textbf{\U{Testbed and workload}}
      \begin{itemize}
        \item \U{hardware, model and resource counts}
        \item \U{network, workload, dataset and repetitions}
      \end{itemize}
    \end{column}
    \begin{column}{.48\textwidth}
      \textbf{\U{Baselines and metrics}}
      \begin{itemize}
        \item \U{baseline A and citation}
        \item \U{baseline B and citation}
        \item \U{units, uncertainty and direction of improvement}
      \end{itemize}
    \end{column}
  \end{columns}
  \TalkNote{\U{seconds}}{\U{fair comparison conditions}}
    {\U{paper setup section}}{\U{scope and comparability limitations}}
    {\U{transition to headline result}}
\end{frame}

% 14 先结论，再证据；未核实的数字只能留在未填标记里。
\begin{frame}{\U{Main Results}}
  \textbf{\U{verified headline, baseline and measurement conditions}}
  \begin{center}
    \MissingFigure{figures/UNFILLED-eval-main.pdf}{\U{metric, units, sample conditions, uncertainty and paper figure}}
  \end{center}
  \TalkNote{\U{seconds}}{\U{conclusion before pointing at plot}}
    {\U{specific bars/lines; best and typical cases}}
    {\U{exceptions, variance and non-causal comparisons}}
    {\U{transition to breakdown}}
\end{frame}

% 15 分工作负载分析。
\begin{frame}{\U{Result Deep Dive}}
  \MissingFigure{figures/UNFILLED-eval-breakdown.pdf}{\U{per-workload breakdown and provenance}}
  \TalkNote{\U{seconds}}{\U{where gains come from}}
    {\U{specific workloads}}{\U{where gains disappear}}
    {\U{transition to ablation}}
\end{frame}

% 16 消融：不能把贡献默认视为可加百分比。
\begin{frame}{\U{Ablation Study}}
  \MissingFigure{figures/UNFILLED-eval-ablation.pdf}{\U{ablated variants, controls and figure source}}
  \begin{itemize}
    \item \U{component A effect under stated controls}
    \item \U{component B effect and interactions}
  \end{itemize}
  \TalkNote{\U{seconds}}{\U{which design decisions matter}}
    {\U{ablation values and uncertainty}}{\U{interaction effects and causal limits}}
    {\U{transition to scaling}}
\end{frame}

% 17 扩展性。
\begin{frame}{\U{Scalability}}
  \MissingFigure{figures/UNFILLED-eval-scale.pdf}{\U{scale axis, saturation point and source}}
  \TalkNote{\U{seconds}}{\U{observed scaling behavior}}
    {\U{measured range}}{\U{no extrapolation beyond tested scale}}
    {\U{transition to demo or related work}}
\end{frame}

\section{Demo}
% 18 系统演讲：本地录像备份必须已验证，不放虚构地址。
\begin{frame}{\U{Live Demo}}
  \MissingFigure{figures/UNFILLED-demo-screenshot.png}{\U{realistic workload, capture context and source}}
  {\small\U{verified local backup recording path and fallback screenshot sequence}}
  \TalkNote{\U{seconds including switching}}
    {\U{demonstrate one concrete system behavior}}
    {\U{verified load and expected visible outcome}}
    {\U{rehearsed steps; failure trigger; local recording path; start time; static fallback}}
    {\U{transition after either live or backup path}}
\end{frame}

% 19 相关工作定位。
\begin{frame}{\U{Related Work}}
  \U{brief positioning with accurate citations and scoped distinctions}
  \TalkNote{\U{seconds}}{\U{one positioning point}}{\U{citations}}
    {\U{avoid unsupported priority claims}}{\U{transition to summary}}
\end{frame}

\section{Summary}
% 20 回到论题和贡献。
\begin{frame}{\U{Summary}}
  \begin{enumerate}
    \item \textbf{Problem}: \U{one sentence}
    \item \textbf{Approach}: \U{one sentence}
    \item \textbf{Result}: \U{verified headline with scope}
  \end{enumerate}
  \textbf{Contributions}:
  \begin{itemize}
    \item \U{contribution 1}
    \item \U{contribution 2}
    \item \U{contribution 3, only if supported}
  \end{itemize}
  \TalkNote{\U{seconds}}{\U{restate thesis and contributions}}
    {\U{recap strongest supporting evidence}}{\U{end confidently without new claims}}
    {\U{transition to open questions}}
\end{frame}

% 21 局限与后续工作。
\begin{frame}{\U{Limitations and Future Work}}
  \U{known limitations, open questions and clearly labeled future directions}
  \TalkNote{\U{seconds}}{\U{what remains open}}{\U{paper limitations section}}
    {\U{future work is not a completed result}}{\U{transition to Q and A}}
\end{frame}

% 22 结束页：未知链接省略并报告，不生成示例 URL 或二维码。
\begin{frame}{\U{Thank You / Questions}}
  \begin{center}
    \Large Questions?\\[1em]
    \normalsize\U{verified paper/code links or explicit omission decision}\\[.5em]
    \U{optional QR asset only for a verified destination}
  \end{center}
  \TalkNote{\U{closing seconds; Q and A budget separately}}
    {\U{final takeaway}}{\U{verified resources or omission decision}}
    {\U{leave this slide visible; name relevant backup slide IDs}}
    {\U{invite questions and stop timed talk}}
\end{frame}

% 备份不计入主讲预算；每页也必须有触发问题和 notes。
\appendix
\begin{frame}{\U{Backup: Additional Evaluation}}
  \MissingFigure{figures/UNFILLED-eval-extra.pdf}{\U{extra workloads / scale and source}}
  \TalkNote{\U{optional response seconds}}{\U{answer anticipated evaluation question}}
    {\U{paper evidence}}{\U{trigger question and interpretation boundary}}
    {\U{return to Q and A}}
\end{frame}
\begin{frame}{\U{Backup: Design Details}}
  \U{editable algorithm pseudocode, proof or correctness argument}
  \TalkNote{\U{optional response seconds}}{\U{answer correctness or edge-case question}}
    {\U{paper proof or algorithm location}}{\U{assumptions and failure cases}}
    {\U{return to Q and A}}
\end{frame}
\end{document}
```

### 编译与 overlays / appendix

- 沿用现有工具链编译填好的 `slides.tex`；主题/包缺失、图片缺失警告、越界或编译错误要逐项报告，不自动安装，也不执行清理命令。留存可定位的诊断。
- 该模板原样为 22 个主讲 frame、2 个 appendix frame；其中 Component A 有 3 个 overlay。关闭 notes、无新增隐式 frame 时，预期 **24 个 logical slides / 26 个 PDF pages**。删改后按实际输出重新计数；页数不是验收替代品。
- `\only<3>{...}` 仅在指定 overlay 出现；`\onslide<2->{...}` 可用于保留布局的逐步显现。架构 walkthrough 可分别高亮节点，但每一状态必须来源一致。每个 overlay 的操作提示放在对应 logical slide 的 notes；总时长覆盖所有 reveal。
- `\appendix` 配合 `appendixnumberbeamer` 分离正文与备份的编号逻辑。需要固定结束画面时，演讲者不要自然翻入 appendix；按问题跳转备份。
- 听众版隐藏 notes；双屏演讲者版启用 `pgfpages` 与 `show notes on second screen=right`。另存文件并实际试播。双屏版的物理页面布局不能当作听众版页数。
- handout 通常折叠 overlay，但互斥图层可能重叠；逐页核对，不能以“handout 已编译”证明最终状态正确。

## python-pptx：完整、可编辑的生成骨架

以下脚本**共置于 Markdown，仅作本次演讲的生成示例**。主执行者按已确认大纲编辑 `build_confirmed_outline()` 及局部页面函数；没有统一输入 schema，不自动读论文，不从标题推导正文，不提供动态内容运行时。正文和标题使用原生文本框；图表可复用论文图片，图片内部元素不因此变成可编辑图元。若要求逐元素编辑，应按真实数据建立原生图表/形状，或明确报告仅图像可替换。

默认模板故意阻止导出：先填写 `CONFIRMED_TALK_TYPE`、元数据、页内容、notes、路径；正文与类型匹配后才保存。类型实际参与一致性校验、主讲页数范围、页预算和总时长验证，不再读取后弃用。下面 oral 22 页只展示完整填充位置，短讲须删并重写内容，invited 须显式增加有证据的页。不要绕过校验制造成功。

```python
"""paper-talk 单次生成示例：所有 UNFILLED 均为模板未填，不可交付。"""

import argparse
import math
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.util import Inches, Pt

# 审美建议，不是任何会议的官方视觉规范。
VENUE_COLORS = {
    "OSDI": ("003366", "CC0000"),
    "NSDI": ("003366", "CC0000"),
    "SOSP": ("0071BC", "333333"),
    "ASPLOS": ("0071BC", "333333"),
    "NeurIPS": ("7B2D8E", "F0AD00"),
    "ICML": ("008080", "FF6600"),
    "GENERIC": ("333333", "0066CC"),
}
SLIDE_COUNTS = {
    "poster-talk": (5, 8), "spotlight": (8, 12),
    "oral": (15, 22), "invited": (25, 40),
}
SECONDS_PER_SLIDE = {
    "poster-talk": (30, 60), "spotlight": (30, 45),
    "oral": (45, 90), "invited": (60, 120),
}
CONFIRMED_TALK_TYPE = "UNFILLED: 与已确认 Markdown 大纲一致的类型"
# 仅当用户确认范围外页数时填写原因；未确认保持空字符串。
CONFIRMED_COUNT_EXCEPTION = ""
BASE = Path(__file__).resolve().parent


def U(label):
    return f"UNFILLED: {label}（模板未填，不可交付）"


def require_text(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label}为空；停止导出")
    if "UNFILLED" in value or "待填" in value:
        raise ValueError(f"{label}仍为模板未填，不可交付：{value}")
    return value


def add_text(slide, text, x, y, w, h, *, size=26, color="333333", bold=False):
    require_text(text, "文本框")
    shape = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = shape.text_frame
    tf.word_wrap = True
    tf.text = text
    for paragraph in tf.paragraphs:
        paragraph.font.size = Pt(size)
        paragraph.font.bold = bold
        paragraph.font.color.rgb = RGBColor.from_string(color)
    return shape


def notes(seconds, point, evidence, action, transition):
    # 每页都有时间、核心信息、证据、动作/限制与转场；备份页同样调用。
    if not isinstance(seconds, (int, float)) or not math.isfinite(seconds) or seconds <= 0:
        raise ValueError("逐页时长须为已确认的正数秒数")
    fields = [point, evidence, action, transition]
    for value, label in zip(fields, ["核心信息", "证据", "动作/限制", "转场"]):
        require_text(value, label)
    return seconds, (
        f"[Timing: {seconds:g} 秒]\n核心信息：{point}\n证据：{evidence}\n"
        f"动作/限制：{action}\n转场：{transition}"
    )


def required_asset(relative_path):
    require_text(str(relative_path), "资产路径")
    path = BASE / relative_path
    if not path.is_file() or path.stat().st_size == 0:
        raise FileNotFoundError(f"必要资产缺失或为空：{path}；停止导出，不标成功")
    return path


def add_figure(slide, relative_path, caption, x=.7, y=1.5, w=11.9, h=4.65):
    require_text(caption, "图注")
    path = required_asset(relative_path)
    if path.suffix.lower() not in {".png", ".jpg", ".jpeg"}:
        raise ValueError(f"本示例要求经核对的 PNG/JPEG：{path}")
    # 先按原尺寸载入，再用同一个缩放系数 fit；不强设互不相关的宽高。
    picture = slide.shapes.add_picture(str(path), Inches(x), Inches(y))
    width, height = picture.width, picture.height
    scale = min(Inches(w) / width, Inches(h) / height)
    picture.width = round(width * scale)
    picture.height = round(height * scale)
    picture.left = round(Inches(x) + (Inches(w) - picture.width) / 2)
    picture.top = round(Inches(y) + (Inches(h) - picture.height) / 2)
    add_text(slide, caption, x, y + h + .08, w, .65, size=18)
    return picture


def build_confirmed_outline(prs, blank, colors, title, authors, affiliation, venue):
    """仅为当前演讲编写；按获确认 Markdown 显式增删所有页面。"""
    timings = []
    backup_ids = []

    def page(heading, speaker_notes, *, backup=False):
        require_text(heading, "页标题")
        seconds, note_text = speaker_notes
        require_text(note_text, "speaker notes")
        slide = prs.slides.add_slide(blank)
        # 所有页面都从真实 blank layout 开始，只添加一个自定义标题。
        add_text(slide, heading, .55, .3, 12.2, .85,
                 size=34, color=colors[0], bold=True)
        note_frame = slide.notes_slide.notes_text_frame
        if note_frame is None:
            raise RuntimeError("当前 notes master 无 notes placeholder；停止而非静默丢讲稿")
        note_frame.text = note_text
        index = len(prs.slides)
        if backup:
            backup_ids.append(index)
        else:
            timings.append((index, seconds))
        add_text(slide, f"{'备份' if backup else '主讲'} {index}",
                 11.9, 7.05, .9, .25, size=12, color=colors[1])
        return slide

    def text_page(heading, body, speaker_notes, *, backup=False):
        slide = page(heading, speaker_notes, backup=backup)
        add_text(slide, body, .7, 1.5, 11.9, 5.25)
        return slide

    def figure_page(heading, asset, caption, speaker_notes, *, backup=False):
        slide = page(heading, speaker_notes, backup=backup)
        add_figure(slide, asset, caption)
        return slide

    # 下列 notes 中 30/45 等也只是时间分配示例，须按真实排练逐页确认。
    # 简写 N 仅减少模板重复：每次调用仍显式填写本页的全部讲稿字段。
    N = notes
    slide = page(title, N(30, U("开场论题"), U("论文版本"),
                          U("自我介绍；未知 chair 不写"), U("转入路线图")))
    metadata = "\n".join(value for value in (authors, affiliation, venue) if value)
    if metadata:
        add_text(slide, metadata, .7, 2, 11.9, 3)

    text_page(U("02 Outline"), U("已确认的讲述路线"),
              N(30, U("预告论题"), U("覆盖范围"), U("听众记忆点"), U("转背景")))
    text_page(U("03 Problem Context"), U("领域重要性、规模、来源"),
              N(45, U("具体例子"), U("背景数据来源"), U("例子边界"), U("转问题")))
    text_page(U("04 Problem Statement"), U("输入、目标、约束、具体挑战"),
              N(45, U("一句话问题"), U("论文定义"), U("不覆盖情况"), U("转动机")))

    # 动机保留双栏，图注紧邻图片。
    slide = page(U("05 Motivation: Gaps"),
                 N(45, U("有证据的差距"), U("逐项引文"), U("指图中限制"), U("转洞见")))
    add_text(slide, U("差距 1/2/3 及各自证据"), .7, 1.5, 5.3, 4.65)
    add_figure(slide, "figures/UNFILLED-motivation.png", U("来源与条件"),
               x=6.3, w=6.2, h=4.4)

    text_page(U("06 Key Insight"), U("系统/方法在条件 Z 下改善 Y；原因"),
              N(45, U("论题句"), U("论文支持"), U("停顿强调"), U("转架构")))
    figure_page(U("07 Architecture"), "figures/UNFILLED-architecture.png", U("组件、箭头和图源"),
                N(60, U("请求端到端流动"), U("架构图号"), U("指向创新组件"), U("转 A")))
    text_page(U("08 Component A"), U("职责、设计选择、替代方案、取舍"),
              N(60, U("核心机制"), U("设计章节"), U("静态终态对应 Beamer 三次 reveal"), U("转 B")))
    text_page(U("09 Component B"), U("机制、输入输出、例子"),
              N(60, U("设计点 B"), U("论文证据"), U("边界与失败情况"), U("转 C")))
    text_page(U("10 Component C"), U("机制及组件间相互作用"),
              N(60, U("设计点 C"), U("论文证据"), U("边界与失败情况"), U("转替代方案")))
    text_page(U("11 Design Alternatives"), U("选择、收益、成本、适用条件的逐项比较"),
              N(45, U("为何这样选"), U("比较依据"), U("何时替代方案更好"), U("转实现")))
    text_page(U("12 Implementation"), U("真实工程亮点、开销、实现范围"),
              N(45, U("工程经验"), U("实现章节"), U("原型与生产区别"), U("转实验")))

    # 实验设置保留双栏，但不使用会自动带第二个标题的 title-only layout。
    slide = page(U("13 Evaluation Setup"),
                 N(45, U("公平比较条件"), U("实验章节"), U("可比性限制"), U("转主结果")))
    add_text(slide, U("硬件、网络、工作负载、数据、重复次数"), .7, 1.5, 5.7, 5)
    add_text(slide, U("基线及引用、指标单位、误差、优劣方向"), 6.8, 1.5, 5.7, 5)

    # 结果页标题填真实 takeaway；图注含图号、条件、基线、单位和不确定性。
    figure_page(U("14 Main Results: 已核实的 headline"), "figures/UNFILLED-eval-main.png",
                U("主结果图注和来源"),
                N(75, U("先说结论再展示证据"), U("最佳与典型数值、具体柱线"),
                  U("例外与方差"), U("转分解")))
    figure_page(U("15 Result Deep Dive"), "figures/UNFILLED-eval-breakdown.png", U("按负载分解图注"),
                N(60, U("收益来源"), U("具体负载结果"), U("无收益情况"), U("转消融")))
    figure_page(U("16 Ablation"), "figures/UNFILLED-eval-ablation.png", U("控制变量、变体和来源"),
                N(60, U("设计决策贡献"), U("消融数值"), U("交互作用不可默认相加"), U("转扩展性")))
    figure_page(U("17 Scalability"), "figures/UNFILLED-eval-scale.png", U("规模轴、饱和点、来源"),
                N(60, U("观测到的扩展行为"), U("测试范围"), U("不外推未测试规模"), U("转 demo")))

    # 系统 demo：本地截图和录像均需存在；存在检查不能代替实际回放验收。
    recording = required_asset("media/UNFILLED-demo-backup.mp4")
    figure_page(U("18 Live Demo"), "figures/UNFILLED-demo-screenshot.png", U("真实负载与截图来源"),
                N(90, U("展示具体行为"), U("负载与预期可见结果"),
                  U(f"演示步骤、失败触发、录像 {recording} 起点及静态截图退路"), U("任一路径转相关工作")))
    text_page(U("19 Related Work"), U("准确引用与有边界的定位"),
              N(45, U("核心区别"), U("相关文献"), U("不臆称首次"), U("转总结")))
    text_page(U("20 Summary"), U("问题、方法、已核实结果及贡献 1/2/3"),
              N(45, U("重申论题和贡献"), U("最强证据回顾"), U("不新增结论"), U("转局限")))
    text_page(U("21 Limitations and Future Work"), U("已知限制、开放问题、未来方向"),
              N(45, U("尚未解决的内容"), U("局限章节"), U("未来工作不是完成结果"), U("转问答")))
    text_page(U("22 Thank You / Questions"), U("最后 takeaway；已核实链接或已确认省略决定"),
              N(30, U("最终记忆点"), U("资源核验或省略说明"), U("保持此页，备份页号"), U("邀请提问并停止计时")))
    # 有已核实二维码时，在本页用 add_figure 插入并重新安排布局；未知地址时不生成。

    figure_page(U("Backup: Additional Evaluation"), "figures/UNFILLED-eval-extra.png", U("额外实验来源"),
                N(60, U("回答扩展性或负载问题"), U("对应证据"), U("触发问题与范围"), U("回问答")),
                backup=True)
    text_page(U("Backup: Design Details"), U("可编辑算法、证明或边界情况"),
              N(60, U("回答正确性问题"), U("算法或证明位置"), U("前提与失败情况"), U("回问答")),
              backup=True)
    return timings, backup_ids


def create_presentation(title, authors, affiliation, venue, talk_type, minutes, palette):
    require_text(title, "标题")
    # 未提供或匿名要求省略的元数据保持空，不猜测也不输出虚构占位。
    for value, label in [(authors, "作者"), (affiliation, "单位"), (venue, "会场")]:
        if value:
            require_text(value, label)
    require_text(CONFIRMED_TALK_TYPE, "已确认演讲类型")
    if talk_type != CONFIRMED_TALK_TYPE:
        raise ValueError("请求类型与已确认大纲不一致；先调整并确认大纲，不能仅改 CLI 标签")
    if talk_type not in SLIDE_COUNTS or not math.isfinite(minutes) or minutes <= 0:
        raise ValueError("类型或净演讲时间无效")
    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
    # 日期、页脚、页码占位符不会复制到新页；Blank 布局可保留这些辅助槽位。
    for blank_layout in prs.slide_layouts:
        if any(blank_layout.iter_cloneable_placeholders()):
            continue
        if any(not shape.is_placeholder for shape in blank_layout.shapes):
            continue
        break
    else:
        raise RuntimeError("未找到无内容占位符且无装饰形状的 blank layout；人工检查模板")
    timings, backup_ids = build_confirmed_outline(
        prs, blank_layout, VENUE_COLORS[palette], title, authors, affiliation, venue
    )
    count = len(timings)
    low, high = SLIDE_COUNTS[talk_type]
    if not low <= count <= high:
        require_text(CONFIRMED_COUNT_EXCEPTION, "超出建议页数的已确认理由")
    total_seconds = sum(seconds for _, seconds in timings)
    if total_seconds > minutes * 60:
        raise ValueError(f"主讲计划 {total_seconds:g} 秒超出净预算 {minutes * 60:g} 秒")
    if len(prs.slides) != count + len(backup_ids):
        raise RuntimeError("有页面漏入主讲/备份登记")
    # 保存前再扫所有可见文本和 notes，避免后续手工扩展绕过局部校验。
    for index, slide in enumerate(prs.slides, 1):
        for shape in slide.shapes:
            if shape.has_text_frame:
                require_text(shape.text, f"第 {index} 页文本")
        tf = slide.notes_slide.notes_text_frame
        if tf is None:
            raise RuntimeError(f"第 {index} 页缺 notes placeholder")
        require_text(tf.text, f"第 {index} 页 notes")
    min_seconds, max_seconds = SECONDS_PER_SLIDE[talk_type]
    pacing = [
        f"页 {index}: {seconds:g} 秒"
        for index, seconds in timings
        if not min_seconds <= seconds <= max_seconds
    ]
    return prs, count, backup_ids, total_seconds, pacing


def main():
    parser = argparse.ArgumentParser(description="paper-talk 本次演讲的显式页面生成示例")
    parser.add_argument("--title", required=True)
    parser.add_argument("--authors", default="")  # 仅在已核实且允许展示时填写
    parser.add_argument("--affiliation", default="")
    parser.add_argument("--venue", default="")
    parser.add_argument("--type", dest="talk_type", choices=list(SLIDE_COUNTS), required=True)
    parser.add_argument("--minutes", type=float, required=True, help="不含 Q&A 的净演讲预算")
    parser.add_argument("--palette", choices=list(VENUE_COLORS), default="GENERIC")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.suffix.lower() != ".pptx":
        raise ValueError("输出扩展名须为 .pptx")
    if args.output.exists():
        raise FileExistsError(f"保留既有成果，不覆盖：{args.output}")
    if not args.output.parent.is_dir():
        raise FileNotFoundError("输出目录须由主执行者确认且已存在")
    prs, count, backup_ids, seconds, pacing = create_presentation(
        args.title, args.authors, args.affiliation, args.venue,
        args.talk_type, args.minutes, args.palette
    )
    # 排他创建，避免检查后竞态覆盖其他人的文件；写入失败留下的文件按失败报告。
    with args.output.open("xb") as output:
        prs.save(output)
    print(f"已写出待验收草稿：{args.output}")
    print(f"主讲 logical slides={count}；备份={len(backup_ids)}；PPTX 实体页={len(prs.slides)}")
    print(f"主讲计划={seconds:g} 秒；备份页号={backup_ids}；PPTX 为静态终态，无自动 overlays")
    if pacing:
        print("单页时间偏离类型建议，须排练复核：" + "；".join(pacing))
    print("尚未证明内容真实性、图注可读性、视觉布局或现场 demo 已通过验收。")


if __name__ == "__main__":
    main()
```

### 执行示例

仅在主执行者按大纲填好后，将代码块保存到该演讲已经获准的交付目录。本参考交付本身不创建脚本或任何演讲成品。使用已存在且已有 `python-pptx` 的解释器；不声明 inline 依赖，不追加依赖，不同步环境。缺库直接报告。

下列 shell 变量由主执行者填为**已核实且允许展示的值**；`${变量:?}` 在必需值缺失时停止。作者、单位和会场缺失或要求匿名省略时保持空字符串，并在报告记录省略；Beamer 同样移除对应元数据槽位。`TALK_MINUTES` 是已确认净预算，`TALK_TYPE` 须与填好的大纲一致，`TALK_OUTPUT` 指向不存在的新文件。这里没有示例作者或伪 URL。

```bash
uv run --offline --no-python-downloads --no-project \
  --python "${EXISTING_PYTHON:?指定已有解释器绝对路径}" \
  "${TALK_SCRIPT:?指定已填好脚本绝对路径}" \
  --title "${PAPER_TITLE:?已核实标题}" \
  --authors "${PAPER_AUTHORS-}" \
  --affiliation "${PAPER_AFFILIATION-}" \
  --venue "${TALK_VENUE-}" \
  --type "${TALK_TYPE:?已确认类型}" \
  --minutes "${TALK_MINUTES:?已确认净分钟数}" \
  --output "${TALK_OUTPUT:?新 PPTX 路径}"
```

## Dual Output：同一 Markdown 的两种交付

- **Markdown-first**：逐页内容、证据、notes 和时间的权威版本是已确认 Markdown，不以 PPTX 反推论文内容。任何临场修改回写 Markdown，并同步另一格式。
- **Beamer PDF**：数学与正式排版友好，适合会场播放；保留 `.tex` 供编辑。听众文件、演讲者 notes 文件分开标识。
- **PPTX**：供合作者编辑、套用已提供的会场模板或最后一刻调整。代码默认只产生静态页面；不要承诺自动生成 PowerPoint 动画。需要逐步构建时在 PowerPoint 人工设置并试播，或显式复制状态页并建立 `logical slide → 实体页` 对照。
- **双格式复核**：按 logical ID 对齐标题、论点、证据、图注、notes、来源与主讲/备份边界，不要求两格式视觉逐像素相同。Beamer 三次 reveal 对应 PPTX 一个完整终态时，明确记录该差异；不要为凑相同页数删证据。
- **状态报告**：逐格式写清源生成/编译或保存/视觉验收结果。只生成一份时报告另一份未生成及原因，不把 Markdown 草稿或模板 PDF 称为完成的双格式交付。

## Figure Handling：复用、图注、标注与缺失处理

### 图源与证据

优先复用论文中的架构与最强的 2–3 张实验图；其余放备份。每图记录论文版本、图号/页码、输入资产路径、裁剪/改绘说明和使用范围。实验图的单位、基线、样本条件、误差含义不能裁掉。先讲 takeaway，再指向具体柱/线，同时说明典型、最好与失败情况。箭头或圈注需指向真实数据位置，不遮挡原图。

图注贴近图像；完整来源和解释写入 notes。默认 PPTX 主体 ≥24pt、标题约34pt，图注示例18pt只为紧凑来源行，投影不清就放大或拆页，不缩小到不可读。模板代码不会可靠检测文本溢出、字体替换或图内文字尺寸，必须渲染后人工查看。

### In Beamer

允许在已经确认的论文目录中寻找已有图，但路径必须真实存在。

```latex
% 所有待填标记和示例文件名都必须替换后才可交付。
\graphicspath{{figures/}{../paper/figures/}}
\begin{frame}{\U{verified result headline}}
  \centering
  \includegraphics[width=.90\textwidth,height=.62\textheight,keepaspectratio]
    {UNFILLED-eval-throughput.pdf}
  \par{\scriptsize\U{paper figure/page, metric, units, conditions and adaptations}}
  \TalkNote{\U{seconds}}{\U{takeaway}}{\U{bars/lines and source}}
    {\U{annotation cue and limitation}}{\U{transition}}
\end{frame}
```

单独 `\includegraphics` 对缺图会报错；完整模板的 `\MissingFigure` 则显示醒目未填框并发警告。这两种情况都必须报告为未完成。资产文件存在不等于图内容正确；替换后仍要核查。

### In python-pptx

使用上方 `add_figure()`：载入原尺寸，以同一比例 fit 到目标矩形并居中，图注独立可编辑。不要沿用上游 `slide_layouts[5]` 的“Blank”误注，该布局通常是 Title Only；已有标题加自定义标题会重复。不要同时指定任意宽高导致变形，也不要默默裁掉坐标轴。

如果图是 PDF，仅在本机已有转换工具时，把**已确认图页**转为高分辨率 PNG（上游建议 300 dpi）；核对多页输入的页选择、输出文件实际名称、背景/透明度、细字与颜色，再传入图片路径。这里不提供安装或清理命令；无现成转换能力则报告该 PPTX 图导出受阻，保留 Markdown 资产引用。PDF 不是本示例可直接嵌入的图片格式。

### 系统 demo + backup

演示页保留真实负载截图，notes 列出操作序列、预期屏幕结果、时间预算、切换触发点、本地录像路径/起播位置及静态截图后备。现场失败立即走已排练的备份，不临时猜 URL。文件存在检查后还须实际回放、确认音视频和可见内容；仅有空壳文件不能标“demo 已验证”。不能提供录像时说明 demo 尚未就绪，或请用户确认改成明确标注的静态 walkthrough。

## Speaker notes：覆盖每一页和每一层

每个 logical slide（含标题、outline、总结、结尾、appendix）包含：预计秒数、核心句、证据定位、指图/overlay/demo 动作及限制、下一页转场。讲稿通常3–4句，技术限制可另列提示；不把幻灯片 bullet 原样复制充当 notes。Q&A 备份写触发问题、答复时间、证据边界及返回结束页动作。

保留 Mike Dahlin 的分层方法：整场用路线图→正文→总结；章节先说明目标、展示内容、给小结；单页先 headline→证据→转场。章节提示可以由口述完成，不强制多生章节封面。逐页求和与排练核对，揭示动画只计同一 logical slide 的总时间。

## 验证与完成条件

### 可复核的源级检查

- Beamer 每个 `frame` 都有 `\TalkNote`，默认全模板 24 个 frame；22 正文、2 备份，Component A 三次 reveal。不要把 `\maketitle`、自动 section page 或 notes 页面漏计；本模板显式避免前两者。
- Python 代码块可用标准库 `ast.parse` 做语法检查：用上方相同的 **uv + 现有解释器**运行检查，不执行未填生成器、不安装库。语法通过仅证明代码可解析。
- 原样执行生成器必须因 `CONFIRMED_TALK_TYPE` 未填而失败，且不创建输出。单独调用 `required_asset()` 测试不存在文件须抛 `FileNotFoundError`；`require_text()` 对未填作者/图注/notes 须拒绝。
- 默认模板的 Blank 布局含日期、页脚、页码辅助占位符，仍须能创建无内容占位符的新页；带标题/正文占位符或装饰形状的布局须跳过，无可用布局时明确失败。不能只以布局名称或固定索引判断。
- 填好测试副本后分别验证类型不匹配、超出主讲页数且无确认理由、总时长超预算、既有输出、notes placeholder 缺失都明确失败。保留输出文件被拒绝覆盖。
- 用已安装库重新打开合法生成的 PPTX，核对实体页数、每页 notes、原生文本框和图片长宽比。横图/竖图都须 fit 且不超目标框。类型测试需要不同的真实页面实例化，不是只改参数跑同一 22 页。

### 导出后的验收

逐页查看两个格式：内容与来源、图内字可读、图注完整、无双标题/越界、链接/二维码目的地准确、notes 时间与动作齐全。试播 overlay 与 demo 两条路径。验收报告分别列：主讲 logical slides、备份 logical slides、Beamer 听众 PDF 实际页数、PPTX 实体页数、逐页计划总时长、尚未验证项与导出失败。源未填、缺资产、未渲染或未试播，都不能报告成完整演讲交付。

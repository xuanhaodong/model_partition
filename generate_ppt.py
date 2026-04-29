"""
SynerGist 项目介绍 PPT 自动生成脚本
"""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# ── 主题色 ──────────────────────────────────────────────
C_BG       = RGBColor(0x0D, 0x11, 0x17)  # 深蓝黑背景
C_ACCENT   = RGBColor(0x00, 0xB4, 0xD8)  # 亮青色
C_ACCENT2  = RGBColor(0x90, 0xE0, 0xEF)  # 浅青色
C_WHITE    = RGBColor(0xFF, 0xFF, 0xFF)
C_GRAY     = RGBColor(0xB0, 0xB8, 0xC0)
C_DARK     = RGBColor(0x14, 0x1B, 0x25)
C_CARD     = RGBColor(0x1A, 0x22, 0x2E)
C_ORANGE   = RGBColor(0xFF, 0xA5, 0x00)
C_GREEN    = RGBColor(0x00, 0xE6, 0x76)
C_PURPLE   = RGBColor(0xBB, 0x86, 0xFC)

SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)

prs = Presentation()
prs.slide_width = SLIDE_W
prs.slide_height = SLIDE_H


# ── 工具函数 ────────────────────────────────────────────
def _add_bg(slide, color=C_BG):
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = color


def _add_shape(slide, left, top, width, height, fill_color, border_color=None, radius=None):
    shape = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE,
        left, top, width, height,
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color
    if border_color:
        shape.line.color.rgb = border_color
        shape.line.width = Pt(1.5)
    else:
        shape.line.fill.background()
    return shape


def _add_text(slide, left, top, width, height, text, font_size=18,
              color=C_WHITE, bold=False, alignment=PP_ALIGN.LEFT, font_name="微软雅黑"):
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(font_size)
    p.font.color.rgb = color
    p.font.bold = bold
    p.font.name = font_name
    p.alignment = alignment
    return txBox


def _add_multiline(slide, left, top, width, height, lines, font_size=16,
                   color=C_WHITE, line_space=Pt(24), bold=False, font_name="微软雅黑"):
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = True
    for i, line in enumerate(lines):
        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        p.text = line
        p.font.size = Pt(font_size)
        p.font.color.rgb = color
        p.font.bold = bold
        p.font.name = font_name
        p.space_after = line_space
    return txBox


def _add_accent_bar(slide, left, top, width=Inches(0.08), height=Inches(0.6), color=C_ACCENT):
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()
    return shape


def _add_bottom_bar(slide):
    shape = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(0), Inches(7.2), SLIDE_W, Inches(0.3)
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = C_ACCENT
    shape.line.fill.background()


def _card(slide, left, top, w, h, title, body_lines, icon_text="", accent=C_ACCENT):
    _add_shape(slide, left, top, w, h, C_CARD, border_color=accent, radius=True)
    if icon_text:
        _add_text(slide, left + Inches(0.3), top + Inches(0.2), Inches(0.6), Inches(0.6),
                  icon_text, font_size=28, color=accent, bold=True)
    _add_text(slide, left + Inches(0.3) + (Inches(0.7) if icon_text else 0),
              top + Inches(0.2), w - Inches(0.6), Inches(0.5),
              title, font_size=20, color=C_WHITE, bold=True)
    _add_multiline(slide, left + Inches(0.3), top + Inches(0.75), w - Inches(0.6), h - Inches(1),
                   body_lines, font_size=14, color=C_GRAY, line_space=Pt(20))


# ═══════════════════════════════════════════════════════
# SLIDE 1 — 封面
# ═══════════════════════════════════════════════════════
sl = prs.slides.add_slide(prs.slide_layouts[6])
_add_bg(sl)
_add_shape(sl, Inches(0), Inches(0), SLIDE_W, Inches(0.06), C_ACCENT)
_add_bottom_bar(sl)

_add_text(sl, Inches(1.5), Inches(1.8), Inches(10), Inches(1),
          "SynerGist", font_size=60, color=C_ACCENT, bold=True)
_add_text(sl, Inches(1.5), Inches(3.0), Inches(10), Inches(0.8),
          "DNN 模型分割与分布式推理调度系统", font_size=32, color=C_WHITE, bold=True)
_add_text(sl, Inches(1.5), Inches(3.9), Inches(10), Inches(0.6),
          "Synergy + Gist — 在多边缘服务器间实现模型推理的协同精髓", font_size=18, color=C_GRAY)

lines = [
    "▸  基于 VGG5 的按层模型分割与链式推理",
    "▸  PPO 强化学习自动学习最优分割策略",
    "▸  资源感知的动态分割点选择",
    "▸  边缘子任务调度算法",
]
_add_multiline(sl, Inches(1.5), Inches(5.0), Inches(8), Inches(2), lines, font_size=16, color=C_ACCENT2)


# ═══════════════════════════════════════════════════════
# SLIDE 2 — 项目概览
# ═══════════════════════════════════════════════════════
sl = prs.slides.add_slide(prs.slide_layouts[6])
_add_bg(sl)
_add_accent_bar(sl, Inches(0.8), Inches(0.6))
_add_text(sl, Inches(1.1), Inches(0.55), Inches(6), Inches(0.7),
          "项目概览", font_size=36, color=C_WHITE, bold=True)
_add_bottom_bar(sl)

_card(sl, Inches(0.8), Inches(1.8), Inches(3.6), Inches(2.3),
      "核心目标", [
          "将完整 DNN 模型按层分割",
          "到多个边缘节点协同推理",
          "通过 RL 自动学习分割策略",
      ], "🎯", C_ACCENT)

_card(sl, Inches(4.8), Inches(1.8), Inches(3.6), Inches(2.3),
      "实验模型", [
          "VGG5 (简化版) — 共 7 层",
          "3 Conv + 2 MaxPool + 2 Dense",
          "数据集：CIFAR-10",
      ], "🧠", C_ORANGE)

_card(sl, Inches(8.8), Inches(1.8), Inches(3.6), Inches(2.3),
      "通信协议", [
          "TCP Socket + Pickle 序列化",
          "4 字节大端长度头 + 消息体",
          "链式前向传递中间激活",
      ], "🔗", C_GREEN)

_card(sl, Inches(0.8), Inches(4.6), Inches(3.6), Inches(2.3),
      "分割策略", [
          "随机分割：随机选择中间层",
          "资源感知：CPU/内存/网络感知",
          "RL (PPO)：自动优化分割点",
      ], "⚡", C_PURPLE)

_card(sl, Inches(4.8), Inches(4.6), Inches(3.6), Inches(2.3),
      "强化学习", [
          "PPO (Actor-Critic) 算法",
          "滑窗状态衍生 (维度×3)",
          "DQN / Dueling DQN 备选",
      ], "🤖", C_ACCENT)

_card(sl, Inches(8.8), Inches(4.6), Inches(3.6), Inches(2.3),
      "技术栈", [
          "PyTorch · Paramiko · Scikit-learn",
          "Socket · Matplotlib · NumPy",
          "Python 3.8+",
      ], "🛠", C_ORANGE)


# ═══════════════════════════════════════════════════════
# SLIDE 3 — 项目结构
# ═══════════════════════════════════════════════════════
sl = prs.slides.add_slide(prs.slide_layouts[6])
_add_bg(sl)
_add_accent_bar(sl, Inches(0.8), Inches(0.6))
_add_text(sl, Inches(1.1), Inches(0.55), Inches(6), Inches(0.7),
          "项目结构总览", font_size=36, color=C_WHITE, bold=True)
_add_bottom_bar(sl)

tree_left = [
    "Partition_Scheduling/",
    "├── config.py                    全局配置",
    "├── server.py                    服务端入口",
    "├── client.py                    客户端入口",
    "├── utils.py                     工具函数",
    "├── Scheduling.py                子任务调度",
    "├── models/",
    "│   ├── model_struct.py          层元数据",
    "│   └── vgg5/vgg5.py             可分割VGG5",
    "├── communication/",
    "│   ├── communicator.py          Socket通信",
    "│   ├── demo_json/               JSON示例",
    "│   └── demo_send/               链式推理演示",
]
tree_right = [
    "├── strategy/",
    "│   ├── segment_strategy.py      分割策略",
    "│   └── resource_utilization.py  资源采集",
    "├── RL/                          PPO主模块",
    "│   ├── PPO.py / RLEnv.py",
    "│   ├── RL_serverrun.py / clientrun.py",
    "│   └── state_derivation.py      状态衍生",
    "├── RL_multiple/                 多客户端变体",
    "├── RL_IAF/                      IAF变体",
    "├── local_inference/             本地实验集",
    "│   ├── RL/  (DQN变体)",
    "│   ├── single_data_from_server/",
    "│   └── multiple_task_from_server/",
    "└── scientific_research_drawing/ 科研绘图",
]

_add_shape(sl, Inches(0.5), Inches(1.5), Inches(5.9), Inches(5.5), C_CARD, border_color=C_ACCENT, radius=True)
_add_multiline(sl, Inches(0.7), Inches(1.6), Inches(5.5), Inches(5.3),
               tree_left, font_size=13, color=C_ACCENT2, line_space=Pt(18), font_name="Consolas")

_add_shape(sl, Inches(6.7), Inches(1.5), Inches(5.9), Inches(5.5), C_CARD, border_color=C_ACCENT, radius=True)
_add_multiline(sl, Inches(6.9), Inches(1.6), Inches(5.5), Inches(5.3),
               tree_right, font_size=13, color=C_ACCENT2, line_space=Pt(18), font_name="Consolas")

_add_text(sl, Inches(0.8), Inches(7.0), Inches(10), Inches(0.4),
          "共 103 个文件 ·  96 个 .py  ·  5 个 .md  ·  1 个 requirements.txt",
          font_size=14, color=C_GRAY)


# ═══════════════════════════════════════════════════════
# SLIDE 4 — 模型分割原理
# ═══════════════════════════════════════════════════════
sl = prs.slides.add_slide(prs.slide_layouts[6])
_add_bg(sl)
_add_accent_bar(sl, Inches(0.8), Inches(0.6))
_add_text(sl, Inches(1.1), Inches(0.55), Inches(8), Inches(0.7),
          "核心概念 — 模型分割 (Model Partitioning)", font_size=36, color=C_WHITE, bold=True)
_add_bottom_bar(sl)

# VGG5 table
table_data = [
    ["层索引", "类型", "输入通道", "输出通道", "说明"],
    ["0", "Conv", "3", "32", "卷积 + BN + ReLU"],
    ["1", "MaxPool", "32", "32", "最大池化"],
    ["2", "Conv", "32", "64", "卷积 + BN + ReLU"],
    ["3", "MaxPool", "64", "64", "最大池化"],
    ["4", "Conv", "64", "64", "卷积 + BN + ReLU"],
    ["5", "Dense", "4096", "128", "全连接"],
    ["6", "Dense", "128", "10", "输出（10 分类）"],
]

rows, cols = len(table_data), len(table_data[0])
tbl_shape = sl.shapes.add_table(rows, cols, Inches(0.8), Inches(1.6), Inches(6.5), Inches(3.5))
tbl = tbl_shape.table
col_widths = [Inches(0.8), Inches(1), Inches(1.1), Inches(1.1), Inches(2.5)]
for i, w in enumerate(col_widths):
    tbl.columns[i].width = w

for r in range(rows):
    for c in range(cols):
        cell = tbl.cell(r, c)
        cell.text = table_data[r][c]
        for paragraph in cell.text_frame.paragraphs:
            paragraph.font.size = Pt(14)
            paragraph.font.name = "微软雅黑"
            paragraph.alignment = PP_ALIGN.CENTER
            if r == 0:
                paragraph.font.bold = True
                paragraph.font.color.rgb = C_BG
            else:
                paragraph.font.color.rgb = C_WHITE
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        if r == 0:
            cell.fill.solid()
            cell.fill.fore_color.rgb = C_ACCENT
        else:
            cell.fill.solid()
            cell.fill.fore_color.rgb = C_CARD if r % 2 == 1 else C_DARK

# partition diagram
diagram_lines = [
    "┌──────────────┐      ┌──────────────┐      ┌──────────────┐",
    "│   设备 1      │ ───▶ │   设备 2      │ ───▶ │   设备 3      │",
    "│  第 0-1 层    │      │  第 2-3 层    │      │  第 4-6 层    │",
    "│ (Conv+Pool)   │      │ (Conv+Pool)   │      │ (Conv+Dense)  │",
    "└──────────────┘      └──────────────┘      └──────────────┘",
    "     输入                 中间激活               最终输出",
]
_add_shape(sl, Inches(7.8), Inches(1.6), Inches(5), Inches(3.5), C_CARD, border_color=C_ACCENT, radius=True)
_add_text(sl, Inches(8.0), Inches(1.7), Inches(4.6), Inches(0.5),
          "分割示意图", font_size=18, color=C_ACCENT, bold=True)
_add_multiline(sl, Inches(8.0), Inches(2.2), Inches(4.6), Inches(2.5),
               diagram_lines, font_size=11, color=C_ACCENT2, line_space=Pt(15), font_name="Consolas")

# strategy summary
_add_shape(sl, Inches(0.8), Inches(5.4), Inches(12), Inches(1.5), C_CARD, border_color=C_PURPLE, radius=True)
_add_text(sl, Inches(1.1), Inches(5.5), Inches(4), Inches(0.5),
          "三种分割策略", font_size=20, color=C_PURPLE, bold=True)
strat_lines = [
    "① 随机分割 — 在可选层中随机选择 N-1 个分割点，用于基线对比",
    "② 资源感知分割 — 通过 SSH 采集 CPU/内存/网络利用率，将计算量大的层分配给资源充足的节点",
    "③ PPO 强化学习 — 使用 Actor-Critic 网络自动学习最优分割策略（核心方法）",
]
_add_multiline(sl, Inches(1.1), Inches(6.0), Inches(11.5), Inches(1.0),
               strat_lines, font_size=14, color=C_GRAY, line_space=Pt(18))


# ═══════════════════════════════════════════════════════
# SLIDE 5 — 分布式推理流程
# ═══════════════════════════════════════════════════════
sl = prs.slides.add_slide(prs.slide_layouts[6])
_add_bg(sl)
_add_accent_bar(sl, Inches(0.8), Inches(0.6))
_add_text(sl, Inches(1.1), Inches(0.55), Inches(8), Inches(0.7),
          "分布式推理架构", font_size=36, color=C_WHITE, bold=True)
_add_bottom_bar(sl)

# Server box
_add_shape(sl, Inches(1.5), Inches(1.6), Inches(3.5), Inches(2.2), C_CARD, border_color=C_ACCENT, radius=True)
_add_text(sl, Inches(1.7), Inches(1.7), Inches(3), Inches(0.5),
          "server.py  (协调端)", font_size=18, color=C_ACCENT, bold=True)
_add_multiline(sl, Inches(1.7), Inches(2.2), Inches(3), Inches(1.5), [
    "1. SSH 采集所有节点资源",
    "2. 资源感知计算分割点",
    "3. 加载 CIFAR-10 数据",
    "4. Socket 发送至链首客户端",
], font_size=13, color=C_GRAY, line_space=Pt(16))

# Client boxes
client_info = [
    ("client.py #1", "执行第 0-1 层", "Conv + Pool"),
    ("client.py #2", "执行第 2-3 层", "Conv + Pool"),
    ("client.py #3", "执行第 4-6 层", "Conv + Dense → loss/acc"),
]
for i, (name, layer, desc) in enumerate(client_info):
    x = Inches(6.5)
    y = Inches(1.6 + i * 2.0)
    _add_shape(sl, x, y, Inches(5.5), Inches(1.5), C_CARD, border_color=C_GREEN if i < 2 else C_ORANGE, radius=True)
    _add_text(sl, x + Inches(0.2), y + Inches(0.1), Inches(3), Inches(0.4),
              name, font_size=16, color=C_GREEN if i < 2 else C_ORANGE, bold=True)
    _add_text(sl, x + Inches(0.2), y + Inches(0.5), Inches(5), Inches(0.4),
              f"{layer}  |  {desc}", font_size=13, color=C_GRAY)
    if i < 2:
        _add_text(sl, x + Inches(0.2), y + Inches(0.95), Inches(5), Inches(0.4),
                  "→ 转发中间激活给下一节点", font_size=12, color=C_ACCENT2)

# Arrows
_add_text(sl, Inches(5.2), Inches(2.2), Inches(1.3), Inches(0.5),
          "Socket ──▶", font_size=14, color=C_ACCENT, bold=True)
_add_text(sl, Inches(12.2), Inches(2.8), Inches(1), Inches(0.5),
          "▼", font_size=20, color=C_GREEN, bold=True)
_add_text(sl, Inches(12.2), Inches(4.8), Inches(1), Inches(0.5),
          "▼", font_size=20, color=C_GREEN, bold=True)

# Communication protocol box
_add_shape(sl, Inches(1.5), Inches(4.2), Inches(3.5), Inches(2.8), C_CARD, border_color=C_PURPLE, radius=True)
_add_text(sl, Inches(1.7), Inches(4.3), Inches(3), Inches(0.5),
          "通信协议", font_size=18, color=C_PURPLE, bold=True)
_add_multiline(sl, Inches(1.7), Inches(4.85), Inches(3), Inches(2), [
    "[4字节大端长度头]",
    "  + [Pickle序列化消息体]",
    "",
    "消息体：Python 列表",
    "首元素：消息类型字符串",
    "后续元素：数据/张量/配置",
], font_size=12, color=C_GRAY, line_space=Pt(14), font_name="Consolas")


# ═══════════════════════════════════════════════════════
# SLIDE 6 — PPO 强化学习
# ═══════════════════════════════════════════════════════
sl = prs.slides.add_slide(prs.slide_layouts[6])
_add_bg(sl)
_add_accent_bar(sl, Inches(0.8), Inches(0.6))
_add_text(sl, Inches(1.1), Inches(0.55), Inches(10), Inches(0.7),
          "PPO 强化学习自动分割策略", font_size=36, color=C_WHITE, bold=True)
_add_bottom_bar(sl)

# PPO formula
_add_shape(sl, Inches(0.8), Inches(1.5), Inches(12), Inches(1.3), C_CARD, border_color=C_ACCENT, radius=True)
_add_text(sl, Inches(1.0), Inches(1.6), Inches(11.5), Inches(0.5),
          "PPO Clip 目标函数", font_size=18, color=C_ACCENT, bold=True)
_add_text(sl, Inches(1.0), Inches(2.05), Inches(11.5), Inches(0.5),
          "L_CLIP(θ) = E[ min( r(θ)·A,  clip( r(θ), 1-ε, 1+ε )·A ) ]      r(θ) = π_θ(a|s) / π_θ_old(a|s),   ε=0.2",
          font_size=15, color=C_ACCENT2, font_name="Consolas")

# MDP elements
_card(sl, Inches(0.8), Inches(3.2), Inches(3.6), Inches(2.0),
      "状态 (State)", [
          "推理时间 + 卸载比例",
          "经状态衍生增强为 3 倍维度",
          "= [当前值, 历史均值, 变化趋势]",
      ], "S", C_ACCENT)

_card(sl, Inches(4.8), Inches(3.2), Inches(3.6), Inches(2.0),
      "动作 (Action)", [
          "连续值 → Sigmoid → [0,1]",
          "映射为每组客户端的分割层",
          "多元正态分布采样",
      ], "A", C_ORANGE)

_card(sl, Inches(8.8), Inches(3.2), Inches(3.6), Inches(2.0),
      "奖励 (Reward)", [
          "Σ(基线时间 - 推理时间)",
          "         / 基线时间",
          "时间越短，奖励越大",
      ], "R", C_GREEN)

# State derivation
_add_shape(sl, Inches(0.8), Inches(5.6), Inches(5.8), Inches(1.5), C_CARD, border_color=C_PURPLE, radius=True)
_add_text(sl, Inches(1.0), Inches(5.7), Inches(5.5), Inches(0.5),
          "状态衍生 (State Derivation)", font_size=18, color=C_PURPLE, bold=True)
_add_text(sl, Inches(1.0), Inches(6.2), Inches(5.5), Inches(0.7),
          "derived = [ s(t),  mean(buffer),  mean(Δs) ]\n"
          "原始 2G 维 → 衍生 6G 维 (窗口大小=10)",
          font_size=14, color=C_GRAY)

# Network architecture
_add_shape(sl, Inches(7.0), Inches(5.6), Inches(5.6), Inches(1.5), C_CARD, border_color=C_ACCENT, radius=True)
_add_text(sl, Inches(7.2), Inches(5.7), Inches(5.3), Inches(0.5),
          "Actor-Critic 网络", font_size=18, color=C_ACCENT, bold=True)
_add_multiline(sl, Inches(7.2), Inches(6.2), Inches(5.3), Inches(0.7), [
    "输入: state_dim×3  →  隐层: 64  →  Actor: Sigmoid([0,1])",
    "                                         →  Critic: 状态价值 V(s)",
], font_size=13, color=C_GRAY, line_space=Pt(16))


# ═══════════════════════════════════════════════════════
# SLIDE 7 — RL 训练流程
# ═══════════════════════════════════════════════════════
sl = prs.slides.add_slide(prs.slide_layouts[6])
_add_bg(sl)
_add_accent_bar(sl, Inches(0.8), Inches(0.6))
_add_text(sl, Inches(1.1), Inches(0.55), Inches(8), Inches(0.7),
          "RL 训练架构", font_size=36, color=C_WHITE, bold=True)
_add_bottom_bar(sl)

# Server side
_add_shape(sl, Inches(0.8), Inches(1.5), Inches(5.5), Inches(5.5), C_CARD, border_color=C_ACCENT, radius=True)
_add_text(sl, Inches(1.0), Inches(1.6), Inches(5), Inches(0.5),
          "RL_serverrun.py  —  训练循环", font_size=20, color=C_ACCENT, bold=True)

server_modules = [
    ("PPO.py", "Actor-Critic 网络\nselect_action / update / explore_decay", C_ORANGE),
    ("RLEnv.py (Env)", "reset / step / group (KMeans)\ninfer (多线程) / calculate_reward", C_GREEN),
    ("state_derivation.py", "滑窗均值 + 差分\n维度扩展 ×3", C_PURPLE),
]
for i, (name, desc, color) in enumerate(server_modules):
    y = Inches(2.3 + i * 1.5)
    _add_shape(sl, Inches(1.2), y, Inches(4.8), Inches(1.2), C_DARK, border_color=color, radius=True)
    _add_text(sl, Inches(1.4), y + Inches(0.1), Inches(4.4), Inches(0.4),
              name, font_size=16, color=color, bold=True)
    _add_text(sl, Inches(1.4), y + Inches(0.5), Inches(4.4), Inches(0.6),
              desc, font_size=12, color=C_GRAY)

# Arrow
_add_text(sl, Inches(6.4), Inches(3.5), Inches(1), Inches(1),
          "◀─▶\nSocket", font_size=16, color=C_ACCENT, bold=True, alignment=PP_ALIGN.CENTER)

# Client side
_add_shape(sl, Inches(7.2), Inches(1.5), Inches(5.5), Inches(5.5), C_CARD, border_color=C_GREEN, radius=True)
_add_text(sl, Inches(7.4), Inches(1.6), Inches(5), Inches(0.5),
          "RL_clientrun.py  —  客户端集群", font_size=20, color=C_GREEN, bold=True)

for i in range(3):
    y = Inches(2.5 + i * 1.4)
    _add_shape(sl, Inches(7.6), y, Inches(4.8), Inches(1.1), C_DARK, border_color=C_ACCENT2, radius=True)
    _add_text(sl, Inches(7.8), y + Inches(0.1), Inches(4.4), Inches(0.4),
              f"RL_Client  设备 {i+1}", font_size=15, color=C_ACCENT2, bold=True)
    _add_text(sl, Inches(7.8), y + Inches(0.5), Inches(4.4), Inches(0.5),
              "initialize() → infer() → 本地推理/卸载推理", font_size=12, color=C_GRAY)

_add_text(sl, Inches(7.6), Inches(6.7), Inches(4.8), Inches(0.4),
          "correspondence.py — RL 专用 Socket 通信基类", font_size=12, color=C_GRAY)


# ═══════════════════════════════════════════════════════
# SLIDE 8 — 子任务调度算法
# ═══════════════════════════════════════════════════════
sl = prs.slides.add_slide(prs.slide_layouts[6])
_add_bg(sl)
_add_accent_bar(sl, Inches(0.8), Inches(0.6))
_add_text(sl, Inches(1.1), Inches(0.55), Inches(8), Inches(0.7),
          "边缘子任务调度算法", font_size=36, color=C_WHITE, bold=True)
_add_bottom_bar(sl)

phases = [
    ("阶段一：分类排序", C_ACCENT, [
        "每个边缘节点内部",
        "按 执行时间 vs 传输时间 关系",
        "将子任务分为 A 类和 B 类",
        "A 类：执行时间 ≤ 传输时间",
        "B 类：执行时间 > 传输时间",
    ]),
    ("阶段二：A 类优先", C_ORANGE, [
        "优先调度 A 类任务",
        "串行排程（按顺序放入时间轴）",
        "记录每个任务的结束时间",
        "为后续任务确定可用时间窗口",
        "",
    ]),
    ("阶段三：贪心插入", C_GREEN, [
        "对非 A 类（B 类）任务",
        "按「全局最小等待时间」贪心插入",
        "find_min_wait_time() 寻找",
        "最优的插入位置和时间槽",
        "目标：最小化总完成时间",
    ]),
]

for i, (title, color, lines) in enumerate(phases):
    x = Inches(0.8 + i * 4.1)
    _add_shape(sl, x, Inches(1.5), Inches(3.8), Inches(4.5), C_CARD, border_color=color, radius=True)
    _add_text(sl, x + Inches(0.2), Inches(1.6), Inches(3.4), Inches(0.5),
              title, font_size=20, color=color, bold=True)
    # Step number circle
    circle = sl.shapes.add_shape(MSO_SHAPE.OVAL, x + Inches(3.0), Inches(1.65), Inches(0.45), Inches(0.45))
    circle.fill.solid()
    circle.fill.fore_color.rgb = color
    circle.line.fill.background()
    tf = circle.text_frame
    tf.paragraphs[0].text = str(i + 1)
    tf.paragraphs[0].font.size = Pt(18)
    tf.paragraphs[0].font.color.rgb = C_BG
    tf.paragraphs[0].font.bold = True
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER

    _add_multiline(sl, x + Inches(0.2), Inches(2.3), Inches(3.4), Inches(3.5),
                   lines, font_size=14, color=C_GRAY, line_space=Pt(22))

_add_shape(sl, Inches(0.8), Inches(6.3), Inches(12), Inches(0.8), C_DARK, border_color=C_PURPLE, radius=True)
_add_text(sl, Inches(1.0), Inches(6.4), Inches(11.5), Inches(0.6),
          "核心函数：scheduling_subtasks_ess()  ·  sort_edges()  ·  find_min_wait_time()  ·  print_ess()",
          font_size=15, color=C_PURPLE)


# ═══════════════════════════════════════════════════════
# SLIDE 9 — 实验变体与本地推理
# ═══════════════════════════════════════════════════════
sl = prs.slides.add_slide(prs.slide_layouts[6])
_add_bg(sl)
_add_accent_bar(sl, Inches(0.8), Inches(0.6))
_add_text(sl, Inches(1.1), Inches(0.55), Inches(8), Inches(0.7),
          "实验变体 & 本地推理", font_size=36, color=C_WHITE, bold=True)
_add_bottom_bar(sl)

# RL variants
_add_text(sl, Inches(0.8), Inches(1.5), Inches(5), Inches(0.5),
          "RL 变体模块", font_size=22, color=C_ACCENT, bold=True)

rl_variants = [
    ("RL/", "PPO + 滑窗状态衍生", "核心方法", C_ACCENT),
    ("RL_multiple/", "PPO + 多客户端扩展", "扩展实验", C_ORANGE),
    ("RL_IAF/", "PPO + IAF 状态衍生 (LSTM)", "实验性", C_PURPLE),
    ("local_inference/RL/", "DQN / 优化 DQN / GRU", "备选算法", C_GREEN),
]
for i, (path, desc, tag, color) in enumerate(rl_variants):
    y = Inches(2.1 + i * 1.0)
    _add_shape(sl, Inches(0.8), y, Inches(6.2), Inches(0.85), C_CARD, border_color=color, radius=True)
    _add_text(sl, Inches(1.0), y + Inches(0.05), Inches(2), Inches(0.4),
              path, font_size=14, color=color, bold=True, font_name="Consolas")
    _add_text(sl, Inches(3.2), y + Inches(0.05), Inches(2.8), Inches(0.4),
              desc, font_size=13, color=C_WHITE)
    _add_text(sl, Inches(1.0), y + Inches(0.42), Inches(5.5), Inches(0.4),
              tag, font_size=11, color=C_GRAY)

# Local inference variants
_add_text(sl, Inches(7.5), Inches(1.5), Inches(5), Inches(0.5),
          "本地推理实验 (local_inference/)", font_size=22, color=C_GREEN, bold=True)

local_vars = [
    ("single_data_from_server/", "基础链式推理（数据在服务端）"),
    ("single_data_from_client/", "基础链式推理（数据在客户端）"),
    ("single_data_from_server_recycle/", "带回收聚合的推理变体"),
    ("single_data_from_server_RL/", "Gym FederatedEnv + PPO"),
    ("multiple_task_from_server/", "多任务 + Barrier 同步"),
    ("rl_data_from_server/", "Dueling DQN + 服务端数据"),
]
for i, (path, desc) in enumerate(local_vars):
    y = Inches(2.1 + i * 0.82)
    _add_shape(sl, Inches(7.5), y, Inches(5.3), Inches(0.7), C_CARD, radius=True)
    _add_text(sl, Inches(7.7), y + Inches(0.05), Inches(5), Inches(0.35),
              path, font_size=12, color=C_ACCENT2, bold=True, font_name="Consolas")
    _add_text(sl, Inches(7.7), y + Inches(0.35), Inches(5), Inches(0.35),
              desc, font_size=11, color=C_GRAY)

_add_shape(sl, Inches(7.5), Inches(7.0) - Inches(0.3), Inches(5.3), Inches(0.4), C_DARK, radius=True)
_add_text(sl, Inches(7.7), Inches(7.0) - Inches(0.25), Inches(5), Inches(0.3),
          "scientific_research_drawing/ — matplotlib 论文绘图脚本", font_size=12, color=C_GRAY)


# ═══════════════════════════════════════════════════════
# SLIDE 10 — 关键配置与运行方式
# ═══════════════════════════════════════════════════════
sl = prs.slides.add_slide(prs.slide_layouts[6])
_add_bg(sl)
_add_accent_bar(sl, Inches(0.8), Inches(0.6))
_add_text(sl, Inches(1.1), Inches(0.55), Inches(8), Inches(0.7),
          "配置说明 & 运行方式", font_size=36, color=C_WHITE, bold=True)
_add_bottom_bar(sl)

# Config table
config_items = [
    ["配置项", "默认值", "说明"],
    ["SERVER_ADDR / PORT", "192.168.215.128:51000", "协调端地址"],
    ["server_list", "4 台设备", "边缘设备列表 (IP/SSH/端口)"],
    ["N / B", "10000 / 256", "数据总量 / 批次大小"],
    ["K / G", "4 / 3", "设备数 / 分组数"],
    ["split_layer", "[6, 6, 6]", "初始分割层"],
    ["max_episodes", "100", "RL 最大训练回合"],
    ["K_epochs / eps_clip", "50 / 0.2", "PPO 更新迭代 / 裁剪参数"],
    ["window_size", "10", "状态衍生窗口大小"],
]
rows, cols = len(config_items), len(config_items[0])
tbl_shape = sl.shapes.add_table(rows, cols, Inches(0.8), Inches(1.5), Inches(6.5), Inches(3.8))
tbl = tbl_shape.table
for w, width in enumerate([Inches(2.2), Inches(2.2), Inches(2.1)]):
    tbl.columns[w].width = width

for r in range(rows):
    for c in range(cols):
        cell = tbl.cell(r, c)
        cell.text = config_items[r][c]
        for paragraph in cell.text_frame.paragraphs:
            paragraph.font.size = Pt(13)
            paragraph.font.name = "微软雅黑" if c > 0 else "Consolas"
            paragraph.alignment = PP_ALIGN.CENTER if c > 0 else PP_ALIGN.LEFT
            if r == 0:
                paragraph.font.bold = True
                paragraph.font.color.rgb = C_BG
            else:
                paragraph.font.color.rgb = C_WHITE
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        if r == 0:
            cell.fill.solid()
            cell.fill.fore_color.rgb = C_ACCENT
        else:
            cell.fill.solid()
            cell.fill.fore_color.rgb = C_CARD if r % 2 == 1 else C_DARK

# Run instructions
_add_shape(sl, Inches(7.8), Inches(1.5), Inches(5), Inches(5.4), C_CARD, border_color=C_GREEN, radius=True)
_add_text(sl, Inches(8.0), Inches(1.6), Inches(4.5), Inches(0.5),
          "运行方式", font_size=22, color=C_GREEN, bold=True)

run_sections = [
    ("① 分布式推理", [
        "# 先启动客户端",
        "python client.py",
        "# 再启动服务端",
        "python server.py",
    ], C_ACCENT),
    ("② RL 训练 (PPO)", [
        "cd RL/",
        "python RL_serverrun.py",
        "python RL_clientrun.py",
    ], C_ORANGE),
    ("③ 本地测试", [
        "cd local_inference/",
        "single_data_from_server/",
        "python server.py",
        "python client_1/2/3.py",
    ], C_PURPLE),
]
y_offset = Inches(2.2)
for title, cmds, color in run_sections:
    _add_text(sl, Inches(8.0), y_offset, Inches(4.5), Inches(0.4),
              title, font_size=15, color=color, bold=True)
    y_offset += Inches(0.35)
    _add_multiline(sl, Inches(8.2), y_offset, Inches(4.3), Inches(len(cmds) * 0.3),
                   cmds, font_size=11, color=C_ACCENT2, line_space=Pt(14), font_name="Consolas")
    y_offset += Inches(len(cmds) * 0.25 + 0.2)


# ═══════════════════════════════════════════════════════
# SLIDE 11 — 依赖与技术栈
# ═══════════════════════════════════════════════════════
sl = prs.slides.add_slide(prs.slide_layouts[6])
_add_bg(sl)
_add_accent_bar(sl, Inches(0.8), Inches(0.6))
_add_text(sl, Inches(1.1), Inches(0.55), Inches(8), Inches(0.7),
          "技术栈 & 依赖", font_size=36, color=C_WHITE, bold=True)
_add_bottom_bar(sl)

tech_cards = [
    ("PyTorch", "深度学习框架\n模型构建与训练\ntorch==1.10.0", "🔥", C_ORANGE),
    ("Socket + Pickle", "节点间 TCP 通信\n4字节长度头协议\n链式中间激活传递", "🔌", C_ACCENT),
    ("Paramiko", "SSH 远程命令\n采集 CPU/GPU/内存\n网络利用率信息", "🖥", C_GREEN),
    ("PPO (RL)", "Actor-Critic 策略\n自动分割优化\n探索衰减机制", "🧠", C_PURPLE),
    ("Scikit-learn", "KMeans 聚类\n客户端自动分组\nv1.3.0", "📊", C_ACCENT2),
    ("Matplotlib", "科研论文绘图\n对比实验可视化\nv3.7.3", "📈", C_ORANGE),
]

for i, (name, desc, icon, color) in enumerate(tech_cards):
    col = i % 3
    row = i // 3
    x = Inches(0.8 + col * 4.1)
    y = Inches(1.5 + row * 3.0)
    _add_shape(sl, x, y, Inches(3.7), Inches(2.5), C_CARD, border_color=color, radius=True)
    _add_text(sl, x + Inches(0.3), y + Inches(0.2), Inches(0.6), Inches(0.6),
              icon, font_size=28, color=color)
    _add_text(sl, x + Inches(0.9), y + Inches(0.2), Inches(2.5), Inches(0.5),
              name, font_size=20, color=C_WHITE, bold=True)
    _add_text(sl, x + Inches(0.3), y + Inches(0.85), Inches(3.1), Inches(1.4),
              desc, font_size=14, color=C_GRAY)


# ═══════════════════════════════════════════════════════
# SLIDE 12 — 总结
# ═══════════════════════════════════════════════════════
sl = prs.slides.add_slide(prs.slide_layouts[6])
_add_bg(sl)
_add_shape(sl, Inches(0), Inches(0), SLIDE_W, Inches(0.06), C_ACCENT)
_add_bottom_bar(sl)

_add_text(sl, Inches(1.5), Inches(1.5), Inches(10), Inches(1),
          "总结", font_size=48, color=C_ACCENT, bold=True)

summary_items = [
    ("模型分割", "VGG5 按层切分到多个边缘节点，链式协同推理"),
    ("资源感知", "SSH 采集节点资源，动态计算最优分割点"),
    ("PPO 自动优化", "Actor-Critic 网络 + 状态衍生，自动学习分割策略"),
    ("子任务调度", "三阶段算法：分类排序 → A类优先 → 贪心插入"),
    ("丰富实验", "DQN / Dueling DQN / IAF / Gym 等多种变体对比"),
    ("通信框架", "TCP Socket + Pickle 高效传输中间激活张量"),
]

for i, (title, desc) in enumerate(summary_items):
    y = Inches(2.8 + i * 0.72)
    _add_shape(sl, Inches(1.5), y, Inches(0.12), Inches(0.12), C_ACCENT)
    _add_text(sl, Inches(1.9), y - Inches(0.08), Inches(2.5), Inches(0.4),
              title, font_size=18, color=C_ACCENT, bold=True)
    _add_text(sl, Inches(4.5), y - Inches(0.08), Inches(7.5), Inches(0.4),
              desc, font_size=16, color=C_GRAY)

_add_text(sl, Inches(1.5), Inches(6.8), Inches(10), Inches(0.5),
          "SynerGist — 多服务器间模型推理的协同精髓",
          font_size=20, color=C_ACCENT2, bold=True)


# ── 保存 ──────────────────────────────────────────────
output_path = r"e:\1_MyCode\model_partitioning\Partition_Scheduling\SynerGist_项目介绍.pptx"
prs.save(output_path)
print(f"PPT 已生成: {output_path}")

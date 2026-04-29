# -*- coding: utf-8 -*-
"""
生成 DNN/LLM 分布式推理平台讨论 PPT
使用 python-pptx 创建会议讨论汇报材料
"""
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.enum.shapes import MSO_SHAPE
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn
from copy import deepcopy

# ===== 主题色 =====
COLOR_PRIMARY = RGBColor(0x1F, 0x3A, 0x68)      # 深蓝
COLOR_ACCENT = RGBColor(0x2E, 0x86, 0xAB)       # 中蓝
COLOR_HIGHLIGHT = RGBColor(0xE0, 0x6C, 0x00)    # 橙
COLOR_LIGHT = RGBColor(0xEC, 0xF2, 0xF9)        # 浅蓝灰
COLOR_TEXT = RGBColor(0x22, 0x2A, 0x35)         # 深灰黑
COLOR_MUTED = RGBColor(0x6B, 0x73, 0x80)        # 中灰
COLOR_GREEN = RGBColor(0x2E, 0x8B, 0x57)
COLOR_RED = RGBColor(0xC1, 0x44, 0x2E)
COLOR_YELLOW = RGBColor(0xE6, 0xB8, 0x22)

CN_FONT = '微软雅黑'
EN_FONT = 'Calibri'

# ===== Slide 尺寸 16:9 =====
SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)

prs = Presentation()
prs.slide_width = SLIDE_W
prs.slide_height = SLIDE_H


def set_run(run, text, size=18, bold=False, color=COLOR_TEXT, font=CN_FONT):
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = font
    # 让中文也走指定字体
    rPr = run._r.get_or_add_rPr()
    eastAsia = rPr.find(qn('a:ea'))
    if eastAsia is None:
        from lxml import etree
        ea = etree.SubElement(rPr, qn('a:ea'))
        ea.set('typeface', CN_FONT)


def add_textbox(slide, left, top, width, height, text, size=18, bold=False,
                color=COLOR_TEXT, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP,
                font=CN_FONT, fill=None):
    tb = slide.shapes.add_textbox(left, top, width, height)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.05)
    tf.margin_right = Inches(0.05)
    tf.margin_top = Inches(0.03)
    tf.margin_bottom = Inches(0.03)
    tf.vertical_anchor = anchor
    p = tf.paragraphs[0]
    p.alignment = align
    set_run(p.add_run(), text, size=size, bold=bold, color=color, font=font)
    if fill is not None:
        tb.fill.solid()
        tb.fill.fore_color.rgb = fill
        tb.line.fill.background()
    else:
        tb.line.fill.background()
        tb.fill.background()
    return tb


def add_rect(slide, left, top, width, height, fill=COLOR_LIGHT, line=None,
             shadow=False):
    shp = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shp.adjustments[0] = 0.08
    shp.fill.solid()
    shp.fill.fore_color.rgb = fill
    if line is None:
        shp.line.fill.background()
    else:
        shp.line.color.rgb = line
        shp.line.width = Pt(0.75)
    if not shadow:
        shp.shadow.inherit = False
        # disable shadow
        sppr = shp._element.spPr
        from lxml import etree
        for el in sppr.findall(qn('a:effectLst')):
            sppr.remove(el)
        effLst = etree.SubElement(sppr, qn('a:effectLst'))
    shp.text_frame.text = ""
    return shp


def add_card(slide, left, top, width, height, title, body_lines,
             color=COLOR_ACCENT, title_size=16, body_size=12):
    """带顶色横条的卡片"""
    bg = add_rect(slide, left, top, width, height, fill=COLOR_LIGHT)
    # 顶部彩色横条
    bar = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, left, top, width, Inches(0.18))
    bar.fill.solid()
    bar.fill.fore_color.rgb = color
    bar.line.fill.background()

    # 标题
    add_textbox(slide, left + Inches(0.1), top + Inches(0.22),
                width - Inches(0.2), Inches(0.4),
                title, size=title_size, bold=True, color=color)

    # 正文
    bbox = slide.shapes.add_textbox(
        left + Inches(0.1), top + Inches(0.65),
        width - Inches(0.2), height - Inches(0.7))
    tf = bbox.text_frame
    tf.word_wrap = True
    bbox.line.fill.background()
    bbox.fill.background()

    for i, line in enumerate(body_lines):
        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        p.alignment = PP_ALIGN.LEFT
        set_run(p.add_run(), '• ' + line if not line.startswith('•') else line,
                size=body_size, color=COLOR_TEXT)
        p.space_after = Pt(2)


def add_title_band(slide, title, subtitle=None):
    """所有内容页统一的顶部标题条"""
    # 顶部彩条
    bar = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, 0, 0, SLIDE_W, Inches(0.85))
    bar.fill.solid()
    bar.fill.fore_color.rgb = COLOR_PRIMARY
    bar.line.fill.background()
    # 装饰小条
    dec = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(0.4), Inches(0.25),
        Inches(0.08), Inches(0.4))
    dec.fill.solid()
    dec.fill.fore_color.rgb = COLOR_HIGHLIGHT
    dec.line.fill.background()
    # 标题文字
    add_textbox(slide, Inches(0.6), Inches(0.13),
                Inches(11.5), Inches(0.45),
                title, size=24, bold=True,
                color=RGBColor(0xFF, 0xFF, 0xFF))
    if subtitle:
        add_textbox(slide, Inches(0.6), Inches(0.55),
                    Inches(11.5), Inches(0.3),
                    subtitle, size=12, bold=False,
                    color=RGBColor(0xCF, 0xDC, 0xEC))


def add_footer(slide, page_no, total):
    add_textbox(slide, Inches(0.4), SLIDE_H - Inches(0.35),
                Inches(6), Inches(0.3),
                'DNN/LLM 分布式推理平台需求讨论 · 2026-04-25', size=10,
                color=COLOR_MUTED)
    add_textbox(slide, SLIDE_W - Inches(1.5), SLIDE_H - Inches(0.35),
                Inches(1.2), Inches(0.3),
                f'{page_no} / {total}', size=10, color=COLOR_MUTED,
                align=PP_ALIGN.RIGHT)


def blank_slide():
    return prs.slides.add_slide(prs.slide_layouts[6])


# =========================================================
# Slide 1: 封面
# =========================================================
def slide_cover(page_no, total):
    s = blank_slide()
    # 大色块
    bg = slide_bg = s.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, 0, 0, SLIDE_W, SLIDE_H)
    bg.fill.solid()
    bg.fill.fore_color.rgb = COLOR_PRIMARY
    bg.line.fill.background()
    # 装饰圆
    for i, (l, t, w, c, alpha) in enumerate([
        (Inches(9.5), Inches(-1.5), Inches(6), COLOR_ACCENT, 0.4),
        (Inches(-2), Inches(5.0), Inches(5), COLOR_HIGHLIGHT, 0.3),
    ]):
        circle = s.shapes.add_shape(MSO_SHAPE.OVAL, l, t, w, w)
        circle.fill.solid()
        circle.fill.fore_color.rgb = c
        circle.line.fill.background()

    # 主标题
    add_textbox(s, Inches(0.8), Inches(2.0),
                Inches(11.5), Inches(1.0),
                'DNN / LLM 分布式推理平台',
                size=44, bold=True,
                color=RGBColor(0xFF, 0xFF, 0xFF))
    # 副标题
    add_textbox(s, Inches(0.8), Inches(2.95),
                Inches(11.5), Inches(0.6),
                '需求调研 · 平台搭建 · 难点与机会',
                size=22, bold=False,
                color=RGBColor(0xCF, 0xDC, 0xEC))
    # 高亮线
    line = s.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(3.7),
        Inches(2.0), Inches(0.06))
    line.fill.solid()
    line.fill.fore_color.rgb = COLOR_HIGHLIGHT
    line.line.fill.background()
    # 关键词
    add_textbox(s, Inches(0.8), Inches(4.0),
                Inches(11.5), Inches(0.5),
                '面向 边缘 / 卫星 / 空天地一体化（SAGIN） 协同推理',
                size=18, color=RGBColor(0xFF, 0xC1, 0x68))
    # 底部
    add_textbox(s, Inches(0.8), Inches(6.6),
                Inches(11.5), Inches(0.4),
                '组会汇报 · 2026 年 4 月 25 日',
                size=14, color=RGBColor(0xCF, 0xDC, 0xEC))
    add_textbox(s, Inches(0.8), Inches(6.9),
                Inches(11.5), Inches(0.4),
                '基于 SynerGist (Partition_Scheduling) 项目',
                size=12, color=RGBColor(0x9D, 0xB6, 0xD0))


# =========================================================
# Slide 2: 议程
# =========================================================
def slide_agenda(page_no, total):
    s = blank_slide()
    add_title_band(s, '汇报提纲', 'Agenda')

    items = [
        ('01', '背景与动机', 'AI 模型规模 vs 边缘资源，模型分割的必要性'),
        ('02', '应用场景', '端边云、卫星协同、SAGIN 灾害救援、LLM 推理'),
        ('03', '关键技术栈', '分割维度、调度算法、通信、LLM 专属技术'),
        ('04', '现有基础', 'SynerGist / Partition_Scheduling 项目快照'),
        ('05', '文献实验平台综述', '硬件 / 软件 / 数据集 / 网络对照'),
        ('06', '平台需求', '功能、硬件、模型、数据集'),
        ('07', '搭建难点', '系统、模型、算法三个维度'),
        ('08', '论文复现的坑', '代码、硬件、数据、训练、SAGIN 仿真'),
        ('09', '做研究的坑', '工程、建模、LLM、评估'),
        ('10', '路线图与讨论', 'PoC → SAGIN → 论文'),
    ]
    cols = 2
    rows = 5
    cell_w = Inches(6.0)
    cell_h = Inches(1.05)
    start_x = Inches(0.6)
    start_y = Inches(1.2)
    for i, (no, t, sub) in enumerate(items):
        col = i % cols
        row = i // cols
        x = start_x + col * (cell_w + Inches(0.2))
        y = start_y + row * (cell_h + Inches(0.15))
        # 编号
        circle = s.shapes.add_shape(
            MSO_SHAPE.OVAL, x, y, Inches(0.85), Inches(0.85))
        circle.fill.solid()
        circle.fill.fore_color.rgb = COLOR_ACCENT
        circle.line.fill.background()
        tb = circle.text_frame
        tb.text = ''
        p = tb.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        set_run(p.add_run(), no, size=20, bold=True,
                color=RGBColor(0xFF, 0xFF, 0xFF))
        # 标题
        add_textbox(s, x + Inches(1.0), y + Inches(0.05),
                    cell_w - Inches(1.1), Inches(0.5),
                    t, size=18, bold=True, color=COLOR_PRIMARY)
        # 副标题
        add_textbox(s, x + Inches(1.0), y + Inches(0.5),
                    cell_w - Inches(1.1), Inches(0.5),
                    sub, size=12, color=COLOR_MUTED)

    add_footer(s, page_no, total)


# =========================================================
# Slide 3: 背景与动机
# =========================================================
def slide_background(page_no, total):
    s = blank_slide()
    add_title_band(s, '为什么需要模型分割？', '从 AI 模型规模 vs 边缘资源说起')

    # 左侧：四个驱动力
    drivers = [
        ('模型规模爆炸', 'GPT-4 ~1.8T 参数；Llama-3-70B 显存 ≥ 140 GB；端侧根本放不下',
         COLOR_RED),
        ('实时性 & 隐私', '自动驾驶/灾害救援/AIoT 对时延、隐私、带宽要求严格',
         COLOR_HIGHLIGHT),
        ('基础设施变革', 'LEO 卫星（Starlink/OneWeb）+ HAP/UAV + 5G/6G → SAGIN',
         COLOR_ACCENT),
        ('内存墙 & 通信墙', '中间张量 / KV-Cache 在窄带链路把"算力瓶颈"变"通信瓶颈"',
         COLOR_GREEN),
    ]
    for i, (t, b, c) in enumerate(drivers):
        x = Inches(0.5)
        y = Inches(1.1) + i * Inches(1.4)
        # 左竖条
        bar = s.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, x, y, Inches(0.12), Inches(1.2))
        bar.fill.solid()
        bar.fill.fore_color.rgb = c
        bar.line.fill.background()
        add_textbox(s, x + Inches(0.25), y,
                    Inches(6.5), Inches(0.5),
                    t, size=18, bold=True, color=COLOR_PRIMARY)
        add_textbox(s, x + Inches(0.25), y + Inches(0.5),
                    Inches(6.5), Inches(0.7),
                    b, size=13, color=COLOR_TEXT)

    # 右侧：核心思想图
    rx = Inches(7.6)
    ry = Inches(1.1)
    add_textbox(s, rx, ry, Inches(5.2), Inches(0.4),
                '核心思想：把模型切到多节点协同执行',
                size=15, bold=True, color=COLOR_PRIMARY)
    # 三个节点
    boxes = [
        ('端侧 UE', '量化 SLM\nPhi-3-mini', COLOR_HIGHLIGHT),
        ('边缘 / HAP', '中等模型\nLlama-3-8B', COLOR_ACCENT),
        ('卫星 / 云', '大模型 / MoE\nDeepSeek-V3', COLOR_PRIMARY),
    ]
    bx = rx
    by = ry + Inches(0.6)
    bw = Inches(1.6)
    bh = Inches(1.2)
    gap = Inches(0.15)
    for i, (t, sub, c) in enumerate(boxes):
        x = bx + i * (bw + gap)
        rect = s.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE, x, by, bw, bh)
        rect.adjustments[0] = 0.15
        rect.fill.solid()
        rect.fill.fore_color.rgb = c
        rect.line.fill.background()
        tf = rect.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        set_run(p.add_run(), t, size=14, bold=True,
                color=RGBColor(0xFF, 0xFF, 0xFF))
        p2 = tf.add_paragraph()
        p2.alignment = PP_ALIGN.CENTER
        set_run(p2.add_run(), sub, size=10,
                color=RGBColor(0xEC, 0xF2, 0xF9))

    # 箭头
    for i in range(2):
        ax = bx + (i + 1) * bw + i * gap
        arrow = s.shapes.add_shape(
            MSO_SHAPE.RIGHT_ARROW,
            ax, by + Inches(0.5),
            gap, Inches(0.2))
        arrow.fill.solid()
        arrow.fill.fore_color.rgb = COLOR_MUTED
        arrow.line.fill.background()

    # 下方说明
    add_textbox(s, rx, by + bh + Inches(0.3),
                Inches(5.2), Inches(0.4),
                '中间激活 / Token / 梯度 通过 RF / FSO / ISL 传输',
                size=12, color=COLOR_MUTED, align=PP_ALIGN.CENTER)

    # 三利益
    add_textbox(s, rx, by + bh + Inches(0.85),
                Inches(5.2), Inches(0.4),
                '收益', size=14, bold=True, color=COLOR_HIGHLIGHT)
    benefits = [
        '✓ 算力 / 显存 / 能耗 按节点能力分摊',
        '✓ 就近处理 → 减少回传 / 保护隐私 / 缩短时延',
        '✓ 充分利用边缘 / 卫星 海量闲置算力',
    ]
    for i, b in enumerate(benefits):
        add_textbox(s, rx, by + bh + Inches(1.25) + i * Inches(0.35),
                    Inches(5.2), Inches(0.35),
                    b, size=12, color=COLOR_TEXT)

    add_footer(s, page_no, total)


# =========================================================
# Slide 4: 应用场景
# =========================================================
def slide_scenarios(page_no, total):
    s = blank_slide()
    add_title_band(s, '平台典型应用场景',
                   '从 IoT 端边协同 → 到 LLM 端侧 → 到 SAGIN 灾害救援')

    scenarios = [
        ('① 端边云协同 DNN 推理',
         '移动 / IoT / MEC 场景下细粒度分割',
         'JointDNN, MoEI, Li 2024, DeepSlicing', COLOR_ACCENT),
        ('② 多边缘节点流水线推理',
         '多 Pi/Jetson 协同；DAG 调度；流水线气泡管理',
         'DeepSlicing, HiDP, PMP, POPS', COLOR_ACCENT),
        ('③ 早退 / 多出口推理',
         '按置信度提前退出；时延-精度 trade-off',
         'BranchyNet, SatCooper', COLOR_GREEN),
        ('④ 卫星-地面协同推理',
         '遥感 / 对地观测；星地链路 / 太阳能能耗',
         'SLICE, SatCooper, Qiao 2025, APT-SAT', COLOR_HIGHLIGHT),
        ('⑤ SAGIN 灾害救援（重点）',
         '应急通信弹性；隐私保护；多模态请求',
         '本组 251225 + LLM-DRL Li 2025', COLOR_RED),
        ('⑥ 分布式 LLM 推理',
         'Tensor Parallelism / AirComp / KV-Cache',
         'Communication-Eff Zhang 2025, Birds Zhu 2025', COLOR_PRIMARY),
        ('⑦ LLM-SLM 协同 + 模型缓存',
         '双时间尺度：缓存（慢）+ 卸载（快）',
         'LSCI Xu 2025', COLOR_PRIMARY),
        ('⑧ 在轨微调 / 自主导航',
         'UAV NaviSplit；星上 fine-tune',
         'NaviSplit, Plumridge 2025, Růžička 2023',
         COLOR_MUTED),
    ]

    cols = 4
    rows = 2
    card_w = Inches(3.05)
    card_h = Inches(2.55)
    start_x = Inches(0.4)
    start_y = Inches(1.1)
    gap_x = Inches(0.13)
    gap_y = Inches(0.18)

    for i, (t, b, ref, c) in enumerate(scenarios):
        col = i % cols
        row = i // cols
        x = start_x + col * (card_w + gap_x)
        y = start_y + row * (card_h + gap_y)
        add_card(s, x, y, card_w, card_h, t,
                 [b, '', f'代表工作：{ref}'],
                 color=c, title_size=14, body_size=11)

    add_footer(s, page_no, total)


# =========================================================
# Slide 5: 模型分割维度
# =========================================================
def slide_partition_dim(page_no, total):
    s = blank_slide()
    add_title_band(s, '关键技术 (1/3) · 模型分割维度', '层 / 张量 / 数据 / 专家 / 出口')

    dims = [
        ('Layer-wise / Pipeline',
         '按层切分，链式 or DAG\nVGG, ResNet, GoogLeNet',
         '本组 SynerGist；APT-SAT；DeepSlicing；Li 2024',
         COLOR_ACCENT),
        ('Tensor Parallel',
         '把矩阵 W ∈ ℝ^(d×d) 沿行/列切\nTransformer 注意力 / FFN',
         'Megatron 思想；Zhang 2025 (+AirComp)',
         COLOR_HIGHLIGHT),
        ('Data Parallel',
         '把输入 batch 切到多节点\n各执行同一份模型',
         'Edge AI; HiDP；分布式训练通用',
         COLOR_GREEN),
        ('Expert (MoE)',
         '路由给不同 Expert\n稀疏激活',
         'DeepSeek-V3; Mixtral; (展望)',
         COLOR_PRIMARY),
        ('Early Exit / Multi-Exit',
         '前几层即可输出；置信度门控',
         'BranchyNet; SatCooper',
         COLOR_RED),
        ('Hierarchical / Multi-Level',
         '全局粗粒度 + 节点内 CPU/GPU 细粒度',
         'HiDP (DATE 2025); Tango',
         COLOR_MUTED),
    ]
    cols = 3
    card_w = Inches(4.05)
    card_h = Inches(2.6)
    start_x = Inches(0.4)
    start_y = Inches(1.1)
    gap_x = Inches(0.15)
    gap_y = Inches(0.2)
    for i, (t, b1, b2, c) in enumerate(dims):
        col = i % cols
        row = i // cols
        x = start_x + col * (card_w + gap_x)
        y = start_y + row * (card_h + gap_y)
        add_card(s, x, y, card_w, card_h, t,
                 [b1, '', f'代表工作：{b2}'],
                 color=c, title_size=15, body_size=12)

    add_footer(s, page_no, total)


# =========================================================
# Slide 6: 调度与决策算法
# =========================================================
def slide_algo(page_no, total):
    s = blank_slide()
    add_title_band(s, '关键技术 (2/3) · 卸载与调度算法',
                   '启发式 → 优化 → 博弈 → 强化学习')

    table_data = [
        ['算法类别', '代表方法', '代表论文', '优势', '局限'],
        ['启发式 / 贪心',
         '资源感知、负载方差最小化',
         'APT-SAT (Stage 2)',
         '复杂度低、易实现',
         '局部最优'],
        ['图搜索 / 关键路径',
         'AOE / CP / 剪枝',
         'PMP (Liao 2023)',
         '处理 DAG 依赖好',
         '搜索空间大'],
        ['整数规划 ILP / MILP',
         'GLPK / Gurobi 求解',
         'JointDNN; Birds in Cages',
         '理论最优',
         '不可在线、规模受限'],
        ['博弈论',
         '完全信息离线分析',
         'MoEI (Liu 2024)',
         '建模理性 agent',
         '需均衡存在性证明'],
        ['强化学习',
         'PPO / SAC / DQN / A3C',
         '本组；APT-SAT；Li 2024；MoEI',
         '在线、自适应',
         '训练慢、奖励噪声'],
        ['消息传递 BP',
         'Belief Propagation',
         'LSCI (Xu 2025)',
         '低复杂度、分布式',
         '收敛性需保证'],
        ['联邦学习',
         'FL-PPO',
         '本组 RL_multiple; FL-PPO',
         '隐私 + 多 agent 协同',
         '同步开销'],
    ]

    rows = len(table_data)
    cols = len(table_data[0])
    tbl_left = Inches(0.4)
    tbl_top = Inches(1.1)
    tbl_w = Inches(12.5)
    tbl_h = Inches(5.6)
    tbl = s.shapes.add_table(rows, cols, tbl_left, tbl_top, tbl_w, tbl_h).table
    # 列宽
    widths = [Inches(1.7), Inches(2.2), Inches(2.6), Inches(3.0), Inches(3.0)]
    for i, w in enumerate(widths):
        tbl.columns[i].width = w
    # 行高
    tbl.rows[0].height = Inches(0.55)
    for i in range(1, rows):
        tbl.rows[i].height = Inches(0.72)

    for r in range(rows):
        for c in range(cols):
            cell = tbl.cell(r, c)
            cell.text = ''
            tf = cell.text_frame
            tf.word_wrap = True
            tf.margin_left = Inches(0.08)
            tf.margin_right = Inches(0.08)
            tf.margin_top = Inches(0.04)
            tf.margin_bottom = Inches(0.04)
            p = tf.paragraphs[0]
            p.alignment = PP_ALIGN.LEFT
            run = p.add_run()
            if r == 0:
                set_run(run, table_data[r][c], size=13, bold=True,
                        color=RGBColor(0xFF, 0xFF, 0xFF))
                cell.fill.solid()
                cell.fill.fore_color.rgb = COLOR_PRIMARY
            else:
                set_run(run, table_data[r][c], size=11, color=COLOR_TEXT)
                cell.fill.solid()
                cell.fill.fore_color.rgb = (
                    RGBColor(0xFF, 0xFF, 0xFF) if r % 2 == 1 else COLOR_LIGHT)

    add_footer(s, page_no, total)


# =========================================================
# Slide 7: LLM 专属技术
# =========================================================
def slide_llm_tech(page_no, total):
    s = blank_slide()
    add_title_band(s, '关键技术 (3/3) · LLM 分布式推理专属问题',
                   '量化 / KV-Cache / Two-Stage / Continuous Batching')

    # 左：Transformer 推理两阶段
    add_textbox(s, Inches(0.5), Inches(1.0),
                Inches(6.2), Inches(0.4),
                '① Transformer 推理两阶段', size=18, bold=True,
                color=COLOR_PRIMARY)
    # Prefill 卡
    p1 = add_rect(s, Inches(0.5), Inches(1.5), Inches(2.95), Inches(2.2),
                  fill=COLOR_LIGHT)
    add_textbox(s, Inches(0.6), Inches(1.55), Inches(2.85), Inches(0.4),
                'Prefill 阶段', size=15, bold=True, color=COLOR_HIGHLIGHT)
    p1_text = [
        '一次处理整个 Prompt',
        'O(L²) 算力主导',
        '算力瓶颈 → 适合切层并行',
        '中间激活大：B×L×d',
    ]
    for i, t in enumerate(p1_text):
        add_textbox(s, Inches(0.6), Inches(1.95) + i * Inches(0.42),
                    Inches(2.85), Inches(0.4),
                    '• ' + t, size=11, color=COLOR_TEXT)
    # Decoding 卡
    p2 = add_rect(s, Inches(3.65), Inches(1.5), Inches(2.95), Inches(2.2),
                  fill=COLOR_LIGHT)
    add_textbox(s, Inches(3.75), Inches(1.55), Inches(2.85), Inches(0.4),
                'Decoding 阶段', size=15, bold=True, color=COLOR_GREEN)
    p2_text = [
        '逐 token 自回归生成',
        '内存带宽主导',
        '通信瓶颈 → 适合张量并行',
        'KV-Cache 不断增长',
    ]
    for i, t in enumerate(p2_text):
        add_textbox(s, Inches(3.75), Inches(1.95) + i * Inches(0.42),
                    Inches(2.85), Inches(0.4),
                    '• ' + t, size=11, color=COLOR_TEXT)

    # 左：② 关键优化技术
    add_textbox(s, Inches(0.5), Inches(3.85),
                Inches(6.2), Inches(0.4),
                '② 关键优化技术', size=18, bold=True,
                color=COLOR_PRIMARY)
    techs = [
        ('量化', 'INT8 / INT4 / GPTQ / AWQ；Phi-3-mini-4bit'),
        ('KV-Cache 管理', 'PagedAttention / vLLM 显存碎片整理'),
        ('Continuous Batching', 'Iteration-level 调度，避免 padding'),
        ('AirComp', '空中计算做 all-reduce，省通信开销'),
        ('张量切片', 'Megatron 风格，行/列切；TP-rank'),
    ]
    for i, (t, b) in enumerate(techs):
        y = Inches(4.3) + i * Inches(0.5)
        add_textbox(s, Inches(0.5), y, Inches(1.5), Inches(0.45),
                    t, size=12, bold=True, color=COLOR_ACCENT)
        add_textbox(s, Inches(2.0), y, Inches(4.7), Inches(0.45),
                    b, size=11, color=COLOR_TEXT)

    # 右：③ DAG-Driven Prompt 拆解
    rx = Inches(7.0)
    add_textbox(s, rx, Inches(1.0),
                Inches(6.0), Inches(0.4),
                '③ DAG-Driven Prompt 任务拆解（重点研究方向）', size=16, bold=True,
                color=COLOR_HIGHLIGHT)

    # Prompt 框
    pr = add_rect(s, rx, Inches(1.55),
                  Inches(6.0), Inches(0.7),
                  fill=COLOR_PRIMARY)
    tf = pr.text_frame
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.word_wrap = True
    tf.margin_left = Inches(0.15)
    p = tf.paragraphs[0]
    set_run(p.add_run(),
            'Prompt: 发现伤员，腿部骨折，请指导救援并通知最近医院',
            size=12, color=RGBColor(0xFF, 0xFF, 0xFF))

    # 箭头向下
    arr = s.shapes.add_shape(MSO_SHAPE.DOWN_ARROW,
                             rx + Inches(2.85), Inches(2.3),
                             Inches(0.3), Inches(0.3))
    arr.fill.solid()
    arr.fill.fore_color.rgb = COLOR_MUTED
    arr.line.fill.background()

    # 4 个子任务
    subs = [
        ('T1 图像分析\n伤情', COLOR_ACCENT),
        ('T2 急救指南\n生成', COLOR_GREEN),
        ('T3 路径规划\n医院通知', COLOR_HIGHLIGHT),
        ('T4 综合报告\n汇总', COLOR_RED),
    ]
    for i, (t, c) in enumerate(subs):
        sx = rx + Inches(0.05) + i * Inches(1.5)
        rect = s.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE, sx, Inches(2.7),
            Inches(1.4), Inches(1.0))
        rect.adjustments[0] = 0.15
        rect.fill.solid()
        rect.fill.fore_color.rgb = c
        rect.line.fill.background()
        tf = rect.text_frame
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        set_run(p.add_run(), t, size=11, bold=True,
                color=RGBColor(0xFF, 0xFF, 0xFF))

    # 节点分配
    add_textbox(s, rx, Inches(3.85),
                Inches(6.0), Inches(0.4),
                '↓ 路由到异构节点（基于复杂度 / 隐私 / 资源）',
                size=12, color=COLOR_MUTED, align=PP_ALIGN.CENTER)
    nodes = [
        ('UE 端\n4-bit SLM', COLOR_HIGHLIGHT),
        ('UAV/HAP\nLlama-8B', COLOR_ACCENT),
        ('LEO 卫星\nMoE 大模型', COLOR_PRIMARY),
    ]
    for i, (t, c) in enumerate(nodes):
        sx = rx + Inches(0.3) + i * Inches(2.0)
        rect = s.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE, sx, Inches(4.4),
            Inches(1.7), Inches(0.9))
        rect.adjustments[0] = 0.15
        rect.fill.solid()
        rect.fill.fore_color.rgb = c
        rect.line.fill.background()
        rect.line.color.rgb = COLOR_PRIMARY
        rect.line.width = Pt(1.2)
        tf = rect.text_frame
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        set_run(p.add_run(), t, size=11, bold=True,
                color=RGBColor(0xFF, 0xFF, 0xFF))

    # 关键挑战
    add_textbox(s, rx, Inches(5.5),
                Inches(6.0), Inches(0.4),
                '关键挑战', size=14, bold=True, color=COLOR_RED)
    chal = [
        '① Prompt → DAG 自动构建（AI Agent）',
        '② DAG 节点的语义复杂度 / 隐私敏感度 建模',
        '③ 节点能力评分 vs 任务复杂度匹配',
        '④ 中间张量大 → 通信瓶颈',
    ]
    for i, t in enumerate(chal):
        add_textbox(s, rx, Inches(5.9) + i * Inches(0.32),
                    Inches(6.0), Inches(0.32),
                    t, size=11, color=COLOR_TEXT)

    add_footer(s, page_no, total)


# =========================================================
# Slide 8: 现有基础 SynerGist
# =========================================================
def slide_synergist(page_no, total):
    s = blank_slide()
    add_title_band(s, '我们的现有基础：SynerGist / Partition_Scheduling',
                   '已实现 VGG5 链式分割 + PPO 自动分割')

    # 左：架构图
    add_textbox(s, Inches(0.4), Inches(1.0),
                Inches(7.0), Inches(0.4),
                '系统架构（链式推理 + RL 自动分割）',
                size=16, bold=True, color=COLOR_PRIMARY)

    # Server 框
    srv = s.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(0.4), Inches(1.5), Inches(2.5), Inches(1.6))
    srv.adjustments[0] = 0.1
    srv.fill.solid()
    srv.fill.fore_color.rgb = COLOR_PRIMARY
    srv.line.fill.background()
    tf = srv.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    set_run(p.add_run(), 'Server\n(协调端)', size=14, bold=True,
            color=RGBColor(0xFF, 0xFF, 0xFF))
    items = [
        '采集资源 (Paramiko)',
        '计算分割点',
        'PPO 训练',
        '加载 CIFAR-10',
    ]
    for i, t in enumerate(items):
        p = tf.add_paragraph()
        p.alignment = PP_ALIGN.CENTER
        set_run(p.add_run(), '• ' + t, size=10,
                color=RGBColor(0xCF, 0xDC, 0xEC))

    # 三个 Client
    clients = [
        ('Client 1', '层 0~1\nConv+Pool'),
        ('Client 2', '层 2~3\nConv+Pool'),
        ('Client 3', '层 4~6\nConv+Dense'),
    ]
    for i, (t, sub) in enumerate(clients):
        x = Inches(3.3) + i * Inches(1.4)
        rect = s.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE,
            x, Inches(1.8), Inches(1.2), Inches(1.0))
        rect.adjustments[0] = 0.15
        rect.fill.solid()
        rect.fill.fore_color.rgb = COLOR_ACCENT
        rect.line.fill.background()
        tf = rect.text_frame
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        set_run(p.add_run(), t, size=12, bold=True,
                color=RGBColor(0xFF, 0xFF, 0xFF))
        p = tf.add_paragraph()
        p.alignment = PP_ALIGN.CENTER
        set_run(p.add_run(), sub, size=9,
                color=RGBColor(0xEC, 0xF2, 0xF9))

    # 箭头
    arr = s.shapes.add_shape(
        MSO_SHAPE.RIGHT_ARROW,
        Inches(2.93), Inches(2.15),
        Inches(0.3), Inches(0.25))
    arr.fill.solid()
    arr.fill.fore_color.rgb = COLOR_HIGHLIGHT
    arr.line.fill.background()
    for i in range(2):
        ax = Inches(4.5) + i * Inches(1.4)
        a = s.shapes.add_shape(
            MSO_SHAPE.RIGHT_ARROW, ax, Inches(2.15),
            Inches(0.18), Inches(0.25))
        a.fill.solid()
        a.fill.fore_color.rgb = COLOR_HIGHLIGHT
        a.line.fill.background()

    # 协议说明
    add_textbox(s, Inches(0.4), Inches(3.2),
                Inches(7.0), Inches(0.4),
                'TCP Socket + Pickle 链式传递 (4字节头 + 序列化体)',
                size=11, color=COLOR_MUTED)

    # 关键技术栈
    add_textbox(s, Inches(0.4), Inches(3.8),
                Inches(7.0), Inches(0.4),
                '关键技术栈', size=14, bold=True, color=COLOR_PRIMARY)
    stacks = [
        ('PyTorch', 'VGG5 7 层手写'),
        ('PPO', 'Actor-Critic 自动分割'),
        ('状态衍生', '滑窗均值+差分 / IAF'),
        ('KMeans', '客户端聚类分组'),
        ('Paramiko SSH', 'CPU/内存/网络采集'),
    ]
    for i, (t, sub) in enumerate(stacks):
        x = Inches(0.4) + (i % 3) * Inches(2.4)
        y = Inches(4.25) + (i // 3) * Inches(0.9)
        rect = add_rect(s, x, y, Inches(2.2), Inches(0.75),
                        fill=COLOR_LIGHT)
        add_textbox(s, x + Inches(0.1), y + Inches(0.05),
                    Inches(2.0), Inches(0.35),
                    t, size=12, bold=True, color=COLOR_ACCENT)
        add_textbox(s, x + Inches(0.1), y + Inches(0.4),
                    Inches(2.0), Inches(0.35),
                    sub, size=10, color=COLOR_TEXT)

    # 右：痛点 - 待升级
    add_textbox(s, Inches(8.0), Inches(1.0),
                Inches(5.0), Inches(0.4),
                '现状痛点 → 升级方向',
                size=16, bold=True, color=COLOR_HIGHLIGHT)

    rows = [
        ('模型', 'VGG5 (CIFAR-10)',
         'VGG19/ResNet50 + Llama2-7B/Phi-3'),
        ('分割', '链式 + 资源感知',
         'DAG + 张量并行 + 多出口'),
        ('节点', '4 台固定 IP',
         'Docker Compose + YAML 拓扑'),
        ('网络', '局域网，无注入',
         'Linux TC + Hypatia 卫星仿真'),
        ('调度', '资源感知 + PPO',
         '+ SAC/A3C/ILP/贪心 多基线'),
        ('任务', '单 DNN 推理',
         'DAG 任务流 + Prompt→DAG'),
        ('LLM', '不支持',
         'TP / 量化 / KV-Cache 管理'),
    ]
    rx = Inches(8.0)
    for i, (k, now, future) in enumerate(rows):
        y = Inches(1.5) + i * Inches(0.66)
        # 行背景
        bg = add_rect(s, rx, y, Inches(5.0), Inches(0.6),
                      fill=COLOR_LIGHT if i % 2 == 0 else
                      RGBColor(0xFF, 0xFF, 0xFF))
        add_textbox(s, rx + Inches(0.1), y + Inches(0.05),
                    Inches(0.7), Inches(0.55),
                    k, size=12, bold=True,
                    color=COLOR_PRIMARY,
                    anchor=MSO_ANCHOR.MIDDLE)
        add_textbox(s, rx + Inches(0.85), y + Inches(0.05),
                    Inches(1.7), Inches(0.55),
                    now, size=10, color=COLOR_RED,
                    anchor=MSO_ANCHOR.MIDDLE)
        # arrow
        a = s.shapes.add_shape(
            MSO_SHAPE.RIGHT_ARROW,
            rx + Inches(2.6), y + Inches(0.18),
            Inches(0.2), Inches(0.22))
        a.fill.solid()
        a.fill.fore_color.rgb = COLOR_HIGHLIGHT
        a.line.fill.background()
        add_textbox(s, rx + Inches(2.85), y + Inches(0.05),
                    Inches(2.1), Inches(0.55),
                    future, size=10, color=COLOR_GREEN,
                    bold=True,
                    anchor=MSO_ANCHOR.MIDDLE)

    add_footer(s, page_no, total)


# =========================================================
# Slide 9: 文献实验平台对照（DNN）
# =========================================================
def slide_lit_dnn(page_no, total):
    s = blank_slide()
    add_title_band(s, '文献实验平台对照 (1/2) · DNN 模型分割',
                   '硬件 / 软件 / 模型 / 数据集 / 网络')

    headers = ['论文', 'Testbed', '软件', '模型', '数据集', '网络']
    rows_data = [
        ['DeepSlicing\n(Zhang 2021)', '8×Raspberry Pi\n异构集群',
         'PyTorch', 'GoogLeNet, ResNet', 'ImageNet 子集', '局域网'],
        ['JointDNN\n(Eshratifar 2021)', '移动+云仿真',
         'ILP (GLPK)', 'AlexNet/VGG16/ResNet/NiN', 'Benchmark 集',
         'Wi-Fi/3G/4G LTE'],
        ['MoEI\n(Liu 2024)', '3 嵌入式 + 4 阿里云 GPU',
         'PyTorch + Aliyun', '4 类 DNN', 'Lumos5G',
         '5G 真实测量'],
        ['HiDP\n(Taufique 2025)', '商用异构边缘\n(CPU/GPU/NPU)',
         '默认框架', 'ResNet152/VGG19/Inception/EffNet', '—',
         '局域网'],
        ['POPS\n(Yan 2025)', '多端点 DAG 仿真',
         'Python + RL', '4 DNN benchmark', '—',
         '1.1/5.85/18.88 Mbps'],
        ['Li 2024\nFine-grained', 'MEC 仿真',
         'Multi-task A3C', 'DNN blocks', '—',
         '异构 MEC'],
        ['BranchyNet\n(2017)', 'GPU 服务器',
         'Caffe / Chainer', 'LeNet/AlexNet/ResNet',
         'MNIST/CIFAR/SVHN', '—'],
        ['PMP\n(Liao 2023)', '1 云 + 6 边缘',
         '—', 'CNN', '—', 'AOE 关键路径'],
    ]

    rows = len(rows_data) + 1
    cols = len(headers)
    tbl_left = Inches(0.4)
    tbl_top = Inches(1.05)
    tbl_w = Inches(12.5)
    tbl_h = Inches(5.7)
    tbl = s.shapes.add_table(rows, cols, tbl_left, tbl_top, tbl_w, tbl_h).table
    widths = [Inches(1.6), Inches(1.9), Inches(1.7), Inches(2.6),
              Inches(2.3), Inches(2.4)]
    for i, w in enumerate(widths):
        tbl.columns[i].width = w
    tbl.rows[0].height = Inches(0.5)
    for i in range(1, rows):
        tbl.rows[i].height = Inches(0.65)

    for c, h in enumerate(headers):
        cell = tbl.cell(0, c)
        cell.text = ''
        tf = cell.text_frame
        tf.margin_left = Inches(0.06)
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.LEFT
        set_run(p.add_run(), h, size=12, bold=True,
                color=RGBColor(0xFF, 0xFF, 0xFF))
        cell.fill.solid()
        cell.fill.fore_color.rgb = COLOR_PRIMARY

    for r, row in enumerate(rows_data, start=1):
        for c, val in enumerate(row):
            cell = tbl.cell(r, c)
            cell.text = ''
            tf = cell.text_frame
            tf.word_wrap = True
            tf.margin_left = Inches(0.06)
            tf.margin_right = Inches(0.06)
            p = tf.paragraphs[0]
            p.alignment = PP_ALIGN.LEFT
            set_run(p.add_run(), val, size=10, color=COLOR_TEXT)
            cell.fill.solid()
            cell.fill.fore_color.rgb = (
                RGBColor(0xFF, 0xFF, 0xFF) if r % 2 == 1 else COLOR_LIGHT)

    add_footer(s, page_no, total)


# =========================================================
# Slide 10: 文献实验平台对照（卫星 / LLM）
# =========================================================
def slide_lit_sat_llm(page_no, total):
    s = blank_slide()
    add_title_band(s, '文献实验平台对照 (2/2) · 卫星协同 + LLM 推理',
                   '空天地场景 + 大模型分布式')

    headers = ['论文', '场景', 'Testbed', '软件', '模型', '关键链路']
    rows_data = [
        ['APT-SAT\n(Peng 2026)', '卫星协同 DNN',
         'CPU 服务器 i5 / 16GB DDR5\n+ N×N 卫星仿真',
         'Python + SAC RL',
         'ResNet101 / VGG19',
         '卫星距离 < D_max'],
        ['SLICE\n(Chen 2025)', '星地协同节能',
         'COTS 卫星硬件测量',
         '层能耗建模',
         '多 DNN', '太阳能 + 星地链路'],
        ['SatCooper\n(Zhang 2025)', '多轨道协同',
         'LEO+MEO 仿真 + COTS',
         'DDQN',
         '多出口 DNN', '激光 ISL'],
        ['Qiao 2025', '在轨遥感推理',
         'LEO 计算卫星仿真',
         '非线性求解 + SA',
         'DNN', '激光终端'],
        ['Comm.-Eff LLM\n(Zhang 2025)', '端侧 LLM',
         '多天线模拟',
         '—', 'Tensor Parallel LLM',
         '无线多址 + AirComp'],
        ['Beyond Cloud\n(Zhang 2025)', '边缘 LLM',
         '异构边缘仿真',
         'NP-hard 调度',
         'Transformer Decoder LLM',
         '边缘资源约束'],
        ['Birds in Cages\n(Zhu 2025)', '分布式 LLM',
         '仿真',
         '二元整数规划',
         'Decode-only LLM', '边缘协作'],
        ['LSCI\n(Xu 2025)', 'LLM-SLM 协同',
         'MEC 仿真',
         '双时间尺度 + BP',
         'LLM + SLM', 'MEC 网络'],
    ]

    rows = len(rows_data) + 1
    cols = len(headers)
    tbl_left = Inches(0.4)
    tbl_top = Inches(1.05)
    tbl_w = Inches(12.5)
    tbl_h = Inches(5.7)
    tbl = s.shapes.add_table(rows, cols, tbl_left, tbl_top, tbl_w, tbl_h).table
    widths = [Inches(1.5), Inches(1.5), Inches(2.4), Inches(2.0),
              Inches(2.4), Inches(2.7)]
    for i, w in enumerate(widths):
        tbl.columns[i].width = w
    tbl.rows[0].height = Inches(0.5)
    for i in range(1, rows):
        tbl.rows[i].height = Inches(0.65)

    for c, h in enumerate(headers):
        cell = tbl.cell(0, c)
        cell.text = ''
        tf = cell.text_frame
        tf.margin_left = Inches(0.06)
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.LEFT
        set_run(p.add_run(), h, size=12, bold=True,
                color=RGBColor(0xFF, 0xFF, 0xFF))
        cell.fill.solid()
        cell.fill.fore_color.rgb = COLOR_PRIMARY

    for r, row in enumerate(rows_data, start=1):
        for c, val in enumerate(row):
            cell = tbl.cell(r, c)
            cell.text = ''
            tf = cell.text_frame
            tf.word_wrap = True
            tf.margin_left = Inches(0.06)
            tf.margin_right = Inches(0.06)
            p = tf.paragraphs[0]
            p.alignment = PP_ALIGN.LEFT
            set_run(p.add_run(), val, size=10, color=COLOR_TEXT)
            cell.fill.solid()
            cell.fill.fore_color.rgb = (
                RGBColor(0xFF, 0xFF, 0xFF) if r % 2 == 1 else COLOR_LIGHT)

    # 共性结论
    add_textbox(s, Inches(0.4), Inches(6.85),
                Inches(12.5), Inches(0.4),
                '共性观察：① PyTorch 主流；② 多 VM/Docker 仿真常见；'
                '③ Linux TC 注入网络条件；④ Ubuntu 20.04/22.04；'
                '⑤ 卫星端用 STK / Hypatia / 自研轨道仿真',
                size=12, color=COLOR_HIGHLIGHT, bold=True)

    add_footer(s, page_no, total)


# =========================================================
# Slide 11: 平台需求 - 功能
# =========================================================
def slide_req_func(page_no, total):
    s = blank_slide()
    add_title_band(s, '平台需求 (1/2) · 功能模块清单',
                   '统一支持 DNN/LLM × 端边空星云 × 多种调度策略')

    headers = ['模块', '需求', '现状', '待开发']
    rows_data = [
        ['模型抽象层', 'PyTorch / ONNX / HuggingFace 自动 DAG',
         '仅手写 VGG5', 'torch.fx / transformers'],
        ['分割引擎', '链式 / DAG / 张量 / 早退多出口',
         '链式 + 资源感知', 'DAG 切分 + 张量切分'],
        ['节点抽象', '统一 Node API\n(Capability/Resource/Link)',
         'server_list 配置', 'YAML 拓扑 + 容器化'],
        ['通信层', 'TCP / gRPC / Pickle / Protobuf + TC 注入',
         'TCP + Pickle', 'gRPC + safetensors + TC'],
        ['资源采集', 'CPU/显存/带宽/电池/能耗',
         'Paramiko + nvidia-smi', 'tegrastats / RAPL / 能耗模型'],
        ['调度器', '启发式 / RL / ILP 可热插拔',
         'PPO + 资源感知', 'SAC / A3C / ILP / 贪心'],
        ['任务模型', '单 DNN → DAG 任务流',
         '单任务', 'DAG + Prompt→DAG (LLM agent)'],
        ['LLM 模块', 'Llama2-7B / Phi-3 张量并行',
         '无', 'accelerate / vllm / 自研 TP'],
        ['卫星仿真', 'LEO 拓扑 / 过境 / 星历',
         '无', 'Hypatia / Skyfield + TLE'],
        ['可视化', '训练曲线 / 节点占用 / 链路',
         'matplotlib 静态', 'TensorBoard / Streamlit'],
        ['实验管理', '配置版本化 / 可复现实验',
         'config.py', 'Hydra + MLflow'],
    ]

    rows = len(rows_data) + 1
    cols = len(headers)
    tbl_left = Inches(0.4)
    tbl_top = Inches(1.0)
    tbl_w = Inches(12.5)
    tbl_h = Inches(6.0)
    tbl = s.shapes.add_table(rows, cols, tbl_left, tbl_top, tbl_w, tbl_h).table
    widths = [Inches(1.7), Inches(3.6), Inches(2.7), Inches(4.5)]
    for i, w in enumerate(widths):
        tbl.columns[i].width = w
    tbl.rows[0].height = Inches(0.45)
    for i in range(1, rows):
        tbl.rows[i].height = Inches(0.49)

    for c, h in enumerate(headers):
        cell = tbl.cell(0, c)
        cell.text = ''
        tf = cell.text_frame
        tf.margin_left = Inches(0.06)
        p = tf.paragraphs[0]
        set_run(p.add_run(), h, size=13, bold=True,
                color=RGBColor(0xFF, 0xFF, 0xFF))
        cell.fill.solid()
        cell.fill.fore_color.rgb = COLOR_PRIMARY

    color_red = RGBColor(0xC1, 0x44, 0x2E)
    color_green = RGBColor(0x2E, 0x8B, 0x57)

    for r, row in enumerate(rows_data, start=1):
        for c, val in enumerate(row):
            cell = tbl.cell(r, c)
            cell.text = ''
            tf = cell.text_frame
            tf.word_wrap = True
            tf.margin_left = Inches(0.06)
            tf.margin_right = Inches(0.06)
            p = tf.paragraphs[0]
            color = COLOR_TEXT
            if c == 2:
                color = color_red
            elif c == 3:
                color = color_green
            set_run(p.add_run(), val, size=10, color=color,
                    bold=(c == 0))
            cell.fill.solid()
            cell.fill.fore_color.rgb = (
                RGBColor(0xFF, 0xFF, 0xFF) if r % 2 == 1 else COLOR_LIGHT)

    add_footer(s, page_no, total)


# =========================================================
# Slide 12: 平台需求 - 硬件/模型/数据集
# =========================================================
def slide_req_hw(page_no, total):
    s = blank_slide()
    add_title_band(s, '平台需求 (2/2) · 硬件 / 模型 / 数据集',
                   '从 PoC（单机多容器）到真实异构集群')

    # 左：硬件方案
    add_textbox(s, Inches(0.4), Inches(1.0),
                Inches(6.2), Inches(0.4),
                '硬件方案（建议 A → C 渐进）',
                size=16, bold=True, color=COLOR_PRIMARY)
    plans = [
        ('A. 单机多 VM/Docker', '1 台服务器 → N 容器',
         '✓ 成本低、可控；本组先例', '需 TC 注入', COLOR_GREEN),
        ('B. 真实异构集群', 'Pi 4 / Jetson Nano + 服务器',
         '✓ 真实异构、对论文', '部署复杂', COLOR_HIGHLIGHT),
        ('C. 混合方案 ★', '1 服务器 + 4 嵌入式 + STK/Hypatia',
         '✓ 真实 + 灵活', '工作量最大（终态）', COLOR_RED),
        ('D. 云 + 本地', '阿里云 GPU + 本地（参考 MoEI）',
         '✓ 论文对齐', '持续费用', COLOR_MUTED),
    ]
    for i, (t, d, p, c, col) in enumerate(plans):
        y = Inches(1.5) + i * Inches(1.05)
        bg = add_rect(s, Inches(0.4), y, Inches(6.2), Inches(0.95),
                      fill=COLOR_LIGHT)
        # 左色条
        bar = s.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, Inches(0.4), y, Inches(0.1), Inches(0.95))
        bar.fill.solid()
        bar.fill.fore_color.rgb = col
        bar.line.fill.background()
        add_textbox(s, Inches(0.6), y + Inches(0.05),
                    Inches(2.0), Inches(0.4),
                    t, size=13, bold=True, color=col)
        add_textbox(s, Inches(2.6), y + Inches(0.05),
                    Inches(4.0), Inches(0.4),
                    d, size=11, color=COLOR_TEXT)
        add_textbox(s, Inches(0.6), y + Inches(0.5),
                    Inches(3.0), Inches(0.4),
                    p, size=10, color=COLOR_GREEN)
        add_textbox(s, Inches(3.6), y + Inches(0.5),
                    Inches(3.0), Inches(0.4),
                    '✗ ' + c, size=10, color=COLOR_RED)

    # 右：模型清单
    add_textbox(s, Inches(7.0), Inches(1.0),
                Inches(6.0), Inches(0.4),
                '模型清单',
                size=16, bold=True, color=COLOR_PRIMARY)
    models = [
        ('CNN', 'VGG5 / VGG16 / VGG19 / ResNet50 / ResNet101', '现有 + 论文对齐',
         COLOR_ACCENT),
        ('检测', 'YOLOv5 / v8', '遥感、自动驾驶', COLOR_GREEN),
        ('Transformer', 'BERT-base, ViT-S', 'NLP / 视觉 Transformer',
         COLOR_HIGHLIGHT),
        ('LLM (SLM)', 'Phi-3-mini-3.8B / Qwen2.5-1.5B / Llama-3.2-1B',
         '端侧可跑', COLOR_PRIMARY),
        ('LLM (中)', 'Llama-2-7B / Llama-3-8B (4-bit)', '边缘 GPU', COLOR_RED),
        ('LLM (大)', 'Llama-2-13B / 70B', '仅卫星/云对比', COLOR_MUTED),
    ]
    for i, (k, m, u, col) in enumerate(models):
        y = Inches(1.5) + i * Inches(0.55)
        bg = add_rect(s, Inches(7.0), y, Inches(6.0), Inches(0.5),
                      fill=COLOR_LIGHT if i % 2 == 0 else
                      RGBColor(0xFF, 0xFF, 0xFF))
        bar = s.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, Inches(7.0), y, Inches(0.1), Inches(0.5))
        bar.fill.solid()
        bar.fill.fore_color.rgb = col
        bar.line.fill.background()
        add_textbox(s, Inches(7.2), y + Inches(0.05),
                    Inches(1.3), Inches(0.4),
                    k, size=11, bold=True, color=col)
        add_textbox(s, Inches(8.5), y + Inches(0.05),
                    Inches(3.2), Inches(0.4),
                    m, size=10, color=COLOR_TEXT)
        add_textbox(s, Inches(11.7), y + Inches(0.05),
                    Inches(1.3), Inches(0.4),
                    u, size=10, color=COLOR_MUTED)

    # 右下：数据集
    add_textbox(s, Inches(7.0), Inches(4.85),
                Inches(6.0), Inches(0.4),
                '数据集',
                size=16, bold=True, color=COLOR_PRIMARY)
    datasets = [
        ('视觉', 'CIFAR-10/100, ImageNet-1k, AID, NWPU-RESISC45'),
        ('LLM', 'WikiText-2 / -103, MMLU, HellaSwag'),
        ('移动性', 'Lumos5G (5G 带宽轨迹)'),
        ('SAGIN', '自构建 Prompt → DAG 救援数据集'),
    ]
    for i, (k, ds) in enumerate(datasets):
        y = Inches(5.3) + i * Inches(0.45)
        add_textbox(s, Inches(7.0), y, Inches(1.3), Inches(0.4),
                    k, size=11, bold=True, color=COLOR_HIGHLIGHT)
        add_textbox(s, Inches(8.3), y, Inches(4.7), Inches(0.4),
                    ds, size=10, color=COLOR_TEXT)

    add_footer(s, page_no, total)


# =========================================================
# Slide 13: 搭建难点
# =========================================================
def slide_difficulties(page_no, total):
    s = blank_slide()
    add_title_band(s, '平台搭建难点 · 三个层面',
                   '系统 / 模型 / 算法')

    sections = [
        ('系统层面', COLOR_RED, [
            ('节点异构', 'CPU/GPU/NPU 性能/显存/能耗差异巨大'),
            ('网络异构', '5G ~Gbps；卫星 Ka ~Mbps；FSO ISL ~Gbps'),
            ('拓扑动态', 'LEO 5–10 min 过境；UAV 移动；用户切换'),
            ('同步与气泡', '依赖 + 不均衡分配 → 流水线空闲'),
            ('资源采集', '远程低开销同步采集（SSH 不稳）'),
            ('多任务并发', 'DAG 间依赖与资源竞争'),
        ]),
        ('模型层面', COLOR_HIGHLIGHT, [
            ('DAG 解析', '从 PyTorch 自动抽取（torch.fx/ONNX）'),
            ('搜索空间爆炸', '多分割点组合 C(N,K) 巨大'),
            ('中间张量大', '早期卷积层激活 > 输入图本身'),
            ('LLM 显存碎片', 'KV-Cache 长度可变；prefill/decode 差异'),
            ('量化精度损失', '4-bit 端侧 vs FP16 云端'),
        ]),
        ('算法/评估层面', COLOR_ACCENT, [
            ('基线难复现', 'GO/NIDA/A3C/DPDQN 基线代码常不公开'),
            ('奖励稀疏方差大', '推理时延受瞬时网络/调度影响'),
            ('状态/动作空间', '连续 vs 离散；衍生表征'),
            ('真实-仿真鸿沟', 'TC 模拟 vs 真实卫星链路差异'),
        ]),
    ]
    cols = 3
    card_w = Inches(4.05)
    card_h = Inches(5.6)
    start_x = Inches(0.4)
    start_y = Inches(1.1)
    gap_x = Inches(0.15)
    for i, (title, color, items) in enumerate(sections):
        x = start_x + i * (card_w + gap_x)
        # 卡片底
        card = add_rect(s, x, start_y, card_w, card_h, fill=COLOR_LIGHT)
        # 顶部条
        bar = s.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, x, start_y, card_w, Inches(0.5))
        bar.fill.solid()
        bar.fill.fore_color.rgb = color
        bar.line.fill.background()
        # 标题
        tf = bar.text_frame
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        tf.margin_left = Inches(0.2)
        p = tf.paragraphs[0]
        set_run(p.add_run(), title, size=18, bold=True,
                color=RGBColor(0xFF, 0xFF, 0xFF))
        # 条目
        for j, (k, v) in enumerate(items):
            y = start_y + Inches(0.65) + j * Inches(0.78)
            # 编号
            circ = s.shapes.add_shape(
                MSO_SHAPE.OVAL, x + Inches(0.15), y,
                Inches(0.32), Inches(0.32))
            circ.fill.solid()
            circ.fill.fore_color.rgb = color
            circ.line.fill.background()
            tf = circ.text_frame
            tf.vertical_anchor = MSO_ANCHOR.MIDDLE
            p = tf.paragraphs[0]
            p.alignment = PP_ALIGN.CENTER
            set_run(p.add_run(), str(j + 1), size=11, bold=True,
                    color=RGBColor(0xFF, 0xFF, 0xFF))
            add_textbox(s, x + Inches(0.55), y - Inches(0.02),
                        card_w - Inches(0.7), Inches(0.4),
                        k, size=12, bold=True, color=color)
            add_textbox(s, x + Inches(0.55), y + Inches(0.32),
                        card_w - Inches(0.7), Inches(0.45),
                        v, size=10, color=COLOR_TEXT)

    add_footer(s, page_no, total)


# =========================================================
# Slide 14: 论文复现的坑
# =========================================================
def slide_repro(page_no, total):
    s = blank_slide()
    add_title_band(s, '论文复现可能遇到的问题',
                   '代码 / 硬件 / 数据 / 训练 / 卫星仿真')

    sections = [
        ('代码与开源', '⚠', COLOR_RED, [
            'IEEE 论文多数不公开实现 (APT-SAT, SatCooper, Li 2024)',
            '即便开源也常缺 baseline / 数据集脚本',
            '依赖陈旧 (PyTorch 1.x / TF 1.15)',
        ]),
        ('硬件与环境', '⚙', COLOR_HIGHLIGHT, [
            '论文用 Jetson TX2 / 卫星 COTS / 多 GPU，本地缺',
            'Llama-2-70B 需 ≥140GB 显存',
            '5G/LEO 真实环境无法获取，只能 TC 模拟',
            'nvidia-driver / 内核版本敏感',
        ]),
        ('数据与基准', '📊', COLOR_GREEN, [
            'APT-SAT 私有任务 200–300 KB；Lumos5G 需申请',
            '基线 (GO/NIDA/NPSO/DPDQN) 需自实现',
            '指标定义不统一：时延是否含队列/序列化',
        ]),
        ('训练与算法', '🧠', COLOR_ACCENT, [
            '超参数 (lr / replay buffer / 网络结构) 缺失',
            'RL 不收敛：状态归一化 / reward clip',
            '随机性大：3–5 seed 平均，给方差',
            '真实-仿真 gap：链路抖动、计算抖动建模',
        ]),
        ('卫星 / SAGIN 特有', '🛰', COLOR_PRIMARY, [
            '轨道仿真：用 Skyfield + 公开 TLE 替代 STK',
            '太阳能 / 电池模型：参数取自具体卫星',
            '激光 ISL / FSO：用 FSPL + 大气衰减解析模型',
            '过境窗口 5–10 min：必须加入约束',
        ]),
    ]
    cols = 3
    rows = 2
    card_w = Inches(4.05)
    card_h = Inches(2.85)
    start_x = Inches(0.4)
    start_y = Inches(1.05)
    gap_x = Inches(0.15)
    gap_y = Inches(0.18)
    for i, (title, icon, color, items) in enumerate(sections):
        col = i % cols
        row = i // cols
        x = start_x + col * (card_w + gap_x)
        y = start_y + row * (card_h + gap_y)
        # 卡片
        card = add_rect(s, x, y, card_w, card_h, fill=COLOR_LIGHT)
        # 顶部条
        bar = s.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, x, y, card_w, Inches(0.5))
        bar.fill.solid()
        bar.fill.fore_color.rgb = color
        bar.line.fill.background()
        # 图标
        add_textbox(s, x + Inches(0.15), y + Inches(0.04),
                    Inches(0.5), Inches(0.4),
                    icon, size=18, bold=True,
                    color=RGBColor(0xFF, 0xFF, 0xFF))
        # 标题
        add_textbox(s, x + Inches(0.65), y + Inches(0.07),
                    card_w - Inches(0.7), Inches(0.4),
                    title, size=15, bold=True,
                    color=RGBColor(0xFF, 0xFF, 0xFF))
        # 内容
        for j, t in enumerate(items):
            add_textbox(s, x + Inches(0.2), y + Inches(0.65) + j * Inches(0.45),
                        card_w - Inches(0.3), Inches(0.4),
                        '• ' + t, size=11, color=COLOR_TEXT)

    add_footer(s, page_no, total)


# =========================================================
# Slide 15: 做研究的坑
# =========================================================
def slide_research_pitfalls(page_no, total):
    s = blank_slide()
    add_title_band(s, '基于本平台开展研究 · 可能遇到的坑',
                   '工程 / 算法 / LLM / 评估')

    sections = [
        ('系统/工程', COLOR_RED, [
            'LLM 在端侧节点放不下（需 4-bit / GGUF）',
            '中间张量过大：1k token × 4096 × FP16 ≈ 32 MB/层；1Mbps 卫星链路 256 s 才能传完',
            'torch.fx 切片可能丢 inplace ops',
            'TC 不能模拟拓扑变化（链路出现/消失）',
            'Docker 回环 RTT~50µs，必须 netem 注入',
            'Pickle 跨版本不稳，改 safetensors / Protobuf',
            'SSH 16+ 节点采集易超时，改 push 模式',
        ]),
        ('算法/建模', COLOR_HIGHLIGHT, [
            'Prompt → DAG 自动生成需要 fine-tune',
            'RL 状态/动作空间组合爆炸 ⇒ 分层 RL + 动作掩码',
            '奖励噪声大 ⇒ EMA 平滑 / 多 episode 平均',
            '多目标 (时延/能耗/精度/隐私/完成率)：Pareto / 约束化 RL',
            '冷启动：借鉴 SatCooper "环境最近邻初始化"',
        ]),
        ('LLM 特有', COLOR_PRIMARY, [
            'Prefill vs Decoding 算/通比差异大 ⇒ 分阶段切分',
            'KV-Cache 一致性：TP 下需同步；切换分割点需迁移',
            '生成长度不确定（用 ECR/分布估计）',
            'Continuous Batching 与跨节点切分冲突',
            '量化+切分+压缩三层叠加：精度难解耦',
        ]),
        ('实验/评估', COLOR_GREEN, [
            '基线对比公平性：同平台 / 同拓扑 / 同数据集',
            '可复现 vs 真实：trace-driven 录回放',
            '能耗测量：tegrastats / RAPL / power meter',
            '可视化：多节点多链路时序图复杂',
            '计算预算：RL × 多基线 × 多种子 × 多模型 = 几百 GPU 小时',
        ]),
    ]
    cols = 2
    card_w = Inches(6.25)
    card_h = Inches(2.95)
    start_x = Inches(0.4)
    start_y = Inches(1.05)
    gap_x = Inches(0.15)
    gap_y = Inches(0.2)
    for i, (title, color, items) in enumerate(sections):
        col = i % cols
        row = i // cols
        x = start_x + col * (card_w + gap_x)
        y = start_y + row * (card_h + gap_y)
        card = add_rect(s, x, y, card_w, card_h, fill=COLOR_LIGHT)
        bar = s.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, x, y, card_w, Inches(0.45))
        bar.fill.solid()
        bar.fill.fore_color.rgb = color
        bar.line.fill.background()
        add_textbox(s, x + Inches(0.2), y + Inches(0.05),
                    card_w - Inches(0.3), Inches(0.4),
                    title, size=15, bold=True,
                    color=RGBColor(0xFF, 0xFF, 0xFF))
        for j, t in enumerate(items):
            add_textbox(s, x + Inches(0.2), y + Inches(0.55) + j * Inches(0.34),
                        card_w - Inches(0.3), Inches(0.32),
                        '• ' + t, size=10, color=COLOR_TEXT)

    add_footer(s, page_no, total)


# =========================================================
# Slide 16: 路线图
# =========================================================
def slide_roadmap(page_no, total):
    s = blank_slide()
    add_title_band(s, '建设路线图 · 三阶段',
                   '从扩展现有 → LLM/SAGIN → 论文研究')

    phases = [
        ('阶段 1\n4–6 周', 'PoC：扩展现有平台',
         COLOR_GREEN,
         [
             'VGG5 → VGG16/ResNet50',
             'torch.fx 自动 DAG 化',
             'Docker Compose 4–8 节点',
             'Linux TC 网络注入',
             'safetensors 替换 Pickle',
             'SAC / 贪心 / ILP 三 baseline',
         ]),
        ('阶段 2\n6–10 周', 'LLM 与 SAGIN',
         COLOR_HIGHLIGHT,
         [
             'Phi-3-mini / Llama-3.2-1B 流水线',
             'Qwen2.5-7B / Llama-3-8B 张量并行',
             'Skyfield + TLE LEO 卫星仿真',
             '复刻 APT-SAT / SLICE 实验',
             '加入 SAGIN 多链路（RF/FSO/ISL）',
         ]),
        ('阶段 3\n10+ 周', '研究与论文',
         COLOR_PRIMARY,
         [
             'DAG-Driven Prompt 任务建模',
             'TP + 通信压缩 + RL 联合优化',
             '数据集 + 工具开源',
             '投稿目标：TMC / TPDS / IoTJ / INFOCOM',
         ]),
    ]
    card_w = Inches(4.1)
    card_h = Inches(5.8)
    start_x = Inches(0.5)
    start_y = Inches(1.1)
    gap = Inches(0.2)
    for i, (phase, title, color, items) in enumerate(phases):
        x = start_x + i * (card_w + gap)
        # 大圆圈作为阶段编号
        circle = s.shapes.add_shape(
            MSO_SHAPE.OVAL, x + (card_w - Inches(1.4)) / 2, start_y,
            Inches(1.4), Inches(1.4))
        circle.fill.solid()
        circle.fill.fore_color.rgb = color
        circle.line.fill.background()
        tf = circle.text_frame
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        set_run(p.add_run(), phase, size=14, bold=True,
                color=RGBColor(0xFF, 0xFF, 0xFF))
        # 卡片
        card = add_rect(s, x, start_y + Inches(1.6),
                        card_w, card_h - Inches(1.6),
                        fill=COLOR_LIGHT, line=color)
        add_textbox(s, x + Inches(0.1), start_y + Inches(1.7),
                    card_w - Inches(0.2), Inches(0.5),
                    title, size=16, bold=True, color=color,
                    align=PP_ALIGN.CENTER)
        for j, t in enumerate(items):
            add_textbox(s, x + Inches(0.2),
                        start_y + Inches(2.3) + j * Inches(0.5),
                        card_w - Inches(0.4), Inches(0.5),
                        '✓ ' + t, size=12, color=COLOR_TEXT)

        # 箭头连接
        if i < len(phases) - 1:
            ax = x + card_w
            arr = s.shapes.add_shape(
                MSO_SHAPE.RIGHT_ARROW,
                ax, start_y + Inches(0.55),
                gap, Inches(0.3))
            arr.fill.solid()
            arr.fill.fore_color.rgb = COLOR_MUTED
            arr.line.fill.background()

    add_footer(s, page_no, total)


# =========================================================
# Slide 17: 讨论 Q&A
# =========================================================
def slide_qa(page_no, total):
    s = blank_slide()
    bg = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, SLIDE_W, SLIDE_H)
    bg.fill.solid()
    bg.fill.fore_color.rgb = COLOR_PRIMARY
    bg.line.fill.background()
    # 装饰圆
    for i, (l, t, w, c) in enumerate([
        (Inches(10.5), Inches(-2), Inches(7), COLOR_ACCENT),
        (Inches(-2.5), Inches(4.5), Inches(6), COLOR_HIGHLIGHT),
    ]):
        circle = s.shapes.add_shape(MSO_SHAPE.OVAL, l, t, w, w)
        circle.fill.solid()
        circle.fill.fore_color.rgb = c
        circle.line.fill.background()

    add_textbox(s, Inches(0.8), Inches(1.5),
                Inches(11.5), Inches(1.2),
                '讨论 & Q A', size=64, bold=True,
                color=RGBColor(0xFF, 0xFF, 0xFF))

    line = s.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(2.7),
        Inches(2.5), Inches(0.08))
    line.fill.solid()
    line.fill.fore_color.rgb = COLOR_HIGHLIGHT
    line.line.fill.background()

    add_textbox(s, Inches(0.8), Inches(3.0),
                Inches(11.5), Inches(0.5),
                '请大家就以下问题给出意见',
                size=20, bold=True,
                color=RGBColor(0xCF, 0xDC, 0xEC))

    qs = [
        '① 平台首要目标：CNN 调度 优先 还是 LLM 优先？',
        '② 硬件方案选 A 单机多容器 还是 C 真实异构？',
        '③ SAGIN 仿真用 Hypatia 还是 Skyfield+自研？',
        '④ 任务建模选 链式 DNN 还是 DAG 任务流？',
        '⑤ 论文方向锁定：模型分割算法 / 调度优化 / 通信压缩 ?',
    ]
    for i, q in enumerate(qs):
        add_textbox(s, Inches(0.8), Inches(3.7) + i * Inches(0.55),
                    Inches(11.5), Inches(0.5),
                    q, size=18,
                    color=RGBColor(0xFF, 0xC1, 0x68) if i % 2 == 0
                    else RGBColor(0xFF, 0xFF, 0xFF))

    add_textbox(s, Inches(0.8), SLIDE_H - Inches(0.6),
                Inches(11.5), Inches(0.4),
                'Thank You · 2026-04-25 组会',
                size=14, color=RGBColor(0x9D, 0xB6, 0xD0))


# =========================================================
# 生成所有幻灯片
# =========================================================
generators = [
    slide_cover,
    slide_agenda,
    slide_background,
    slide_scenarios,
    slide_partition_dim,
    slide_algo,
    slide_llm_tech,
    slide_synergist,
    slide_lit_dnn,
    slide_lit_sat_llm,
    slide_req_func,
    slide_req_hw,
    slide_difficulties,
    slide_repro,
    slide_research_pitfalls,
    slide_roadmap,
    slide_qa,
]

total_pages = len(generators)
for i, gen in enumerate(generators, start=1):
    gen(i, total_pages)


out_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'DNN_LLM平台讨论.pptx'))
prs.save(out_path)
print(f'Saved: {out_path}')
print(f'Slides: {total_pages}')

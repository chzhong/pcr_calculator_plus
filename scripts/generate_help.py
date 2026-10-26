"""Generate the bot's help.png. Requires Pillow; run from the repository root.

    python scripts/generate_help.py

The image is committed so Pillow is not needed by the running bot.
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "help.png"
WIDTH = 1120
PAD = 54
INK = "#183047"
MUTED = "#516779"
BLUE = "#1768ac"
PALE = "#eaf4fc"
LINE = "#d6e2ec"


def font(size):
    for candidate in (
        "/System/Library/Fonts/STHeiti Medium.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ):
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    raise RuntimeError("需要可显示中文的字体，可在 font() 中加入其路径")


canvas = Image.new("RGB", (WIDTH, 5000), "#ffffff")
draw = ImageDraw.Draw(canvas)
title_font, section_font = font(42), font(30)
body_font, small_font = font(23), font(21)
y = 46


def wrap(text, chosen_font, max_width):
    lines = []
    for source_line in text.split("\n"):
        if not source_line:
            lines.append("")
            continue
        line = ""
        for char in source_line:
            trial = line + char
            if line and draw.textlength(trial, font=chosen_font) > max_width:
                lines.append(line)
                line = char
            else:
                line = trial
        lines.append(line)
    return lines


def paragraph(text, *, chosen_font=body_font, color=INK, indent=0, gap=10):
    global y
    for line in wrap(text, chosen_font, WIDTH - 2 * PAD - indent):
        if line:
            draw.text((PAD + indent, y), line, font=chosen_font, fill=color)
        y += chosen_font.size + 12
    y += gap


def section(text):
    global y
    y += 24
    draw.rounded_rectangle((PAD, y, WIDTH - PAD, y + 54), radius=12, fill=PALE)
    draw.text((PAD + 16, y + 6), text, font=section_font, fill=BLUE)
    y += 76


def code(lines):
    global y
    line_height = small_font.size + 12
    box_height = len(lines) * line_height + 28
    draw.rounded_rectangle((PAD, y, WIDTH - PAD, y + box_height), radius=10,
                           fill="#f4f8fb", outline=LINE, width=2)
    for index, line in enumerate(lines):
        draw.text((PAD + 20, y + 14 + index * line_height), line,
                  font=small_font, fill=INK)
    y += box_height + 16


def row(left, right):
    global y
    height = max(len(wrap(right, small_font, 760)), 1) * 32 + 18
    draw.line((PAD, y, WIDTH - PAD, y), fill=LINE, width=2)
    draw.text((PAD + 12, y + 9), left, font=small_font, fill=BLUE)
    for i, line in enumerate(wrap(right, small_font, 760)):
        draw.text((PAD + 225, y + 9 + i * 32), line, font=small_font, fill=INK)
    y += height


draw.text((PAD, y), "PCR 公会战计算器 · 帮助", font=title_font, fill=BLUE)
y += 66
paragraph("合刀计算与补偿刀时间轴转换", color=MUTED)

section("合刀计算")
paragraph("命令：合刀 / 尾刀计算 / cal    帮助：合刀帮助 / 尾刀计算帮助 / cal帮助")
paragraph("先输入 boss 当前血量 B，再输入每刀伤害 D 或剩余时间 T，最后可输入期望返还时间 E。")
row("B  boss 血量", "700、700w、700万、7000000、1000-300")
row("D  单刀伤害", "500、500w、1e、1.5e、1.5亿、1k、1m、5000000")
row("T / E  秒数", "30s、30S、30秒、15+15；≤90 的无单位数按秒数解析")
y += 12
paragraph("常用格式：B D D = boss 血量 + 两刀伤害；B D = boss 血量 + 单刀伤害。", color=BLUE)
code(["合刀 700 500 600     → 比较两刀先后顺序的补偿", "合刀 700 400         → 计算单刀与合刀补偿"])
paragraph("其他示例：cal 700 30s（B T）；cal 700 800+55s（B DT）；cal 700 500 30s（B D T）。T 可视作 B+T 的缩写。伤害支持 w/万、e/亿、k、m 和四则运算；e/亿可用小数。", chosen_font=small_font)

section("补偿刀时间轴转换")
paragraph("帮助命令：转秒帮助 / 转补秒帮助")
paragraph("转秒：整刀时间轴（起点 90 秒）换算到自己的剩余时间。")
code(["转秒 remain_ts", "ts1", "[ts2 ...]"])
paragraph("转补秒：将对方补偿秒数的时间轴换算到自己的补偿秒数。")
code(["转补秒 their_remain_ts my_remain_ts", "ts1 [ts2 ...]"])
paragraph("参数可用空格或换行分隔。剩余时间为 21–90 秒；转秒输入 90 秒时无需转换。时间戳须为 1–85 秒。", chosen_font=small_font)
paragraph("支持 105、0105、1:05、01:05 等分秒写法；049、0049 都表示总共 49 秒。输出尽量保持原时间戳样式，舍去转换后小于等于零的项。", chosen_font=small_font)
paragraph("转补秒时，若自己的剩余时间比对方多，结果会提示自行模拟；多于 15 秒时建议自行模拟或换轴。", chosen_font=small_font, color=MUTED)

section("转换示例")
row("转秒", "补偿 1:14 的刀按整刀时间轴打")
code(["转秒 114", "105 055 017 016 009 003", "→ 049 039 001 TIME UP"])
row("转补秒", "原轴补偿 26 秒，自己补偿 31 秒")
code(["转补秒 26 31", "014 011 003 002", "→ 019 016 008 007", "→ 剩余时间请自行模拟 / TIME UP"])

y += 8
draw.line((PAD, y, WIDTH - PAD, y), fill=LINE, width=2)
y += 18
paragraph("完整说明与更多合刀例子请查看项目 README。", chosen_font=small_font, color=MUTED)

canvas.crop((0, 0, WIDTH, y + 24)).save(OUTPUT, optimize=True)
print(f"Wrote {OUTPUT} ({WIDTH} x {y + 24})")

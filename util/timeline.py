"""时间轴转换命令共用的解析与格式化逻辑。"""

import re
from collections import Counter


EMPTY_RESULT = "所有操作均在剩余时间之外，请自行模拟和调整"
LARGE_REMAIN_WARNING = "⚠️⚠️ 剩余时间较多，请自行模拟或换轴  ⚠️⚠️"


def parse_timestamp(raw):
    """返回 (总秒数, 输出样式)；样式包含分钟或纯数字的原始宽度。"""
    colon = re.fullmatch(r"(\d{1,2}):(\d{2})", raw)
    if colon:
        minute, second = int(colon[1], 10), int(colon[2], 10)
        if second >= 60:
            raise ValueError(raw)
        return minute * 60 + second, ("colon", len(colon[1]))

    if not re.fullmatch(r"\d{1,4}", raw):
        raise ValueError(raw)
    value = int(raw, 10)
    if value < 100:
        return value, ("digits", len(raw))
    if len(raw) < 3 or int(raw[-2:], 10) >= 60:
        raise ValueError(raw)
    return int(raw[:-2], 10) * 60 + int(raw[-2:], 10), ("digits", len(raw))


def format_timestamp(seconds, style):
    kind, width = style
    minute, second = divmod(seconds, 60)
    if kind == "colon":
        return f"{minute:0{width}d}:{second:02d}"
    # 一位或两位的纯数字输入表示总秒数；超过其宽度时自然扩展。
    if width <= 2:
        return f"{seconds:0{width}d}"
    return f"{minute * 100 + second:0{width}d}"


def _invalid_ts(tokens, index):
    start, end = max(0, index - 2), min(len(tokens), index + 3)
    context = [f"【{token}】" if i == index else token
               for i, token in enumerate(tokens[start:end], start)]
    return f"第{index + 1}个时间戳无效：{tokens[index]}\n参考：{' '.join(context)}"


def _convert(tokens, shift, warning=None):
    if not tokens:
        return "请提供至少一个时间戳"
    parsed = []
    for index, raw in enumerate(tokens):
        try:
            seconds, style = parse_timestamp(raw)
            if not 1 <= seconds <= 85:
                raise ValueError(raw)
        except ValueError:
            return _invalid_ts(tokens, index)
        parsed.append((seconds, style))

    counts = Counter(style for _, style in parsed)
    style = max((style for _, style in parsed), key=lambda item: counts[item])
    output = [format_timestamp(seconds - shift, style)
              for seconds, _ in parsed if seconds - shift > 0]
    if not output:
        return EMPTY_RESULT
    if warning:
        output.append(warning)
    output.append("TIME UP")
    return "\n".join(output)


def convert_seconds(text):
    tokens = text.split()
    if not tokens:
        return "剩余时间无效"
    try:
        remain, _ = parse_timestamp(tokens[0])
    except ValueError:
        return "剩余时间无效"
    if remain == 90:
        return "满补刀无需转换秒数"
    if not 21 <= remain <= 89:
        return "剩余时间无效"
    return _convert(tokens[1:], 90 - remain)


def convert_bonus_seconds(text):
    tokens = text.split()
    remains = []
    for index, label in enumerate(("对方剩余时间", "我的剩余时间")):
        try:
            remain, _ = parse_timestamp(tokens[index])
            if not 21 <= remain <= 90:
                raise ValueError(tokens[index])
        except (IndexError, ValueError):
            return f"{label}无效"
        remains.append(remain)
    their_remain, my_remain = remains
    if their_remain == my_remain:
        return "剩余时间一致，无效转秒"
    warning = None
    if my_remain > their_remain + 15:
        warning = LARGE_REMAIN_WARNING
    elif my_remain > their_remain:
        warning = "剩余时间请自行模拟"
    return _convert(tokens[2:], their_remain - my_remain, warning)

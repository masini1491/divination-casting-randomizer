#!/usr/bin/env python3
"""Canonical stochastic casting CLI and importable runtime API for divination."""

from __future__ import annotations

import argparse
import json
import secrets
from datetime import datetime, timezone
from typing import Any
from zoneinfo import ZoneInfo

SOURCE = "divination-casting-randomizer-python"
ALGORITHM_VERSION = "2"
SCHEMA_VERSION = "4"
AI_SCHEMA_VERSION = "1"
TAIPEI_TZ = ZoneInfo("Asia/Taipei")
SUPPORTED_METHODS = ("tarot", "plum", "liuyao")

MAJORS = [
    "愚者", "魔術師", "女祭司", "女皇", "皇帝", "教皇", "戀人", "戰車", "力量", "隱者",
    "命運之輪", "正義", "倒吊人", "死神", "節制", "惡魔", "高塔", "星星", "月亮", "太陽",
    "審判", "世界",
]
RANKS = ["一", "二", "三", "四", "五", "六", "七", "八", "九", "十", "侍者", "騎士", "皇后", "國王"]
SUITS = ["杖", "杯", "劍", "錢"]
DECK = MAJORS + [f"{suit}{rank}" for suit in SUITS for rank in RANKS]
MAJOR_SHORT = {"魔術師": "魔術", "女祭司": "女祭", "命運之輪": "命輪", "倒吊人": "吊人"}
COURT_SHORT = {"侍者": "侍", "騎士": "騎", "皇后": "后", "國王": "王"}

TRIGRAM = {1: "乾", 2: "兌", 3: "離", 4: "震", 5: "巽", 6: "坎", 7: "艮", 0: "坤"}
HEXAGRAM = {
    "乾乾":"乾為天","坤坤":"坤為地","坎震":"水雷屯","艮坎":"山水蒙","坎乾":"水天需","乾坎":"天水訟",
    "坤坎":"地水師","坎坤":"水地比","巽乾":"風天小畜","乾兌":"天澤履","坤乾":"地天泰","乾坤":"天地否",
    "乾離":"天火同人","離乾":"火天大有","坤艮":"地山謙","震坤":"雷地豫","兌震":"澤雷隨","艮巽":"山風蠱",
    "坤兌":"地澤臨","巽坤":"風地觀","離震":"火雷噬嗑","艮離":"山火賁","艮坤":"山地剝","坤震":"地雷復",
    "乾震":"天雷無妄","艮乾":"山天大畜","艮震":"山雷頤","兌巽":"澤風大過","坎坎":"坎為水","離離":"離為火",
    "兌艮":"澤山咸","震巽":"雷風恆","乾艮":"天山遯","震乾":"雷天大壯","離坤":"火地晉","坤離":"地火明夷",
    "巽離":"風火家人","離兌":"火澤睽","坎艮":"水山蹇","震坎":"雷水解","艮兌":"山澤損","巽震":"風雷益",
    "兌乾":"澤天夬","乾巽":"天風姤","兌坤":"澤地萃","坤巽":"地風升","兌坎":"澤水困","坎巽":"水風井",
    "兌離":"澤火革","離巽":"火風鼎","震震":"震為雷","艮艮":"艮為山","巽艮":"風山漸","震兌":"雷澤歸妹",
    "震離":"雷火豐","離艮":"火山旅","巽巽":"巽為風","兌兌":"兌為澤","巽坎":"風水渙","坎兌":"水澤節",
    "巽兌":"風澤中孚","震艮":"雷山小過","坎離":"水火既濟","離坎":"火水未濟",
}

LIUYAO_POSITION_NAMES = ("初爻", "二爻", "三爻", "四爻", "五爻", "上爻")
LIUYAO_LINE_META = {
    6: ("yin", True, "老陰"),
    7: ("yang", False, "少陽"),
    8: ("yin", False, "少陰"),
    9: ("yang", True, "老陽"),
}
UINT32_RANGE = 1 << 32


def randbelow(max_value: int) -> int:
    """Uniform integer in [0, max_value) using 32-bit rejection sampling."""
    if max_value <= 0:
        raise ValueError("max_value must be > 0")
    if max_value == 1:
        return 0
    if max_value > UINT32_RANGE:
        return secrets.randbelow(max_value)
    limit = UINT32_RANGE - (UINT32_RANGE % max_value)
    while True:
        value = secrets.randbits(32)
        if value < limit:
            return value % max_value


def fisher_yates(items: list[str]) -> list[str]:
    shuffled = list(items)
    for i in range(len(shuffled) - 1, 0, -1):
        j = randbelow(i + 1)
        shuffled[i], shuffled[j] = shuffled[j], shuffled[i]
    return shuffled


def short_name(name: str) -> str:
    if name in MAJOR_SHORT:
        return MAJOR_SHORT[name]
    for suit in SUITS:
        if name.startswith(suit):
            rank = name[len(suit):]
            return suit + COURT_SHORT.get(rank, rank)
    return name


def draw_tarot(count: int) -> dict[str, Any]:
    if not 1 <= count <= 24:
        raise ValueError("Tarot count must be between 1 and 24.")
    chosen = fisher_yates(DECK)[:count]
    cards = []
    for index, full_name in enumerate(chosen, start=1):
        orientation = "逆" if randbelow(2) else "正"
        short = short_name(full_name)
        cards.append({
            "index": index,
            "card": short,
            "full_name": full_name,
            "orientation": orientation,
            "shorthand": f"{short}{orientation}",
        })
    return {"count": count, "cards": cards}


def cast_plum() -> dict[str, Any]:
    a, b = randbelow(1000), randbelow(1000)
    upper, lower = TRIGRAM[a % 8], TRIGRAM[b % 8]
    rem = (a + b) % 6
    moving_line = 6 if rem == 0 else rem
    return {
        "a": f"{a:03d}",
        "b": f"{b:03d}",
        "upper_trigram": upper,
        "lower_trigram": lower,
        "hexagram": HEXAGRAM[upper + lower],
        "moving_line": moving_line,
        "casting_rule": "A%8→上卦；B%8→下卦；(A+B)%6→動爻；餘0分別視為坤／第6爻",
    }


def resolve_liuyao_coin_values(coin_values: list[int] | tuple[int, int, int]) -> dict[str, Any]:
    """Resolve one three-coin toss using canonical yin=2 / yang=3 mapping."""
    if len(coin_values) != 3 or any(v not in {2, 3} for v in coin_values):
        raise ValueError("Liuyao coin values must be exactly three values, each 2 or 3.")
    values = list(coin_values)
    line_value = sum(values)
    yin_yang, changing, line_type = LIUYAO_LINE_META[line_value]
    return {
        "coin_values": values,
        "coin_faces": ["yin" if v == 2 else "yang" for v in values],
        "value": line_value,
        "yin_yang": yin_yang,
        "changing": changing,
        "line_type": line_type,
    }


def cast_liuyao_coins() -> dict[str, Any]:
    """Cast six lines bottom-to-top with three independent fair coins per line."""
    lines = []
    for position, position_name in enumerate(LIUYAO_POSITION_NAMES, start=1):
        values = [2 if randbelow(2) == 0 else 3 for _ in range(3)]
        line = resolve_liuyao_coin_values(values)
        line.update({"position": position, "position_name": position_name})
        lines.append(line)
    return {
        "cast_method": "three-coins",
        "line_order": "bottom-to-top",
        "coin_mapping": {"yin": 2, "yang": 3},
        "casting_rule": "每爻三枚獨立公平銅錢；陰=2、陽=3；合計6/7/8/9；6=老陰動、7=少陽靜、8=少陰靜、9=老陽動；由初爻至上爻起卦",
        "lines": lines,
    }


def make_result(method: str, count: int | None = None) -> dict[str, Any]:
    result: dict[str, Any] = {"method": method}
    if method in {"tarot", "both"}:
        if count is None:
            raise ValueError("Tarot count is required.")
        result["tarot"] = draw_tarot(count)
    if method in {"plum", "both"}:
        result["plum"] = cast_plum()
    if method == "liuyao":
        result["liuyao"] = cast_liuyao_coins()
    return result


def package(results: list[dict[str, Any]], source_commit: str | None = None) -> dict[str, Any]:
    utc = datetime.now(timezone.utc)
    taipei = utc.astimezone(TAIPEI_TZ)
    return {
        "source": SOURCE,
        "algorithm_version": ALGORITHM_VERSION,
        "schema_version": SCHEMA_VERSION,
        "supported_methods": list(SUPPORTED_METHODS),
        "runtime_source_commit": source_commit or "unknown",
        "generated_at_utc": utc.isoformat(timespec="seconds"),
        "generated_at_taipei": taipei.isoformat(timespec="seconds"),
        "timezone": "Asia/Taipei",
        "rng": "secrets.randbits(32) + rejection sampling",
        "results": results,
    }


def compact_ai_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Project a full canonical payload into a low-token AI transport shape.

    This does not change stochastic results. It intentionally omits redundant
    descriptive fields; use full JSON when audit-grade raw metadata is needed.
    """
    compact_results: list[dict[str, Any]] = []
    for result in payload["results"]:
        compact: dict[str, Any] = {"method": result["method"]}
        tarot = result.get("tarot")
        if tarot:
            compact["tarot"] = {
                "count": tarot["count"],
                "cards": [[card["full_name"], card["orientation"]] for card in tarot["cards"]],
            }
        plum = result.get("plum")
        if plum:
            compact["plum"] = {
                "a": plum["a"],
                "b": plum["b"],
                "upper": plum["upper_trigram"],
                "lower": plum["lower_trigram"],
                "hexagram": plum["hexagram"],
                "moving_line": plum["moving_line"],
            }
        liuyao = result.get("liuyao")
        if liuyao:
            compact["liuyao"] = {
                "cast_method": liuyao["cast_method"],
                "line_order": liuyao["line_order"],
                "values": [line["value"] for line in liuyao["lines"]],
                "coin_values": [line["coin_values"] for line in liuyao["lines"]],
            }
        compact_results.append(compact)
    return {
        "source": payload["source"],
        "algorithm_version": payload["algorithm_version"],
        "schema_version": payload["schema_version"],
        "ai_schema_version": AI_SCHEMA_VERSION,
        "runtime_source_commit": payload["runtime_source_commit"],
        "generated_at_taipei": payload["generated_at_taipei"],
        "timezone": payload["timezone"],
        "results": compact_results,
    }


def validate_repeat(repeat: int) -> None:
    if repeat < 1 or repeat > 100:
        raise ValueError("--repeat must be between 1 and 100")


def generate_payload(
    command: str,
    *,
    count: int = 3,
    repeat: int = 1,
    counts: list[int] | None = None,
    method: str = "tarot",
    source_commit: str | None = None,
) -> dict[str, Any]:
    """Import-friendly execution API that avoids CLI/subprocess overhead."""
    if command == "tarot":
        validate_repeat(repeat)
        results = [make_result("tarot", count) for _ in range(repeat)]
    elif command == "plum":
        validate_repeat(repeat)
        results = [make_result("plum") for _ in range(repeat)]
    elif command == "liuyao":
        validate_repeat(repeat)
        results = [make_result("liuyao") for _ in range(repeat)]
    elif command == "both":
        validate_repeat(repeat)
        results = [make_result("both", count) for _ in range(repeat)]
    elif command == "batch":
        if not counts:
            raise ValueError("counts are required for batch")
        if method not in {"tarot", "both"}:
            raise ValueError("batch method must be tarot or both")
        if any(value < 1 or value > 24 for value in counts):
            raise ValueError("each count must be between 1 and 24")
        results = [make_result(method, value) for value in counts]
    else:
        raise ValueError(f"unsupported command: {command}")
    return package(results, source_commit=source_commit)


def render_text(payload: dict[str, Any]) -> str:
    lines = [
        f"來源：{payload['source']} v{payload['algorithm_version']}",
        f"時間：{payload['generated_at_taipei']}",
    ]
    results = payload["results"]
    for idx, result in enumerate(results, start=1):
        if len(results) > 1:
            lines.extend(["", f"第 {idx} 題"])
        tarot = result.get("tarot")
        if tarot:
            lines.append(f"塔羅（{tarot['count']} 張）")
            lines.append("，".join(c["shorthand"] for c in tarot["cards"]))
        plum = result.get("plum")
        if plum:
            lines.extend([
                "梅花易數｜雙數起卦",
                f"{plum['a']}，{plum['b']}",
                f"本卦：{plum['hexagram']}",
                f"上卦：{plum['upper_trigram']}",
                f"下卦：{plum['lower_trigram']}",
                f"動爻：第 {plum['moving_line']} 爻",
                f"取卦規則：{plum['casting_rule']}",
            ])
        liuyao = result.get("liuyao")
        if liuyao:
            lines.append("六爻｜三錢法")
            for line in liuyao["lines"]:
                state = "動" if line["changing"] else "靜"
                coins = "/".join("陽" if f == "yang" else "陰" for f in line["coin_faces"])
                lines.append(f"{line['position_name']}：{line['value']} {line['line_type']}（{state}）｜{coins}")
            lines.append(f"起卦規則：{liuyao['casting_rule']}")
    return "\n".join(lines)


def parse_counts(raw: str) -> list[int]:
    try:
        values = [int(x.strip()) for x in raw.split(",") if x.strip()]
    except ValueError as exc:
        raise argparse.ArgumentTypeError("--counts must be comma-separated integers") from exc
    if not values:
        raise argparse.ArgumentTypeError("--counts cannot be empty")
    if any(v < 1 or v > 24 for v in values):
        raise argparse.ArgumentTypeError("each count must be between 1 and 24")
    return values


def add_common_format(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--format", choices=("text", "json", "ai-json"), default="text")
    parser.add_argument("--source-commit", default=None)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Divination Casting Randomizer CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p_tarot = sub.add_parser("tarot")
    p_tarot.add_argument("--count", type=int, default=3)
    p_tarot.add_argument("--repeat", type=int, default=1)
    add_common_format(p_tarot)

    p_plum = sub.add_parser("plum")
    p_plum.add_argument("--repeat", type=int, default=1)
    add_common_format(p_plum)

    p_liuyao = sub.add_parser("liuyao")
    p_liuyao.add_argument("--method", choices=("coins",), default="coins")
    p_liuyao.add_argument("--repeat", type=int, default=1)
    add_common_format(p_liuyao)

    p_both = sub.add_parser("both")
    p_both.add_argument("--count", type=int, default=3)
    p_both.add_argument("--repeat", type=int, default=1)
    add_common_format(p_both)

    p_batch = sub.add_parser("batch")
    p_batch.add_argument("--counts", type=parse_counts, required=True)
    p_batch.add_argument("--method", choices=("tarot", "both"), default="tarot")
    add_common_format(p_batch)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        payload = generate_payload(
            args.command,
            count=getattr(args, "count", 3),
            repeat=getattr(args, "repeat", 1),
            counts=getattr(args, "counts", None),
            method=getattr(args, "method", "tarot"),
            source_commit=args.source_commit,
        )
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc

    if args.format == "text":
        print(render_text(payload))
    elif args.format == "ai-json":
        print(json.dumps(compact_ai_payload(payload), ensure_ascii=False, separators=(",", ":")))
    else:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

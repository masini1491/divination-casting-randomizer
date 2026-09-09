#!/usr/bin/env python3
"""Divination Casting Randomizer CLI for AI/runtime use.

Standard-library only. Current canonical methods are Tarot and Meihua.
Tarot draws use a 78-card deck, independent upright/reversed orientation,
and a fresh Fisher-Yates shuffle per question. Meihua uses two random
integers A/B in 000-999: A % 8 -> upper trigram, B % 8 -> lower trigram,
(A+B) % 6 -> moving line, with remainder 0 mapped to Kun / line 6.
"""

from __future__ import annotations

import argparse
import json
import secrets
from datetime import datetime, timezone
from typing import Any
from zoneinfo import ZoneInfo

SOURCE = "divination-casting-randomizer-python"
ALGORITHM_VERSION = "1"
SCHEMA_VERSION = "3"
TAIPEI_TZ = ZoneInfo("Asia/Taipei")

MAJORS = [
    "愚者", "魔術師", "女祭司", "女皇", "皇帝", "教皇", "戀人", "戰車", "力量", "隱者",
    "命運之輪", "正義", "倒吊人", "死神", "節制", "惡魔", "高塔", "星星", "月亮", "太陽",
    "審判", "世界",
]
RANKS = ["一", "二", "三", "四", "五", "六", "七", "八", "九", "十", "侍者", "騎士", "皇后", "國王"]
SUITS = ["杖", "杯", "劍", "錢"]
DECK = MAJORS + [f"{suit}{rank}" for suit in SUITS for rank in RANKS]

MAJOR_SHORT = {
    "魔術師": "魔術",
    "女祭司": "女祭",
    "命運之輪": "命輪",
    "倒吊人": "吊人",
}
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
        reversed_ = randbelow(2) == 1
        orientation = "逆" if reversed_ else "正"
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
    a = randbelow(1000)
    b = randbelow(1000)
    upper = TRIGRAM[a % 8]
    lower = TRIGRAM[b % 8]
    moving_remainder = (a + b) % 6
    moving_line = 6 if moving_remainder == 0 else moving_remainder
    name = HEXAGRAM[upper + lower]

    return {
        "a": f"{a:03d}",
        "b": f"{b:03d}",
        "upper_trigram": upper,
        "lower_trigram": lower,
        "hexagram": name,
        "moving_line": moving_line,
        "casting_rule": "A%8→上卦；B%8→下卦；(A+B)%6→動爻；餘0分別視為坤／第6爻",
    }


def make_result(method: str, count: int | None = None) -> dict[str, Any]:
    result: dict[str, Any] = {"method": method}
    if method in {"tarot", "both"}:
        assert count is not None
        result["tarot"] = draw_tarot(count)
    if method in {"plum", "both"}:
        result["plum"] = cast_plum()
    return result


def package(results: list[dict[str, Any]], source_commit: str | None = None) -> dict[str, Any]:
    generated_at_utc_dt = datetime.now(timezone.utc)
    generated_at_taipei_dt = generated_at_utc_dt.astimezone(TAIPEI_TZ)
    return {
        "source": SOURCE,
        "algorithm_version": ALGORITHM_VERSION,
        "schema_version": SCHEMA_VERSION,
        "runtime_source_commit": source_commit or "unknown",
        "generated_at_utc": generated_at_utc_dt.isoformat(timespec="seconds"),
        "generated_at_taipei": generated_at_taipei_dt.isoformat(timespec="seconds"),
        "timezone": "Asia/Taipei",
        "rng": "secrets.randbits(32) + rejection sampling",
        "results": results,
    }


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
            lines.append("，".join(card["shorthand"] for card in tarot["cards"]))

        plum = result.get("plum")
        if plum:
            lines.append("梅花易數｜雙數起卦")
            lines.append(f"{plum['a']}，{plum['b']}")
            lines.append(f"本卦：{plum['hexagram']}")
            lines.append(f"上卦：{plum['upper_trigram']}")
            lines.append(f"下卦：{plum['lower_trigram']}")
            lines.append(f"動爻：第 {plum['moving_line']} 爻")
            lines.append(f"取卦規則：{plum['casting_rule']}")
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
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument(
        "--source-commit",
        default=None,
        help="GitHub commit SHA for the canonical randomizer.py used by this run",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Divination Casting Randomizer CLI (standard library only)"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_tarot = sub.add_parser("tarot", help="draw Tarot cards")
    p_tarot.add_argument("--count", type=int, default=3)
    p_tarot.add_argument("--repeat", type=int, default=1)
    add_common_format(p_tarot)

    p_plum = sub.add_parser("plum", help="cast Meihua with A/B double-number method")
    p_plum.add_argument("--repeat", type=int, default=1)
    add_common_format(p_plum)

    p_both = sub.add_parser("both", help="draw Tarot and cast Meihua independently")
    p_both.add_argument("--count", type=int, default=3)
    p_both.add_argument("--repeat", type=int, default=1)
    add_common_format(p_both)

    p_batch = sub.add_parser(
        "batch",
        help="multiple independent questions with per-question Tarot counts",
    )
    p_batch.add_argument("--counts", type=parse_counts, required=True,
                         help="comma-separated Tarot counts, e.g. 5,5,6,3")
    p_batch.add_argument("--method", choices=("tarot", "both"), default="tarot")
    add_common_format(p_batch)

    return parser


def validate_repeat(repeat: int) -> None:
    if repeat < 1:
        raise ValueError("--repeat must be >= 1")
    if repeat > 100:
        raise ValueError("--repeat must be <= 100")


def main() -> int:
    args = build_parser().parse_args()

    try:
        if args.command == "tarot":
            validate_repeat(args.repeat)
            results = [make_result("tarot", args.count) for _ in range(args.repeat)]
        elif args.command == "plum":
            validate_repeat(args.repeat)
            results = [make_result("plum") for _ in range(args.repeat)]
        elif args.command == "both":
            validate_repeat(args.repeat)
            results = [make_result("both", args.count) for _ in range(args.repeat)]
        else:
            results = [make_result(args.method, count) for count in args.counts]
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc

    payload = package(results, source_commit=args.source_commit)
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(render_text(payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
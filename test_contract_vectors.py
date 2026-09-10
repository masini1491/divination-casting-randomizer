import hashlib
import json
from pathlib import Path
import re
import unittest

import randomizer

ROOT = Path(__file__).resolve().parent
VECTORS = json.loads((ROOT / "contract_vectors.json").read_text(encoding="utf-8"))
HTML = (ROOT / "index.html").read_text(encoding="utf-8")


def _extract_json_array(name: str) -> list[str]:
    match = re.search(rf"const {name}=(\[[^;]+\]);", HTML)
    if not match:
        raise AssertionError(f"missing JS array: {name}")
    return json.loads(match.group(1))


def _extract_json_object(name: str) -> dict[str, str]:
    match = re.search(rf"const {name}=(\{{[^;]+\}});", HTML)
    if not match:
        raise AssertionError(f"missing JS object: {name}")
    return json.loads(match.group(1))


def _extract_tri() -> dict[int, str]:
    match = re.search(r"const tri=\{([^;]+)\};", HTML)
    if not match:
        raise AssertionError("missing JS tri map")
    return {int(key): value for key, value in re.findall(r'(\d):"([^"]+)"', match.group(1))}


class CrossRuntimeContractTests(unittest.TestCase):
    def test_tarot_deck_matches_shared_vector_in_python_and_web(self):
        tarot = VECTORS["tarot"]
        python_deck = randomizer.DECK
        web_deck = _extract_json_array("majors") + [
            suit + rank
            for suit in _extract_json_array("suits")
            for rank in _extract_json_array("ranks")
        ]

        self.assertEqual(len(python_deck), tarot["deck_size"])
        self.assertEqual(web_deck, python_deck)
        digest = hashlib.sha256("\n".join(python_deck).encode("utf-8")).hexdigest()
        self.assertEqual(digest, tarot["deck_sha256_lf"])
        self.assertIn("return shuffle(deck).slice(0,n)", HTML)
        self.assertIn("rev:rnd(2)===1", HTML)

    def test_plum_golden_vectors_match_python_and_web_tables(self):
        web_tri = _extract_tri()
        web_hex = _extract_json_object("hex")
        self.assertEqual(web_tri, randomizer.TRIGRAM)
        self.assertEqual(web_hex, randomizer.HEXAGRAM)

        for vector in VECTORS["plum"]["vectors"]:
            a, b = vector["a"], vector["b"]
            upper = randomizer.TRIGRAM[a % 8]
            lower = randomizer.TRIGRAM[b % 8]
            moving_line = (a + b) % 6 or 6
            self.assertEqual(upper, vector["upper"])
            self.assertEqual(lower, vector["lower"])
            self.assertEqual(randomizer.HEXAGRAM[upper + lower], vector["hexagram"])
            self.assertEqual(moving_line, vector["moving_line"])

        self.assertIn("m=(a+b)%6", HTML)
        self.assertIn("up=tri[a%8]", HTML)
        self.assertIn("low=tri[b%8]", HTML)
        self.assertIn("move:m===0?6:m", HTML)

    def test_liuyao_golden_vectors_match_python_and_web_contract(self):
        for vector in VECTORS["liuyao"]["line_vectors"]:
            resolved = randomizer.resolve_liuyao_coin_values(vector["coins"])
            self.assertEqual(resolved["value"], vector["value"])
            self.assertEqual(resolved["yin_yang"], vector["yin_yang"])
            self.assertEqual(resolved["changing"], vector["changing"])
            self.assertEqual(resolved["line_type"], vector["line_type"])

        self.assertIn('const yaoNames=["初爻","二爻","三爻","四爻","五爻","上爻"]', HTML)
        self.assertIn('6:["老陰","陰",true]', HTML)
        self.assertIn('7:["少陽","陽",false]', HTML)
        self.assertIn('8:["少陰","陰",false]', HTML)
        self.assertIn('9:["老陽","陽",true]', HTML)
        self.assertIn("coins=Array.from({length:3},()=>rnd(2)===0?2:3)", HTML)


if __name__ == "__main__":
    unittest.main()

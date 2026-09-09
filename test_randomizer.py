import json
import subprocess
import sys
import unittest

import randomizer


class RandomizerTests(unittest.TestCase):
    def test_deck_has_78_unique_cards(self):
        self.assertEqual(len(randomizer.DECK), 78)
        self.assertEqual(len(set(randomizer.DECK)), 78)

    def test_tarot_draw_has_no_duplicates(self):
        result = randomizer.draw_tarot(24)
        cards = result["cards"]
        self.assertEqual(len(cards), 24)
        self.assertEqual(len({card["full_name"] for card in cards}), 24)
        self.assertTrue(all(card["orientation"] in {"正", "逆"} for card in cards))

    def test_each_question_draw_is_independent_shape(self):
        payload = randomizer.package([
            randomizer.make_result("tarot", 5),
            randomizer.make_result("tarot", 5),
            randomizer.make_result("tarot", 6),
        ])
        self.assertEqual([r["tarot"]["count"] for r in payload["results"]], [5, 5, 6])
        for result in payload["results"]:
            cards = result["tarot"]["cards"]
            self.assertEqual(len(cards), len({card["full_name"] for card in cards}))

    def test_plum_contract(self):
        for _ in range(100):
            result = randomizer.cast_plum()
            self.assertRegex(result["a"], r"^\d{3}$")
            self.assertRegex(result["b"], r"^\d{3}$")
            self.assertIn(result["upper_trigram"], set(randomizer.TRIGRAM.values()))
            self.assertIn(result["lower_trigram"], set(randomizer.TRIGRAM.values()))
            self.assertIn(result["hexagram"], set(randomizer.HEXAGRAM.values()))
            self.assertGreaterEqual(result["moving_line"], 1)
            self.assertLessEqual(result["moving_line"], 6)

    def test_all_hexagram_pairs_are_covered(self):
        pairs = {
            upper + lower
            for upper in set(randomizer.TRIGRAM.values())
            for lower in set(randomizer.TRIGRAM.values())
        }
        self.assertEqual(set(randomizer.HEXAGRAM), pairs)

    def test_liuyao_coin_resolution_covers_four_line_values(self):
        cases = {
            (2, 2, 2): (6, "yin", True, "老陰"),
            (3, 2, 2): (7, "yang", False, "少陽"),
            (3, 3, 2): (8, "yin", False, "少陰"),
            (3, 3, 3): (9, "yang", True, "老陽"),
        }
        for coins, expected in cases.items():
            result = randomizer.resolve_liuyao_coin_values(coins)
            self.assertEqual(
                (result["value"], result["yin_yang"], result["changing"], result["line_type"]),
                expected,
            )
            self.assertEqual(sum(result["coin_values"]), result["value"])

    def test_liuyao_cast_has_six_bottom_to_top_lines(self):
        result = randomizer.cast_liuyao_coins()
        self.assertEqual(result["cast_method"], "three-coins")
        self.assertEqual(result["line_order"], "bottom-to-top")
        self.assertEqual(len(result["lines"]), 6)
        self.assertEqual([line["position"] for line in result["lines"]], list(range(1, 7)))
        self.assertEqual(
            [line["position_name"] for line in result["lines"]],
            list(randomizer.LIUYAO_POSITION_NAMES),
        )
        for line in result["lines"]:
            self.assertEqual(len(line["coin_values"]), 3)
            self.assertTrue(all(value in {2, 3} for value in line["coin_values"]))
            self.assertEqual(sum(line["coin_values"]), line["value"])
            self.assertIn(line["value"], {6, 7, 8, 9})
            self.assertEqual(line["changing"], line["value"] in {6, 9})
            self.assertEqual(line["yin_yang"], "yin" if line["value"] in {6, 8} else "yang")

    def test_package_declares_supported_methods_and_versions(self):
        payload = randomizer.package([randomizer.make_result("liuyao")])
        self.assertEqual(payload["source"], "divination-casting-randomizer-python")
        self.assertEqual(payload["algorithm_version"], "2")
        self.assertEqual(payload["schema_version"], "4")
        self.assertEqual(payload["supported_methods"], ["tarot", "plum", "liuyao"])

    def test_liuyao_cli_json_is_parseable(self):
        completed = subprocess.run(
            [sys.executable, "randomizer.py", "liuyao", "--format", "json"],
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["results"][0]["method"], "liuyao")
        self.assertEqual(len(payload["results"][0]["liuyao"]["lines"]), 6)

    def test_invalid_liuyao_coin_values_rejected(self):
        with self.assertRaises(ValueError):
            randomizer.resolve_liuyao_coin_values([2, 3])
        with self.assertRaises(ValueError):
            randomizer.resolve_liuyao_coin_values([2, 3, 4])

    def test_invalid_tarot_count_rejected(self):
        with self.assertRaises(ValueError):
            randomizer.draw_tarot(0)
        with self.assertRaises(ValueError):
            randomizer.draw_tarot(25)


if __name__ == "__main__":
    unittest.main()

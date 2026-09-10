import os
import unittest
from unittest import mock

from api import cast


class CastApiContractTests(unittest.TestCase):
    def test_accepts_minimal_tarot_request(self):
        self.assertEqual(
            cast.validate_cast_request({"method": "tarot", "count": 3}),
            {"method": "tarot", "count": 3, "repeat": 1},
        )

    def test_accepts_plum_and_liuyao_without_count(self):
        for method in ("plum", "liuyao"):
            with self.subTest(method=method):
                params = cast.validate_cast_request({"method": method, "repeat": 2})
                self.assertEqual(params["method"], method)
                self.assertEqual(params["count"], 3)
                self.assertEqual(params["repeat"], 2)

    def test_rejects_question_or_other_extra_fields(self):
        with self.assertRaisesRegex(cast.RequestValidationError, "unsupported field"):
            cast.validate_cast_request({"method": "tarot", "count": 3, "question": "private text"})

    def test_rejects_legacy_both_method(self):
        with self.assertRaisesRegex(cast.RequestValidationError, "method must be"):
            cast.validate_cast_request({"method": "both", "count": 3})

    def test_rejects_invalid_count_and_repeat(self):
        invalid_requests = [
            {"method": "tarot", "count": 0},
            {"method": "tarot", "count": 25},
            {"method": "tarot", "count": True},
            {"method": "tarot", "repeat": 0},
            {"method": "tarot", "repeat": cast.MAX_REPEAT + 1},
        ]
        for request in invalid_requests:
            with self.subTest(request=request):
                with self.assertRaises(cast.RequestValidationError):
                    cast.validate_cast_request(request)

    def test_execute_cast_uses_deployment_commit_and_compact_projection(self):
        full = {"full": "payload"}
        compact = {"compact": "payload"}
        with (
            mock.patch.dict(os.environ, {"VERCEL_GIT_COMMIT_SHA": "deadbeef"}, clear=False),
            mock.patch.object(cast.randomizer, "generate_payload", return_value=full) as generate,
            mock.patch.object(cast.randomizer, "compact_ai_payload", return_value=compact) as project,
        ):
            result = cast.execute_cast({"method": "tarot", "count": 5, "repeat": 4})

        self.assertEqual(result, compact)
        generate.assert_called_once_with(
            "tarot", count=5, repeat=4, source_commit="deadbeef"
        )
        project.assert_called_once_with(full)

    def test_execute_cast_falls_back_to_unknown_commit_off_vercel(self):
        with (
            mock.patch.dict(os.environ, {}, clear=True),
            mock.patch.object(cast.randomizer, "generate_payload", return_value={}) as generate,
            mock.patch.object(cast.randomizer, "compact_ai_payload", return_value={}),
        ):
            cast.execute_cast({"method": "plum", "count": 3, "repeat": 1})
        self.assertEqual(generate.call_args.kwargs["source_commit"], "unknown")


if __name__ == "__main__":
    unittest.main()

import unittest

from wubi_helper import WubiRepository


class WubiRepositoryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.repository = WubiRepository()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.repository.close()

    def test_exact_match_prefers_short_code(self) -> None:
        result = self.repository.query("中")
        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result.main_code, "k")
        self.assertEqual(result.mode, "exact")
        self.assertIn("khk", result.all_codes)

    def test_exact_match_can_use_longest_code(self) -> None:
        result = self.repository.query("中", code_mode="longest")
        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result.main_code, "khk")
        self.assertEqual(result.code_mode, "longest")

    def test_other_codes_do_not_repeat_selected_main_code(self) -> None:
        result = self.repository.query("你", code_mode="longest")
        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result.main_code, "wqiy")
        self.assertEqual(result.other_codes, ("wq", "wqi"))

    def test_phrase_can_be_derived_when_not_in_database(self) -> None:
        result = self.repository.query("中根")
        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result.main_code, "khsv")
        self.assertEqual(result.all_codes, ("khsv",))
        self.assertEqual(result.mode, "derived")

    def test_exact_phrase_still_uses_database(self) -> None:
        result = self.repository.query("输入法")
        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result.main_code, "ltif")
        self.assertEqual(result.mode, "exact")


if __name__ == "__main__":
    unittest.main()

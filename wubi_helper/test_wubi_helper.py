import unittest

from wubi_helper import WubiApp, WubiRepository


class WubiRepositoryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.repository = WubiRepository(wubi_version="86")

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


class Wubi98RepositoryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.repository = WubiRepository(wubi_version="98")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.repository.close()

    def test_wubi98_supports_xian_code(self) -> None:
        result = self.repository.query("显", code_mode="longest")
        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result.wubi_version, "98")
        self.assertEqual(result.main_code, "jof")
        self.assertEqual(result.all_codes, ("jo", "jof"))

    def test_wubi98_prefers_short_code(self) -> None:
        result = self.repository.query("显")
        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result.main_code, "jo")
        self.assertEqual(result.mode, "exact")

    def test_wubi98_can_use_full_code(self) -> None:
        result = self.repository.query("显", code_mode="longest")
        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result.main_code, "jof")
        self.assertEqual(result.code_mode, "longest")


class WubiXinshijiRepositoryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.repository = WubiRepository(wubi_version="xinshiji")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.repository.close()

    def test_xinshiji_version_supports_xian_code(self) -> None:
        result = self.repository.query("显", code_mode="longest")
        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result.wubi_version, "xinshiji")
        self.assertEqual(result.main_code, "jogf")
        self.assertEqual(result.all_codes, ("jo", "jog", "jogf"))

    def test_default_version_is_xinshiji(self) -> None:
        default_repository = WubiRepository()
        try:
            result = default_repository.query("显", code_mode="longest")
            self.assertIsNotNone(result)
            assert result is not None
            self.assertEqual(result.wubi_version, "xinshiji")
            self.assertEqual(result.main_code, "jogf")
            self.assertEqual(result.all_codes, ("jo", "jog", "jogf"))
        finally:
            default_repository.close()

    def test_xinshiji_alias_06_can_be_used(self) -> None:
        alias_repository = WubiRepository(wubi_version="06")
        try:
            result = alias_repository.query("输入法")
            self.assertIsNotNone(result)
            assert result is not None
            self.assertEqual(result.wubi_version, "xinshiji")
            self.assertEqual(result.main_code, "ltif")
            self.assertEqual(result.mode, "exact")
        finally:
            alias_repository.close()


class WubiAppTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.repository = WubiRepository(wubi_version="86")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.repository.close()

    def test_non_exact_match_hides_codes_and_images(self) -> None:
        app = WubiApp(self.repository, code_mode="longest")
        try:
            app.query_var.set("中根")
            app.search()
            self.assertEqual(app.code_var.get(), "编码：-")
            self.assertEqual(app.alt_var.get(), "其他编码：-")
            self.assertEqual(app.hit_var.get(), "命中结果：86 版未命中")
            self.assertTrue(all(not card.canvas.find_all() for card in app.cards))
        finally:
            app.root.destroy()


if __name__ == "__main__":
    unittest.main()

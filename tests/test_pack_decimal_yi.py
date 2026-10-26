import unittest

from util.pack import PackInvaildException, from_string


class DecimalYiTests(unittest.TestCase):
    def test_decimal_yi_as_damage(self):
        for raw in ("1.5e", "1.5E", "1.5亿"):
            with self.subTest(raw=raw):
                pack = from_string(raw)
                self.assertEqual((pack.D, pack.T), (150000000, None))
        self.assertEqual(from_string("1.23456789亿").D, 123456789)

    def test_expression_and_remaining_time(self):
        self.assertEqual(from_string("1.5亿-500w").D, 145000000)
        pack = from_string("1.5亿+30秒")
        self.assertEqual((pack.D, pack.T), (150000000, 30))

    def test_fractional_damage_is_rejected(self):
        with self.assertRaises(PackInvaildException):
            from_string("1.234567891亿")


if __name__ == "__main__":
    unittest.main()

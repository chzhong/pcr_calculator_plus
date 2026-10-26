import unittest

from util.timeline import convert_bonus_seconds, convert_seconds


class TimelineTests(unittest.TestCase):
    def test_examples(self):
        self.assertEqual(convert_seconds("114\n105\n055\n017\n016\n009\n003"),
                         "049\n039\n001\nTIME UP")
        self.assertEqual(convert_seconds("1:24 1:05 0:55 0:17 0:16 0:09 0:03"),
                         "0:59\n0:49\n0:11\n0:10\n0:03\nTIME UP")

    def test_bounds_and_empty(self):
        self.assertEqual(convert_seconds("130 085"), "满补刀无需转换秒数")
        self.assertEqual(convert_seconds("020 050"), "剩余时间无效")
        self.assertEqual(convert_seconds("121 001"),
                         "所有操作均在剩余时间之外，请自行模拟和调整")
        self.assertEqual(convert_seconds("129 085"), "124\nTIME UP")

    def test_style_and_decimal(self):
        self.assertEqual(convert_seconds("109 0049 049 1:05"), "0028\n0028\n0044\nTIME UP")
        self.assertEqual(convert_seconds("109 01:05 049 0:50"), "00:44\n00:28\n00:29\nTIME UP")

    def test_invalid_timestamp_context(self):
        self.assertEqual(convert_seconds("129 010 020 abc 040 050 060"),
                         "第3个时间戳无效：abc\n参考：010 020 【abc】 040 050")
        self.assertIn("第1个时间戳无效：1:99", convert_seconds("129 1:99 050"))
        self.assertIn("第1个时间戳无效：086", convert_seconds("129 086"))

    def test_bonus_conversion_and_warnings(self):
        self.assertEqual(convert_bonus_seconds("1:10 1:20 0:55 0:40"),
                         "1:05\n0:50\n剩余时间请自行模拟\nTIME UP")
        self.assertEqual(convert_bonus_seconds("70 85 055"),
                         "110\n剩余时间请自行模拟\nTIME UP")
        self.assertEqual(convert_bonus_seconds("70 86 055"),
                         "111\n⚠️⚠️ 剩余时间较多，请自行模拟或换轴  ⚠️⚠️\nTIME UP")
        self.assertEqual(convert_bonus_seconds("90 21 001"),
                         "所有操作均在剩余时间之外，请自行模拟和调整")
        self.assertEqual(convert_bonus_seconds("90 90 055"), "剩余时间一致，无效转秒")
        self.assertEqual(convert_bonus_seconds("20 90 055"), "对方剩余时间无效")
        self.assertEqual(convert_bonus_seconds("90 91 055"), "我的剩余时间无效")


if __name__ == "__main__":
    unittest.main()

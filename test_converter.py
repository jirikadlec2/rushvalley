from unittest import TestCase
from converter import Converter
__author__ = 'Jiri'


class TestConvert(TestCase):
    def test_convert(self):
        c = Converter.create("MPS-6")
        self.assertAlmostEqual(c.convert(1, 29289144), -100006.02, 0)
        self.assertAlmostEqual(c.convert(2, 29289144), 4.6, 1)

    def test_gs3(self):
        c = Converter.create("GS3")
        self.assertAlmostEqual(c.convert(1, 1980031206), 0.078, 3)
        self.assertAlmostEqual(c.convert(2, 1980031206), 7.2, 1)
        self.assertAlmostEqual(c.convert(3, 1908601066), 0.0016, 3)

    def test_srsnr(self):
        c = Converter.create("SRS-Nr")
        raw = 46495837
        self.assertAlmostEqual(c.convert(1, raw), 0.0169, 3)
        self.assertAlmostEqual(c.convert(2, raw), 0.0206, 3)
        self.assertAlmostEqual(c.convert(3, raw), 0.387, 3)
        self.assertAlmostEqual(c.convert(3, 46766311), 0.381, 3)

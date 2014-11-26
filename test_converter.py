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

    def test_srsnr2(self):
        c = Converter.create("SRS-Nr")
        raw = 2200590363
        self.assertAlmostEqual(c.convert(1, raw), 0.0145, 3)
        self.assertAlmostEqual(c.convert(2, raw), 0.0026, 3)
        self.assertAlmostEqual(c.convert(3, raw), -9999)

    def test_srsni(self):
        c = Converter.create("SRS-Ni")
        raw = 2200590363
        self.assertAlmostEqual(c.convert(1, raw), 0.0145, 3)
        self.assertAlmostEqual(c.convert(2, raw), 0.0026, 3)
        self.assertEqual(c.convert(3, raw), -9999)

    def test_ecrn50(self):
        c = Converter.create("ECRN50Precip")
        raw = 177
        self.assertEqual(c.convert(1, raw), 177)

    def test_pyr(self):
        c = Converter.create("PYR")
        raw = 128
        self.assertAlmostEqual(c.convert(1, raw), 234.375, 2)
        self.assertAlmostEqual(c.convert(1, 32), 58.59, 2)

    def test_vp3(self):
        c = Converter.create("VP3")
        raw = 35782696
        self.assertAlmostEqual(c.convert(1, raw), 0.241, 3)
        self.assertAlmostEqual(c.convert(2, raw), 14.6, 1)

    def test_anemo(self):
        c = Converter.create("Anemo")
        raw = 411371075
        self.assertAlmostEqual(c.convert(1, raw), 289, 0)
        #self.assertAlmostEqual(c.convert(2, raw), 3.21, 2)
        #self.assertAlmostEqual(c.convert(3, raw), 9.8, 1)

        raw2 = 230935151
        self.assertAlmostEqual(c.convert(2, raw), 2.42, 2)
__author__ = 'Jiri'

import bitstring


class Converter(object):
    #create based on class name
    def create(sensor):
        if sensor == "MPS-6": return MPS6()
        if sensor == "GS3": return GS3()
        if sensor == "SRS-Nr": return SRSNr()
        assert 0, "The sensor type is not supported: " + sensor
    create = staticmethod(create)

    #convert raw bits from the port to the numeric raw value
    def port(raw_bits, start_bit, end_bit):
        #bits in the DECAGON specs are counted from right to left
        start = 31 - end_bit
        end = 32 - start_bit
        raw_bits = bitstring.BitArray(uint=raw_bits, length=32)
        subset = bitstring.BitArray(bin=raw_bits[start:end].bin)
        return subset.uint
    port = staticmethod(port)


#MPS-6 sensor (water potential, temperature)
class MPS6(Converter):
    def convert(self, response, raw_value):
        #MPS-6 water potential
        if response == 1:
            rw = self.port(raw_value, start_bit=0, end_bit=15)
            return (10 ** (0.0001 * rw)) / -10.20408
        #MPS-6 temperature
        elif response == 2:
            rt = self.port(raw_value, start_bit=16, end_bit=25)
            if rt <= 900:
                return float(rt - 400) / 10.0
            else:
                return ((900 + 5 *(rt - 900)) - 400) / 10


#GS-3 sensor (WWC, temperature, EC)
class GS3(Converter):
    def convert(self, response, raw_value):
        #volumnometric water content
        if response == 1:
                re = self.port(raw_value, start_bit=0, end_bit=11)
                ea = float(re) / 50.0
                wwc = 5.89e-6 * ea**3 - 7.62e-4 * ea**2 + 3.67e-2 * ea - 7.53e-2
                return wwc
        #temperature
        elif response == 2:
            rt = self.port(raw_value, start_bit=22, end_bit=31)
            if rt <= 900:
                return float(rt - 400) / 10.0
            else:
                return ((900 + 5 *(rt - 900)) - 400) / 10
        #bulk electrical conductivity
        elif response == 3:
            rec = self.port(raw_value, start_bit=12, end_bit=21)
            ec = float(10.0 ** float(rec / 215.0)) / 1000.0
            return ec


#SRS-Nr NDVI Field Stop (sensor #114)
class SRSNr(Converter):
    def convert(self, response, raw_value):
        #red spectral radiance (630 nm)
        if response == 1:
            r630 = self.port(raw_value, start_bit=1, end_bit=11)
            return (10 ** float(r630 /480.0)) / 10000.0
        #NIR spectral radiance (800 nm)
        elif response == 2:
            r800 = self.port(raw_value, start_bit=12, end_bit=22)
            return (10 ** float(r800 / 480.0)) / 10000.0
        #NDVI
        elif response == 3:
            ra = self.port(raw_value, start_bit=25, end_bit=31)
            orientation = self.port(raw_value, start_bit=23, end_bit=24)
            alpha = 100.0 / float(ra)
            #if the sensor returns alpha=1, use the predefined default alpha
            default_alpha = 1.86
            if alpha == 1:
                alpha = default_alpha

            r630 = self.port(raw_value, start_bit=1, end_bit=11)
            red = (10 ** float(r630 / 480.0)) / 10000.0
            r800 = self.port(raw_value, start_bit=12, end_bit=22)
            nir = (10 ** float(r800 / 480.0)) / 10000.0
            ndvi = float(alpha * nir - red)/float(alpha * nir + red)
            return ndvi


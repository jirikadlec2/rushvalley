#! /usr/bin/env python
__author__ = 'Jiri'

import bitstring
import math


####################################################################
# Base Class for Converting Decagon Data from raw data to SI Units #
# Expand this class for other sensors or data loggers              #
####################################################################
class Converter(object):
    #create a new converter based on class name
    def create(sensor):
        if sensor == "MPS-6":
            return MPS6()
        if sensor == "GS3":
            return GS3()
        if sensor == "SRS-Nr" or sensor == "SRS":
            return SRSNr()
        if sensor == "SRS-Ni":
            return SRSNi()
        if sensor == "PYR":
            return PYR()
        if sensor == "ECRN50Precip" or sensor == "ECRN50":
            return ECRN50Precip()
        if sensor == "VP3":
            return VP3()
        if sensor == "Anemo":
            return Anemo()
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

#################################################################
# MPS-6 sensor (water potential, temperature)                   #
#################################################################
class MPS6(Converter):
    def convert(self, response, raw_value):
        #MPS-6 water potential
        if response == 1:
            nodata = -999999
            rw = self.port(raw_value, start_bit=0, end_bit=15)
            if rw == 65535:
                return nodata
            else:
                return (10 ** (0.0001 * rw)) / -10.20408
        #MPS-6 temperature
        elif response == 2:
            nodata = -9999
            rt = self.port(raw_value, start_bit=16, end_bit=25)
            if rt == 1023:
                return nodata
            elif rt <= 900:
                return float(rt - 400) / 10.0
            else:
                return ((900 + 5 *(rt - 900)) - 400) / 10

##################################################################
# GS-3 sensor (WWC, temperature, EC)                             #
##################################################################
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

####################################################################
# SRS-Nr NDVI Field Stop (sensor #114)                             #
####################################################################
class SRSNr(Converter):
    def get_red(self, raw_value):
        r630 = self.port(raw_value, start_bit=1, end_bit=11)
        if r630 > 0:
            return (10 ** float(r630 /480.0)) / 10000.0
        else:
            return 0


    def get_nir(self, raw_value):
        r800 = self.port(raw_value, start_bit=12, end_bit=22)
        if r800 > 0:
            return (10 ** float(r800 / 480.0)) / 10000.0
        else:
            return 0


    def convert(self, response, raw_value):
        #red spectral radiance (630 nm)
        if response == 1:
            return self.get_red(raw_value)
        #NIR spectral radiance (800 nm)
        elif response == 2:
            return self.get_nir(raw_value)
        #NDVI
        elif response == 3:
            nodata = -9999
            ra = self.port(raw_value, start_bit=25, end_bit=31)
            orientation = self.port(raw_value, start_bit=23, end_bit=24)

            #if the sensor returns alpha=1, use the predefined default alpha
            #otherwise, get alpha from the measured incident radiation
            #print "raw_alpha: %s" % ra
            if ra >= 50 and ra <= 126:
                alpha = 100.0 / float(ra)
            else:
                alpha = 1.86
            #print "alpha: %s" % alpha

            red = self.get_red(raw_value)
            nir = self.get_nir(raw_value)
            if red > 0 and nir > 0:
                return float(alpha * nir - red)/float(alpha * nir + red)
            else:
                return nodata

####################################################################
# SRS-Ni (sensor #115)                                             #
####################################################################
class SRSNi(Converter):

    #orientation: 0 up-facing, 1 down-facing,
    #             2 up-facing, 3 bad reading
    def get_orientation(self, raw_value):
        return self.port(raw_value, start_bit=23, end_bit=24)


    def get_red(self, raw_value):
        orientation = self.get_orientation(raw_value)
        nodata = -9999
        if orientation == 3:
            return nodata
        r630 = self.port(raw_value, start_bit=1, end_bit=11)
        print "r630: %s" % r630
        if r630 == 0:
            return 0
        return (10 ** float(r630 /480.0)) / 10000.0


    def get_nir(self, raw_value):
        orientation = self.get_orientation(raw_value)
        nodata = -9999
        if orientation == 3:
            return nodata
        r800 = self.port(raw_value, start_bit=12, end_bit=22)
        print "r800: %s" % r800
        if r800 == 0:
            return 0
        return (10 ** float(r800 / 480.0)) / 10000.0


    def convert(self, response, raw_value):
        nodata = -9999
        if raw_value == 0:
            return nodata
        if response == 1:
            return self.get_red(raw_value)
        elif response == 2:
            return self.get_nir(raw_value)
        elif response == 3:
            ra = self.port(raw_value, start_bit=25, end_bit=31)
            #check valid raw alpha is in range [50, 126]
            if ra >= 50 and ra <= 126:
                alpha = float(ra) / 100.0
            else:
                alpha = 100.0 / float(ra)

            red = self.get_red(raw_value)
            nir = self.get_nir(raw_value)

            orientation = self.get_orientation(raw_value)
            if orientation == 2:
                alpha = red / nir
            print "alpha: %s" % alpha

            if red > 0 and nir > 0:
                return float(alpha * nir - red)/float(alpha * nir + red)
            else:
                return nodata


######################################################################
# ECRN-50 Precipitation                                              #
######################################################################
class ECRN50Precip(Converter):
    def convert(self, response, raw_value):
        return raw_value

######################################################################
# PYR Solar Radiation                                                #
######################################################################
class PYR(Converter):
    def convert(self, response, raw_value):
        return raw_value * (1500.0/4096.0) * 5.0

######################################################################
# VP-3 Humidity/Air Temperature                                      #
######################################################################
class VP3(Converter):

    def get_temperature(self, raw_value):
        rt = self.port(raw_value, start_bit=16, end_bit=25)
        if rt <= 900:
            return float(rt - 400) / 10.0
        else:
            return ((900 + 5 *(rt - 900)) - 400) / 10

    def convert(self, response, raw_value):
        #validity check, if invalid return NoData
        if raw_value == 0:
            return -9999.0
        #vapor pressure - relative humidity
        if response == 1:
            re = self.port(raw_value, 0, 15)
            ew = re / 100.0
            t = self.get_temperature(raw_value)
            saturated_vp = 0.611 * math.e ** ((17.502 * t) / (240.97+t))
            return float(ew) / float(saturated_vp)
        #temperature
        elif response == 2:
            return self.get_temperature(raw_value)

########################################################################
# Sonic Anemo Wind - NEED CHECK!!!                                     #
########################################################################
class Anemo(Converter):
    def convert(self, response, raw_value):

        detect_flag = self.port(raw_value, 0, 0)
        if detect_flag == 0:
            return -9999.0

        if response == 1:
            d = self.port(raw_value, 1, 9)
            return d

        elif response == 2:
            rs = self.port(raw_value, 20, 29)
            #print rs
            return 1.006 * rs / 10.0

        elif response == 3:
            rg = self.port(raw_value, 10, 19)
            #print rg
            return 1.006 * rg / 10.0


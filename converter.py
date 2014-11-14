__author__ = 'Jiri'
#converts the raw byte to the real sensor values

import bitstring


def port_response(raw, start_bit, end_bit):
    #bits in the DECAGON specs are counted from right to left
    start = 31 - end_bit
    end = 32 - start_bit
    print "start: %s end: %s" % (start, end)

    raw_bits = bitstring.BitArray(uint=raw, length=32)
    subset = bitstring.BitArray(bin=raw_bits[start:end].bin)
    return subset.uint


def convert(raw_value, sensor, response):
    #MPS-6
    if sensor == 'MPS-6':

        #MPS-6 water potential
        if response == 1:
            rw = port_response(raw_value, start_bit=0, end_bit=15)
            return (10 ** (0.0001 * rw)) / -10.20408

        #MPS-6 temperature
        elif response == 2:
            rt = port_response(raw_value, start_bit=16, end_bit=25)
            if rt <= 900:
                return float(rt - 400) / 10.0
            else:
                return ((900 + 5 *(rt - 900)) - 400) / 10

    #GS3 Moisture/Temp/EC
    elif sensor == 'GS3':

        #GS3 soil moisture WWC
        if response == 1:
            re = port_response(raw_value, start_bit=0, end_bit=11)
            ea = float(re) / 50.0
            wwc = 5.89e-6 * ea**3 - 7.62e-4 * ea**2 + 3.67e-2 * ea - 7.53e-2
            return wwc
        #GS3 temperature
        elif response == 2:
            rt = port_response(raw_value, start_bit=22, end_bit=31)
            if rt <= 900:
                return float(rt - 400) / 10.0
            else:
                return ((900 + 5 *(rt - 900)) - 400) / 10
        #GS3 bulk electrical conductivity
        elif response == 3:
            rec = port_response(raw_value, start_bit=12, end_bit=21)
            ec = (10.0 ** float(rec / 215)) / 1000.0
            return ec





if __name__ == '__main__':
    print port_response(1917014247, 0, 11)
    print port_response(1917014247, 22, 31)
    print port_response(1917014247, 12, 21)
    print port_response(29289144, 0, 15)
    print port_response(29289144, 16, 25)

    #tests
    water_potential = convert(43414879, 'MPS-6', 1)
    print "MPS-6 water potential:%s" % water_potential
    soil_temperature = convert(43414879, 'MPS-6', 2)
    print "MPS-6 temperature:%s" % soil_temperature
    soil_moisture = convert(2764071169, 'GS3', 1)
    print "GS3 soil moisture:%s" % soil_moisture
    gs3_temperature = convert(2764071169, 'GS3', 2)
    print "GS3 temperature:%s" % gs3_temperature
    gs3_ec = convert(2764071169, 'GS3', 3)
    print "GS3 electric conductivity:%s" % gs3_ec


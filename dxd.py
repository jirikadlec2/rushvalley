__author__ = 'Jiri'

from lxml import etree

#reads the dxd file and checks the response of the file
#returns a dictionary with raw dates and raw values
def read_dxd(dxd_file, port):
    txt = "no data found"
    doc = etree.parse(dxd_file)
    root = doc.getroot()
    for element in root.iter():
        if 'Data' in element.tag:
            nrow = int(element.get('scans'))
            print nrow
            txt = element.text

    #now parse txt to two lists dates, vals
    result = {"dates": [], "vals": []}
    for line in txt.splitlines():
        if line.strip() == "":
            continue
        items = line.split(",")
        if port > len(items):
            raise ValueError('File %s does not have data from port %s' %(dxd_file, port))
        result["dates"].append(int(items[0]))
        result["vals"].append(int(items[port]))
    return result


if __name__ == '__main__':
    txt = read_dxd('C:\\jiri\\Dropbox\\BYU\\hydroinformatics\\project\\decagon_files\\5G0E3562new.dxd', 1)
    print txt["dates"]
import matplotlib.pyplot as plt
import numpy as np
import urllib
import matplotlib.dates as mdates

def graph_data(stock):
    stock_price_url = 'http://chartapi.finance.yahoo.com/instrument/1.0/'+stock+'/chartdata;type=quote;range=10y/csv'

    source_code = urllib.request.urlopen(stock_price_url).read().decode()

    stock_data = []
    split_source = source_code.split('\n')

    for line in split_source:
        split_line = line.split(',')
        if len(split_line) == 6:
            if 'values' not in line:
                stock_data.append(line)

    date, closep, highp, lowp, openp, volume = np.loadtxt(stock_data,
                                                          delimiter=',',
                                                          unpack=True,
                                                          converters={0:bytespdate2num('%Y%m%d')})



graph_data('TSLA')


#x = [1,2,3,4,5]
#y = [2,4,6,8,10]
#x2 = [1,2,3,4,5]
#y2 = [3,6,9,12,15]
#plt.plot(x, y, label='Data 1')
#plt.plot(x2, y2, label='Data 2')
#plt.xlabel('Numbers')
#plt.ylabel('Values')
#plt.title('Graph')
#plt.legend()
#plt.show()

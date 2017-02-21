from stockex import stockwrapper as sw
import pandas as pd
import numpy as np

class stockDataManager(object):
	"""docstring for stockDataManager"""

	data = sw.YahooData()

	def __init__(self):
		super(stockDataManager, self).__init__()

	def getStockCurentData(self,stock):
		# Print Current data of a Stock
		print(self.data.get_current([stock]))
	
	def getStockHistoricalData(self,stock,sd, ed):
		result = self.data.get_historical(stock, ['Date','Open', 'Close', 'High', 'Low'],
                          startDate=sd, endDate=ed, limit=500000)
		return result

	def loadStockList(self):
		df = pd.read_csv('companylist.csv')
		numpyMatrix = df.loc[:,['Symbol']].values
		stockNameList = [item[0] for item in numpyMatrix]
		return stockNameList


	def fetchAllStockDataFromYQL(self,startDate,endDate):
		dateRange = pd.date_range(startDate,endDate)
		stockList = self.loadStockList()
		df = pd.DataFrame(np.zeros(len(stockList)*len(dateRange)).reshape((-1,len(stockList))),index=dateRange, columns=[stockList])
		dateRangeInString = dateRange.map(lambda x: x.strftime('%Y-%m-%d'))
		print(dateRangeInString)
		#print(df)
		#for stock in self.loadStockList:
		#	historicals = self.getStockHistoricalData(stock,startDate,endDate)


		pass







if __name__ == "__main__":
	sm = stockDataManager()
	sm.fetchAllStockDataFromYQL('2013-01-01','2013-01-03')
	#result = sm.getStockHistoricalData("EBAY",'2013-01-01','2013-01-03')
	#print(result[0]["Date"])
	#data = sm.getStockHistoricalData('EBAY')
    # for item in data:
    # 	print(item['Date'] + '\t' + item['Close'])
    #sm.loadStockList()

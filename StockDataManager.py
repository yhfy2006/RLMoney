from stockex import stockwrapper as sw
import pandas as pd
import numpy as np
import os
import time

DATADIR = 'data'

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
		print('Start fetching Stock data from '+startDate + " to "+endDate)
		dateRange = pd.date_range(startDate,endDate)
		dateRangeInStrings = dateRange.map(lambda x: x.strftime('%Y-%m-%d'))
		stockList = self.loadStockList()
		df = pd.DataFrame(np.zeros(len(stockList)*len(dateRange)).reshape((-1,len(stockList))),index=dateRangeInStrings, columns=[stockList])
		stockList = self.loadStockList()
		for i in range(len(stockList)):
			stock =stockList[i]
			print("processingStock: " +stock + " with index of "+ str(i))
			try:
				historicals = self.getStockHistoricalData(stock, startDate, endDate)
			except:
				print("[Error]---->Stock "+stock+" doesn't have values in the time peroid")
				continue
			for dayHistory in historicals:
				dateStr =dayHistory['Date']
				closePrice = dayHistory['Close']
				df[stock][dateStr] = closePrice
			# for each ip 2000 querys perhour. not enough for our use case, so sleep for every call.
			time.sleep(1.5)
		file_name = DATADIR+"/[Close]"+startDate+"|"+endDate+".csv"
		df.to_csv(file_name)
		return df

	def loadData(self,startDate,endDate):
		fileName = DATADIR+"/[Close]"+startDate+"|"+endDate+".csv"
		if os.path.exists(fileName):
			df = pd.read_csv(fileName)
		else:
			df = self.fetchAllStockDataFromYQL(startDate,endDate)
		dataMatrix = df.as_matrix()
		return dataMatrix







if __name__ == "__main__":
	sm = stockDataManager()
	df = pd.read_csv('data/[Close]2015-01-01|2015-12-31.csv',header=None)
	df = df.iloc[1:,1:].astype(float)
	a = df.loc[~df.apply(lambda row: (row==0).all(), axis=1)]
	for column_name,column in a.transpose().iterrows():
		print (column.values)



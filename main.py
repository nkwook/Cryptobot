import pyupbit
from pyupbit import Upbit
import time
import pandas as pd
import numpy as np

access_key = 'UWkLbJD9S5nFjdiAIlCuz9PcqWHONM42sv65UK1O'
secret_key = 'Xu1ynHbeiFqFubMz08hT1icklD7HEuVVY9aJjvgP'
upbit=Upbit(access_key, secret_key)
# print(res.json())

def rsi_eval(df, rsi_number, count):
	rsi=0
	diff=[]
	
	open=df['open']
	close=df['close']

	for i in range(len(df.index)):
		diff.append(close.iloc[i]-open.iloc[i])

	au=pd.Series(diff)
	ad=pd.Series(diff)
	
	au[au<0] = 0 #remove ad
	ad[ad>0] = 0 #remove au

	_gain = au.ewm(com = rsi_number-1, min_periods = count).mean() #Exponentially weighted average
	_loss = ad.abs().ewm(com = rsi_number-1, min_periods = count).mean()

	RS = _gain/_loss
	# print(RS)
	rsi = 100-(100 / (1+RS.iloc[-1]))

	print(rsi)
	# print(df.tail())
	return rsi

def get_data(tickers, count):
	request_count=0
	request_limit_per_second=10

	time_start=time.time()

	rsi_dictionary={}

	df=pyupbit.get_ohlcv('KRW-ETH', interval="minute10", count=count)
	# print(df[['open', 'close']])
	new_df= df.iloc[::-1]
	# new_df=df

	rsi=rsi_eval(new_df[['open', 'close']], 14, count)

			

	for ticker in tickers:
		print(ticker)
		if(request_count<request_limit_per_second):
			df=pyupbit.get_ohlcv(ticker, interval="minute10", count=count)
			# print(df[['open', 'close']])
			new_df= df.iloc[::-1]
			# new_df=df
			rsi=rsi_eval(new_df[['open', 'close']], 14, count)
			rsi_dictionary[ticker]=rsi

			request_count+=1
		else:
			if(1> time.time()-time_start): # to avoid time limit
				time.sleep(1-time.time()-time_start)
			request_count=0
			time_start=time.time()

	return rsi_dictionary
		
		
			 
	
def main():
	# quotation
	tickers= pyupbit.get_tickers(fiat="KRW") # get 117 tickers

	while True:
		print("main")
		# rsiEval(tickers, 500)

		rsi_dic=get_data(tickers, 14)

		sorted_dic=dict(sorted(rsi_dic.items(), key=lambda item: item[1]))
		print(sorted_dic)
		# print(upbit.get_balance("KRW-BTC"))
		# balance=upbit.get_balance("KRW-BTG")
		
		# time.sleep(3)
		break

if __name__=="__main__":
	main()




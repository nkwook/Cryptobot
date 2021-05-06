
import pyupbit
from pyupbit import Upbit
import time
import pandas as pd
import numpy as np
from datetime import datetime
from pytz import timezone

access_key = 'UWkLbJD9S5nFjdiAIlCuz9PcqWHONM42sv65UK1O'
secret_key = 'Xu1ynHbeiFqFubMz08hT1icklD7HEuVVY9aJjvgP'
upbit=Upbit(access_key, secret_key)

def balance_check():
	krw=0
	owning_coin_list=[]
	balances=upbit.get_balances()
	for balance in balances:
		# print(balance)
		if(balance['currency']=='KRW'):
			krw=balance['balance']
			# print(krw)
			continue
		ticker='KRW-'+balance['currency']
		current_price=pyupbit.get_current_price(ticker)
		earning=float(current_price)/float(balance['avg_buy_price'])
		#익절손절
		if earning<0.8 or earning>2.0:
			upbit.sell_market_order(ticker, balance['balance'])
			print(ticker+" "+earning+"의 earning으로 매도")
		else:
			owning_coin_list.append(ticker)
	
	return float(krw), owning_coin_list

def sell_all():
	balances=upbit.get_balances()
	for balance in balances:
		# print(balance)
		if(balance['currency']=='KRW'):
			continue
		ticker='KRW-'+balance['currency']
		current_price=pyupbit.get_current_price(ticker)
		earning=float(current_price)/float(balance['avg_buy_price'])
		upbit.sell_market_order(ticker, balance['balance'])
		print(ticker+" "+str(earning)+"의 earning으로 매도")
	return 


def get_vb_data(tickers):
	request_count=0
	request_limit_per_second=10

	time_start=time.time()
	vb_dictionary={}
	
	print("현재 시간: " +str(datetime.now(timezone('Asia/Seoul'))))

	for ticker in tickers:
		# print(ticker)
		if(request_count<request_limit_per_second):
			# df=pyupbit.get_ohlcv(ticker, interval="day", count=2)
			df=pyupbit.get_daily_ohlcv_from_base(ticker, base=16)
			df=df.iloc[::-1]
			previous_data=df.iloc[1]
			current_price=pyupbit.get_current_price(ticker)
			
			diff=(current_price-previous_data['close'])/(previous_data['high']-previous_data['low'])
			# print(diff)

			vb_dictionary[ticker]=diff

			request_count+=1
		else:
			if(1> time.time()-time_start): # to avoid time limit
				time.sleep(1-time.time()-time_start)
			request_count=0
			time_start=time.time()
	
	return vb_dictionary


def get_k():
	return 0.5

def main():
	# quotation
	tickers= pyupbit.get_tickers(fiat="KRW") # get 117 tickers

	while True:
		# print("main")
		krw, owning_list=balance_check()
		print("잔고: "+ str(krw) + ", 보유 코인: "+ str(owning_list))
		buy_success=False
		# get_vb_data(tickers)
		if krw >6500: 
			vb_dictionary=get_vb_data(tickers)
			sorted_dic=dict(sorted(vb_dictionary.items(), key=lambda item: item[1]))
			print(list(sorted_dic)[-1], sorted_dic[list(sorted_dic)[-1]])
			for high_vb_coin in reversed(sorted_dic):
				# print(high_vb_coin, sorted_dic[high_vb_coin])
				if high_vb_coin not in owning_list and sorted_dic[high_vb_coin]>get_k():
					#산다
					result=upbit.buy_market_order(high_vb_coin, 6500)
					# if result['error']==None: 
					# error handling 일단 넘어가고.. 
					print(high_vb_coin+" 6500원 매수 완료, vb값은 "+str(sorted_dic[high_vb_coin]))
					break
			print("조건을 만족하는 코인이 없습니다")
		else:
			print("매수 가능 현금이 없습니다")
		
		# time.sleep(300)
		t=datetime.now(timezone('Asia/Seoul'))
		if(t.hour==15 and t.minute>55):
			sell_all()
		

		time.sleep(600)
		

if __name__=="__main__":
	main()

#!/usr/bin/python
#_*_coding:utf-8_*_

import requests

def query_stock(gid):
	url = "http://web.juhe.cn:8080/finance/stock/hs"
	params = {
		'gid':gid,
		'key':'879274ab3fd65eb91d3c21abdc77736b'
	}
	r = requests.get(url,params=params)
	query_result = ''
	if r.status_code == 200:
		r_data = r.json()
		error_code = r_data.get('error_code')
		if error_code == 0:
			result = r_data.get('result')
			data = result[0].get('data')
			name = data.get('name')
			now_price = data.get('nowPri')
			query_result = '当前股票{}({})最新价格为 {}'.format(name,gid,now_price)
		elif error_code == 202101:
			query_result = '参数错误，确认你的输入正确'
		elif error_code == 202102:
			query_result = '查询不到结果，请确认你的输入存在'
		elif error_code == 202103:
			query_result = '网络异常'
		else:
			query_result = '特殊异常，请确认你的API接口正常'
	else:
		query_result = '请求错误，错误代码{}'.format(r.status_code)
	return query_result

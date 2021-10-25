#!/usr/local/bin/python3

import json
import matplotlib.pyplot as plt
import requests
import numpy as np
import pandas as pd
# import cufflinks as cf
import pandas_bokeh as pb
from datetime import date
from scipy.signal import savgol_filter

import datetime


url = {}
population = {}
lockdowns = [(datetime.date(2021,1,5),datetime.date(2021,4,12)), (datetime.date(2020,11,5),datetime.date(2020,12,2)), (datetime.date(2020,3,23),datetime.date(2020,7,4))]
verbose = False
# cf.set_config_file(sharing='public',theme='white',offline=True)
pd.set_option('plotting.backend', 'pandas_bokeh')



def init_urls():
	url['Plymouth'] = 'https://api.coronavirus.data.gov.uk/v1/data?filters=areaType=utla;areaName=Plymouth&structure=%7B%22areaType%22:%22areaType%22,%22areaName%22:%22areaName%22,%22areaCode%22:%22areaCode%22,%22date%22:%22date%22,%22newCasesBySpecimenDate%22:%22newCasesBySpecimenDate%22,%22cumCasesBySpecimenDate%22:%22cumCasesBySpecimenDate%22%7D&format=json'
	url['Devon'] = 'https://api.coronavirus.data.gov.uk/v1/data?filters=areaType=utla;areaName=Devon&structure=%7B%22areaType%22:%22areaType%22,%22areaName%22:%22areaName%22,%22areaCode%22:%22areaCode%22,%22date%22:%22date%22,%22newCasesBySpecimenDate%22:%22newCasesBySpecimenDate%22,%22cumCasesBySpecimenDate%22:%22cumCasesBySpecimenDate%22%7D&format=json'
	url['England'] = 'https://api.coronavirus.data.gov.uk/v1/data?filters=areaType=nation;areaName=England&structure=%7B%22areaType%22:%22areaType%22,%22areaName%22:%22areaName%22,%22areaCode%22:%22areaCode%22,%22date%22:%22date%22,%22newCasesBySpecimenDate%22:%22newCasesBySpecimenDate%22,%22cumCasesBySpecimenDate%22:%22cumCasesBySpecimenDate%22%7D&format=json'
	# url['Scotland'] = 'https://api.coronavirus.data.gov.uk/v1/data?filters=areaType=nation;areaName=Scotland&structure=%7B%22areaType%22:%22areaType%22,%22areaName%22:%22areaName%22,%22areaCode%22:%22areaCode%22,%22date%22:%22date%22,%22newCasesBySpecimenDate%22:%22newCasesBySpecimenDate%22,%22cumCasesBySpecimenDate%22:%22cumCasesBySpecimenDate%22%7D&format=json'
	# url['London'] = 'https://api.coronavirus.data.gov.uk/v1/data?filters=areaType=region;areaName=London&structure=%7B%22areaType%22:%22areaType%22,%22areaName%22:%22areaName%22,%22areaCode%22:%22areaCode%22,%22date%22:%22date%22,%22newCasesBySpecimenDate%22:%22newCasesBySpecimenDate%22,%22cumCasesBySpecimenDate%22:%22cumCasesBySpecimenDate%22%7D&format=json'

	population['Plymouth'] = 264200
	population['Devon'] = 1194166
	population['England'] = 67886011
	population['Scotland'] = 5460000
	population['London'] = 8982000

def fetch_data(region):
	post_return = requests.get(url[region])
	post_data = json.loads(post_return.text)
	if verbose:
		print(post_data)
	return post_data['data']

def fetch_parse_data(region):
	post_data = fetch_data(region)
	df_data = {}
	df_data['date'] = [datetime.datetime.fromisoformat(d['date']) for d in post_data]
	cases = [d['newCasesBySpecimenDate'] for d in post_data]
	df_data[region+'_cases'] = cases
	# df_data[region+'_cases'] = average_smoothing(cases, window_size=7)
	df = pd.DataFrame(data=df_data)
	if verbose:
		print(df)
	return(df)

def average_smoothing(y, window_size=3):
	return savgol_filter(y, window_size, 3)

def plot_data(df, highlights=lockdowns, output_figure='images/plymouth_covid_graph.png'):
	# plt.figure()
	df_ = df[df.columns[~df.columns.isin(['England_cases'])]]

	df_.plot(x='date', figsize=(12,8))
	for h in highlights:
		plt.axvspan(h[0], h[1], color='grey', alpha=0.5)
	plt.ylabel('Number of Cases') 
	plt.title('Covid Cases')
	plt.savefig(output_figure)
	pb.output_file(output_figure[:-3]+'.html')

def plot_data_pht(df, highlights=lockdowns, output_figure='images/plymouth_covid_graph_pht.png'):
	df_ = data_to_pht(df)
	df_.plot(x='date', figsize=(12,8))
	for h in highlights:
		plt.axvspan(h[0], h[1], color='grey', alpha=0.5)
	plt.ylabel('Number of Cases Per 100,000') 
	plt.title('Covid Cases Per Hundered Thousand Local Population')
	plt.savefig(output_figure)
	pb.output_file(output_figure[:-3]+'.html')


def data_to_pht(df):
	for region in url:
		df[region+'_cases'] = df[region+'_cases'].div(population[region]).mul(100000)
	return df

def	update_index(filename, date=date.today().strftime("%d %B %Y")):

	lines = open(filename, 'r').readlines()
	lines[-1] = 'Last updated on: {}'.format(date)
	open(filename, 'w').writelines(lines)

def main():
	df = pd.DataFrame(data={'date':[]})
	data = {}
	init_urls()

	for region in url:
		data[region] = fetch_parse_data(region)
		df = (pd.merge(df, data[region], on='date', how='outer'))
	plot_data(df)
	df.to_csv('data_dump.csv')
	plot_data_pht(df)
	update_index('index.md')



if __name__ == "__main__":
	main()

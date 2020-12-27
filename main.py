#!/usr/local/opt/python/libexec/bin/python

import json
import matplotlib.pyplot as plt
import requests
import numpy as np
import pandas as pd
from scipy.signal import savgol_filter

import datetime

url = {}
population = {}

lockdowns = [(datetime.date(2020,11,5),datetime.date(2020,12,2)), (datetime.date(2020,3,23),datetime.date(2020,7,4)),]
verbose = False


def init_urls():
	url['Plymouth'] = 'https://api.coronavirus.data.gov.uk/v1/data?filters=areaType=utla;areaName=Plymouth&structure=%7B%22areaType%22:%22areaType%22,%22areaName%22:%22areaName%22,%22areaCode%22:%22areaCode%22,%22date%22:%22date%22,%22newCasesBySpecimenDate%22:%22newCasesBySpecimenDate%22,%22cumCasesBySpecimenDate%22:%22cumCasesBySpecimenDate%22%7D&format=json'
	url['Devon'] = 'https://api.coronavirus.data.gov.uk/v1/data?filters=areaType=utla;areaName=Devon&structure=%7B%22areaType%22:%22areaType%22,%22areaName%22:%22areaName%22,%22areaCode%22:%22areaCode%22,%22date%22:%22date%22,%22newCasesBySpecimenDate%22:%22newCasesBySpecimenDate%22,%22cumCasesBySpecimenDate%22:%22cumCasesBySpecimenDate%22%7D&format=json'
	# url['England'] = 'https://api.coronavirus.data.gov.uk/v1/data?filters=areaType=nation;areaName=England&structure=%7B%22areaType%22:%22areaType%22,%22areaName%22:%22areaName%22,%22areaCode%22:%22areaCode%22,%22date%22:%22date%22,%22newCasesBySpecimenDate%22:%22newCasesBySpecimenDate%22,%22cumCasesBySpecimenDate%22:%22cumCasesBySpecimenDate%22%7D&format=json'

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
	df_data[region+'_cases'] = average_smoothing(cases, window_size=7)
	df = pd.DataFrame(data=df_data)
	if verbose:
		print(df)
	return(df)

def average_smoothing(y, window_size=3):
	return savgol_filter(y, window_size, 3)

def plot_data(df, highlights=lockdowns, output_figure='images/plymouth_covid_graph.png'):
	df.plot(x='date')
	for h in highlights:
		plt.axvspan(h[0], h[1], color='grey', alpha=0.5)
	plt.ylabel('Number of Cases') 
	plt.title('Covid Cases')
	plt.savefig(output_figure)

def main():
	df = pd.DataFrame(data={'date':[]})
	data = {}
	init_urls()

	for region in url:
		data[region] = fetch_parse_data(region)
		df = (pd.merge(df, data[region], on='date', how='outer'))
	plot_data(df)

if __name__ == "__main__":
	main()
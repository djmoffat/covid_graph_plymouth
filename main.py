#! /usr/local/opt/python/libexec/bin/python

import json
import matplotlib.pyplot as plt
import requests
import numpy as np
import datetime


plym_url = 'https://api.coronavirus.data.gov.uk/v1/data?filters=areaType=utla;areaName=Plymouth&structure=%7B%22areaType%22:%22areaType%22,%22areaName%22:%22areaName%22,%22areaCode%22:%22areaCode%22,%22date%22:%22date%22,%22newCasesBySpecimenDate%22:%22newCasesBySpecimenDate%22,%22cumCasesBySpecimenDate%22:%22cumCasesBySpecimenDate%22%7D&format=json'
lockdowns = [(datetime.date(2020,11,5),datetime.date(2020,12,2)), (datetime.date(2020,3,23),datetime.date(2020,7,4)),]
verbose = False

def fetch_data():
	post_return = requests.get(plym_url)
	post_data = json.loads(post_return.text)
	# print(post_data)
	return post_data

def parse_data(data):
	date_data = [datetime.datetime.fromisoformat(d['date']) for d in data]
	cases_data = [d['newCasesBySpecimenDate'] for d in data]
	if verbose:
		for date,case in sorted(zip(date_data, cases_data), key = lambda x: x[0]):
			print(date,case)
	cases_data = average_smoothing(cases_data, window_size=7)
	return(date_data, cases_data)

def average_smoothing(y, window_size=3):
	from scipy.signal import savgol_filter
	return savgol_filter(y, window_size, 3)

def plot_data(data, highlights, output_figure='images/plymouth_covid_graph.png'):
	plt.plot(data[0], data[1])
	plt.xticks(rotation=45)
	for h in highlights:
		plt.axvspan(h[0], h[1], color='grey', alpha=0.5)
	plt.ylim(bottom=0)
	plt.xlabel('Date') 
	plt.ylabel('Number of Cases') 
	plt.title('Plymouth Covid Cases')
	plt.legend(["Number of New Cases Per Day", "National Locks Downs"]);
	plt.gcf().autofmt_xdate()
	plt.savefig(output_figure)

def main():
	data = fetch_data()
	data = parse_data(data['data'])
	plot_data(data, lockdowns)

if __name__ == "__main__":
	main()
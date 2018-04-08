'''
This is a collection of functions to create and deal with word embeddings and statistics.
'''

import collections
import logging
import os
import pdb
import random
import shutil
import itertools
import json
from matplotlib.ticker import FormatStrFormatter
from matplotlib.mlab import PCA


import enchant
import gensim
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from nltk.corpus import stopwords


class MySentences(object):
	#Class to read in files in a folder, each one line by line, sentence by sentence
	def __init__(self, dirname):
		self.dirname = dirname

	def __iter__(self):
		for fname in os.listdir(self.dirname):
			for line in open(os.path.join(self.dirname, fname)):
				yield line.split()

def gender_score(model, subreddit, defaultdict):
	"""Computes gender score for the model, saves in dict. 'subreddit' is either a subreddit or a folder name ending with '/'"""
	error_words = []
	stops = set(stopwords.words('english'))
	en_US = enchant.Dict('en_US')
	calc_list = []
	number_of_top_words = 1000
	tfidf_words = collections.defaultdict(list)
	if subreddit.endswith('/'): # in this case subreddit = cluster folder
		with open(subreddit+'directory_tfidf.json','r') as f:
			tfidf_words.update(json.load(f))
	else:
		with open(subreddit+'_tfidf.json','r') as f:
			tfidf_words.update(json.load(f))
	top_words = []
	for x, y in itertools.islice(sorted(tfidf_words.items(), key=lambda t: t[1],  reverse=True), number_of_top_words): # X*number to have enough even when stop words are discarded
		top_words.append(x)
	i = 0
	for word in top_words:
		if word.lower() not in stops and i < number_of_top_words: #normal version
			try:
				i += 1
				value = calculate_gender_score_value(model, word)
				round_value = float('%.5f' % round(value, 5)) # rounds to X decimals
				defaultdict[round_value].append(word)
				calc_list.append(value)
			except:
				error_words.append(word)
	median = calculate_median(calc_list)
	print('Error words: '+str(error_words))
	return median

def calculate_gender_score_value(model, word):
	return  np.dot(model.wv[word], model.wv['he']) / (np.linalg.norm(model.wv[word]) * np.linalg.norm(model.wv['he'])) - np.dot(model.wv[word], model.wv['she']) / (np.linalg.norm(model.wv[word]) * np.linalg.norm(model.wv['she']))

def calculate_median(list):
	"""Calculates the median of a list"""
	list.sort()
	median = 0
	if len(list)%2 == 0:
		index1 = int(len(list) /2)
		index2 = int(len(list) /2) +1
		median = (list[index1] + list[index2]) / 2
	else:
		median = list[int(len(list)/2)]
	return median

def vector_similarity(vec1,vec2):
	"""Computes the similarity between two numpy array vectors"""
	value = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
	return value

def evaluate_model_accuracy(accuracy_list):
	sum_corr = len(accuracy_list[-1]['correct'])
	sum_incorr = len(accuracy_list[-1]['incorrect'])
	total = sum_corr + sum_incorr
	percent = lambda a: a / total * 100
	print('Total sentences: {}, Correct: {:.2f}%, Incorrect: {:.2f}%'.format(total, percent(sum_corr), percent(sum_incorr)))

def gender_classification_test(model):
	"""Tests a model's classification accuracy for a list of 206 gender specific words"""
	male_list = []
	female_list = []
	success_count = 0
	with open('wordlist_gender_male.txt','r') as f:
		male_list.extend(f.read().splitlines())
	with open('wordlist_gender_female.txt','r') as f:
		female_list.extend(f.read().splitlines())
	total_words = len(male_list) + len(female_list)
	for word in male_list:
		if word in model.wv.vocab:
			sim_male = vector_similarity(model[word],model['he'])
			sim_female = vector_similarity(model[word],model['she'])
			if sim_male > sim_female:
				success_count += 1
	for word in female_list:
		if word in model.wv.vocab:
			sim_male = vector_similarity(model[word],model['he'])
			sim_female = vector_similarity(model[word],model['she'])
			if sim_male < sim_female:
				success_count += 1
	
	success_percentage = 100 / total_words * success_count
	print(str(success_percentage)+'% successfully classified. ('+str(success_count)+'/'+str(total_words)+' words)')
	
def plot_histogram(d, median, name):
	"""Plots a histogram with values from a defaultdict"""
	values = []
	for item in d.keys():
		values.extend(len(d.get(item)) * [item])
	fig, ax = plt.subplots()
	counts, bins, patches = ax.hist(sorted(values), bins=np.arange(-0.3,0.3,0.025),facecolor='g',align='right')
	print('Bins: ')
	print(bins)
	print('Patches: ')
	print(patches)
	twentyfifth, seventyfifth = np.percentile(sorted(bins), [49.99, 50.01]) #changes colour of either side, adapt when steps above change
	for patch, rightside, leftside in zip(patches, bins[1:], bins[:-1]):
		if rightside < 0:
			patch.set_facecolor('pink')
		elif leftside > 0:
			patch.set_facecolor('red')
	tick_bins = np.arange(-0.3,0.3+0.025,0.025)
	ax.set_xticks(tick_bins[0::4])
	ax.xaxis.set_major_formatter(FormatStrFormatter('%0.1f'))
	plt.ylabel('Number of words')
	plt.xlabel('Gender Bias Score')
	#	manually create legend
	pink_patch = mpatches.Patch(color='pink', label='Female')
	green_patch = mpatches.Patch(color='green', label='Neutral')
	red_patch = mpatches.Patch(color='red', label='Male')
	plt.legend(handles=[pink_patch, green_patch, red_patch])
	#	save the image
	plt.savefig(str(name)+'.png',dpi=300)
	#	close image to avoid conflicts
	plt.close('all')

def score_and_plot(model,subreddit,name):
	"""Computes gender score, creates and saves a plot histogram"""
	d = collections.defaultdict(list)
	med = gender_score(model,subreddit,d)
	save_dir_dict = name.replace('plots','stats')
	save_dir_dict = save_dir_dict.replace('_plot','_stats.json')
	with open(save_dir_dict, 'w') as f:
		json.dump(d, f, indent=4)
	print(name+' Median: '+str(med))
	plot_histogram(d, med, name)

def train_word_embedding():
	''' Trains a word embedding with the parameters explained in the thesis'''
	sentences = MySentences('../reddit_crawl/wem_data') # a memory-friendly iterator
	model = gensim.models.Word2Vec(sentences,size=300,sg=1,workers=4)
	#Save the model
	if ('model' in locals()):
		model.save('word_embedding_reddit_d300_sg_4workers')
	else:
		print("model is not defined.")
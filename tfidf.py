import os
import collections
from string import punctuation
import numpy as np

import nltk
import pdb
import json

def compute_tfidf_for_dir(directory):
	''' 
	Compute tfidf with counts and occurrences
	from the cluster folders which act as documents
	all_occurrences.json = which words occur in which documents
	all_counts_ordere... = counts of words in each document
	'''
	directory_list = []
	all_docs_occurrences = collections.defaultdict(list)
	with open(directory+'all_occurrences.json','r') as f:
		all_docs_occurrences.update(json.load(f))
	for subdir, dirs, files in os.walk(directory):
		if not subdir.endswith('/'):
			directory_list.append(subdir)
	docs_total = len(directory_list)
	for x in directory_list:
		x = x+'/'
		print('Computing tfidf for '+x)
		# in every subdir we have
		# all_counts_ordered_aggregated.json
		# all_occurrences.json
		tfidf_calc = collections.defaultdict(list)
		sub_count = collections.defaultdict(list)
		with open(x+'all_counts_ordered_aggregated.json','r') as f:
			sub_count.update(json.load(f))
		for term in sub_count.keys():
			term_freq = sub_count.get(term) #
			docs_with_term = all_docs_occurrences.get(term) #
			inv_term_freq = np.log(docs_total / (1+docs_with_term)) #
			tfidf_calc.update({term:term_freq*inv_term_freq})
		tfidf = collections.OrderedDict(sorted(tfidf_calc.items(), key=lambda t: t[1], reverse=True))
		with open(x+'directory_tfidf.json','w') as f:
			json.dump(tfidf, f, indent=4)
			print('Saved tfidf for '+str(x))
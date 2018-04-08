from scipy import stats
import json
import collections
import itertools
import pdb

def compute_kw_combined():
	topics = ['gaming','religion','news','politics','family','arts','food','science','sports','gender']
	values1 = []
	values2 = []
	values3 = []
	values4 = []
	values5 = []
	values6 = []
	values7 = []
	values8 = []
	values9 = []
	values10 = []
	i = 0
	for top in topics:
		i += 1
		with open('../gensim_word2vec/stats/corpora_'+str(top)+'_stats.json','r') as f:
			dict1 = json.load(f)
			for item in dict1.keys():
				exec('values%i.extend(len(dict1.get(item)) * [item])' % i)

	comb_list = [values1,values2,values3,values4,values5,values6,values7,values8,values9,values10]

	print('Kruskal Wallis for the 10 topics')
	print(stats.mstats.kruskalwallis(values1,values2,values3,values4,values5,values6,values7,values8,values9,values10))
	
	### post hoc testing for all 10! combinations
	test = 0
	sig = 0
	alpha = 0.05 / 45 # original alpha by the number of comparisons
	for x in range(0,len(comb_list)):
		for y in range(x+1,len(comb_list)):
			test += 1
			array1 = [float(element) for element in comb_list[x]]
			array2 = [float(element) for element in comb_list[y]]
			resultu, resultp = stats.mstats.mannwhitneyu(array1,array2)
			if resultp < alpha:
				sig += 1
				print('MWU of '+str(topics[x]+' and '+str(topics[y])))
				print(str(resultu)+' '+str(resultp))
			else:
				print('MWU of '+str(topics[x]+' and '+str(topics[y])+' (NOT SIGNIFICANT)'))
				print(str(resultu)+' '+str(resultp))


	print('number of tests: '+str(test))
	print('number of significant results: '+str(sig))
import json
import os
import pdb
import shutil
import socket
import time
from datetime import datetime

import praw
import prawcore
import requests
import urllib3
from praw.models import MoreComments

import ak_private


def crawl_comments(reddit, sub, comments_count, sublim, folder=None):
	occurred_errors = 0
	subreddit = reddit.subreddit(sub.display_name)
	subreddit.title # fixes unavailable attribute bug
	print(str(datetime.now())+': Crawling ' + str(subreddit.display_name) + ': ' + str(subreddit.title))

	subcount = 0

	if(sublim==None):
		limit_display = '_unlimited'
	else:
		limit_display = str(sublim)

	if(folder==None):
		outputfile = 'corpora/' + subreddit.display_name.lower() + '_top' + limit_display + '.txt'
	else:
		outputfile = 'corpora_' + folder + '/' + subreddit.display_name + '_top' + limit_display + '.txt'

	with open(outputfile, 'w') as crawl_text:
		#limit either max. 100 or None which means unlimited (max. 1000 saved by Reddit)
		for submission in subreddit.top(limit=sublim):
			try:
				comments_count[0] += submission.num_comments
				print('Submission has ' + str(submission.num_comments) + ' comments.', end=' ')
				submission_text = ''
				# .list() means traversing the comment tree breadth first
				all_comments = submission.comments.list()
				for comment in all_comments:
					if isinstance(comment, MoreComments):
						continue
					submission_text = submission_text + ' ' + str(comment.body)
				crawl_text.write(submission_text)
				subcount += 1
				if(sublim!=None):
					perc = 100 / sublim * subcount
					print(str(perc)+'% of submissions crawled.')
				else:
					print(str(subcount)+' submissions crawled.')
			except (socket.gaierror, urllib3.exceptions.NewConnectionError, urllib3.exceptions.MaxRetryError, requests.exceptions.ConnectionError, prawcore.exceptions.RequestException) as e:
				occurred_errors += 1
				if(occurred_errors>=5):
					print('--- '+str(occurred_errors)+' errors occurred. Skipping complete Sub to avoid high data loss. ---')
					raise
				else:
					print('Connection Error occurred. Skipping to next submission after 15s sleep. Error message: "'+str(e)+'"')
					subcount += 1
					time.sleep(15)
					continue
		

def crawl_single_sub(reddit, sub):
	try:
		subreddit = reddit.subreddit(sub)
		comments_count = [0] #has to be a mutable object (list), otherwise a function cant change the value
		crawl_comments(reddit, subreddit, comments_count, None)
		print(str(datetime.now())+': '+str(subreddit)+' successfully crawled.')
	except Exception as e:
		handle_errors(e)
			

def crawl_list_of_subs_full(reddit, sub_list):
	crawled_subs = {}
	try:
		print(str(datetime.now())+': Loaded list of previous crawled subreddits.')
		# json file containing all successfully crawled Subreddits so far
		with open('crawled_subs_full.json') as f:
			crawled_subs = json.load(f)
	except Exception:
		print(str(datetime.now())+': No list of previous crawled subreddits found.')
	crawled_subs_lower = set(k.lower() for k in crawled_subs) #check all in lowercase because our lists are lowercase

	subreddit_list = []


	for subreddit in sub_list:
		if subreddit not in crawled_subs_lower:
			subreddit_list.append(reddit.subreddit(subreddit))

	print(str(datetime.now())+': '+str(len(subreddit_list))+' subreddit(s) to be crawled: '+str(subreddit_list))
	subrcount = 0

	for subreddit in subreddit_list:
		subrcount += 1
		try:
			comments_count = [0] #has to be a mutable object (list), otherwise a function cant change the value
			crawl_comments(reddit, subreddit, comments_count, None)
			crawled_subs.update({subreddit.display_name:comments_count[0]})
			with open('crawled_subs_full.json', 'w') as f:
				json.dump(crawled_subs, f, indent=4)
			perc = 100 / len(subreddit_list) * subrcount
			print(str(datetime.now())+': ----- Status: '+str(perc)+'% done. -----')
		except Exception as e:
			handle_errors(subreddit,e)


def handle_errors(subreddit,e):
	# pylint: disable=no-value-for-parameter
	if(str(e)=='Unexpected status code: 451'):
		print(str(datetime.now())+': '+str(subreddit.display_name)+': This content is not available in your country. Skipping. Error: '+str(e))
	if(str(e)=='received 403 HTTP response'):
		print(str(datetime.now())+': '+str(subreddit.display_name)+': Access denied by server. Probably private or banned Sub. Skipping. Error: '+str(e))
	else:
		print(str(datetime.now())+': '+str(subreddit.display_name)+': An error occured. Skip sub and wait in case of bad connection. Error: '+str(e))
		time.sleep(60)


def main():
	# Login with Reddit user data
	# use praw.Reddit(credentials) with credentials being:
	# - client_id
	# - client_secret
	# - password
	# - user_agent
	# - username
	reddit = ak_private.login()
	



	'''load predefined lists from according files'''
	list_family = []
	list_politics = []
	list_gender = []
	list_science = []
	list_gaming = []
	list_food = []
	list_religion = []
	list_sports = []
	list_arts = []
	list_news = []
	list_popular = []
	with open('sublist_family.txt') as f:
		list_family.extend(f.read().splitlines())
	with open('sublist_politics.txt') as f:
		list_politics.extend(f.read().splitlines())
	with open('sublist_gender.txt') as f:
		list_gender.extend(f.read().splitlines())
	with open('sublist_science.txt') as f:
		list_science.extend(f.read().splitlines())
	with open('sublist_gaming.txt') as f:
		list_gaming.extend(f.read().splitlines())
	with open('sublist_food.txt') as f:
		list_food.extend(f.read().splitlines())
	with open('sublist_religion.txt') as f:
		list_religion.extend(f.read().splitlines())
	with open('sublist_sports.txt') as f:
		list_sports.extend(f.read().splitlines())
	with open('sublist_arts.txt') as f:
		list_arts.extend(f.read().splitlines())
	with open('sublist_news.txt') as f:
		list_news.extend(f.read().splitlines())
	with open('sublist_500_popular.txt') as f:
		list_popular.extend(f.read().splitlines())
	current_list = list_family + list_politics + list_gender + list_science + list_gaming + list_food + list_religion + list_sports + list_arts + list_news + list_popular
	current_list = list(set(current_list)) # removes duplicates from the list

	'''Crawl concatenated list of all topics'''
	# crawl_list_of_subs_full(reddit,current_list) 

	'''Crawl 500 most popular Subreddits'''
	# popular_list = []
	# for subreddit in reddit.subreddits.popular(limit=500):
	# 	popular_list.append(subreddit.display_name)
	# crawl_list_of_subs_full(reddit,popular_list)


	'''Save list of 500 most popular Subreddits at time of crawling'''
	# with open('sublist_500_popular.txt','w') as f:
	# 	for sub in popular_list:
	# 		f.write(sub+'\n')

	print('Finished!!')

if __name__ == "__main__":
	main()

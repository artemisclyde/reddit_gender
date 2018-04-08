'''
Python text data cleaner for Reddit text corpora retrieved via praw©
'''

import sys, os
import re
import time
import pdb

def main():
	init_time = time.time()
	for filename in sys.argv[1:]:
		if '_cleaned' in filename:
			continue
		print('Cleaning '+str(filename)+' [          ]',end=' ')
		print ('\b'*12,end='')
		sys.stdout.flush()
		if filename+'_cleaned' in sys.argv:
			print(".( '-' ).] Already cleaned.")
			continue
		start_time = time.time()
		content = []
		with open(filename, 'r') as file:
			content = file.readlines()
		num_all = len(content)
		num_steps = len(content)/10

		for i, item in enumerate(content):

			# lowercase
			content[i] = content[i].lower()
			# [deleted] and other reddit tags, also image tags [Rottweiler playing with ball]
			content[i] = re.sub('\[(.*?)\]',' ',content[i])
			# hyperlinks
			content[i] = re.sub('(http:\S*)|(https:\S*)|(www.\S*)',' ',content[i])
			# /r/aww, r/aww and other subs
			content[i] = re.sub('(\/r\/\S*)|(r\/\S*)',' ',content[i])
			# special characters, numbers etc
			# remove last so it doesn't break the other regex matches
			content[i] = re.sub('[{}<>“”:;=~+"!.?,@#\$%^&*()(0-9)\\\|/]|(\s-)|(-\s)',' ',content[i])
			# remove multiple spaces, spaces at the beginning or end of a sentence, empty lines
			content[i] = re.sub('(\s\s+)|(\n)',' ',content[i])
			content[i] = re.sub('(^\s)|(\s$)','',content[i])

			if i%num_steps < 1:
				print('.',end='')
				sys.stdout.flush()

		for i, item in enumerate(content):
			# check if line is blank
			if content[i] in ['\n', '\r\n', '']:
				del content[i]

		# pdb.set_trace()
		with open(filename+'_cleaned', 'w') as file:
			for item in content:
				file.write(item+'\n')

		print(']  Done in %s seconds.' % round(time.time() - start_time, 2))
	print('Finished in %s seconds.' % round(time.time() - init_time, 2))


if __name__ == "__main__":
	main()
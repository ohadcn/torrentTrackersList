#!/usr/bin/python

from urllib import urlopen
from sys import argv, exit, stdout, stderr

def checkTracker(url):
	if not url or not len(url)>1:
		return False
	had = getattr(checkTracker, url, False)
	if had:
		stderr.write('tracker ' + url + ' appeared twice: removing one\n')
		return False
	setattr(checkTracker, url, True)
	#TODO check that trackers are alive
	return (url.startswith('http://') or url.startswith('udp://'))

if __name__ == '__main__':
	if len(argv) < 2 or len(argv) > 3:
		print('USAGE: ' + argv[0] + ' <trackers-list-file> [results-file[')
		exit(0)
	ls = open(argv[1], 'rt')
	if len(argv) == 3:
		stdout = open(argv[2], 'wt', 1)
	print('\n\n'.join([tracker.strip() for tracker in ls if checkTracker(tracker.strip()) ]))
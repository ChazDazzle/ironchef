#!/usr/bin/python
# -*- coding: cp1252 -*-
#    Copyright 2014, Chaz Littlejohn 
#        ________  ____  _   __   ________  ______________
#       /  _/ __ \/ __ \/ | / /  / ____/ / / / ____/ ____/
#       / // /_/ / / / /  |/ /  / /   / /_/ / __/ / /_    
#     _/ // _, _/ /_/ / /|  /  / /___/ __  / /___/ __/    
#    /___/_/ |_|\____/_/ |_/   \____/_/ /_/_____/_/       
#                                                         
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#    
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#    
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

########################################################################

import os
import re
import shutil
import episodes
import difflib
from latin_to_ascii import latin1_to_ascii

re_iron_chef_1 = re.compile("(?P<IRON>[a-z\s]+)\svs\s(?P<CHALLENGER>[a-z\.\s]+)\s(overtime\s)?\((?P<INGREDIENT>[a-z\s\'&]+)\)")
re_iron_chef_2 = re.compile("iron\schef\s\-\s(?P<INGREDIENT>[a-z\s]+?)(\s\(.+?\))?(?P<BATTLE>\s(battle)?(\srematch|\s\d+)?(\sovertime[a-z\s]+)?\s?)\-\s(?P<IRON>[a-z\s]+)\svs\s(?P<CHALLENGER>[a-z\s]+)")

def checklists(item1, item2):
	for w1 in [l for l in item1.split() if l!='and']:
		for w2 in [l for l in item2.split() if l!='and']:
			if difflib.SequenceMatcher(a=w1, b=w2).ratio() >= 0.5:
				return True
	if item1.replace(' ','')==item2.replace(' ', ''):
		return True
	return False

def episode_data(data={}):
	for title, season, episode in episodes.listing:
		m1 = re_iron_chef_1.search(latin1_to_ascii(title))
		if m1:
			iron = m1.group("IRON")
			challenger = m1.group("CHALLENGER")
			last = challenger.split()[-1]
			ingredient = m1.group("INGREDIENT").replace('&', 'and').replace("'", "")
			info = {'season':season, 'episode':episode, 'title':title, 'INGREDIENT':ingredient, 'IRON':iron, 'CHALLENGER':challenger}
			data[(iron,last,ingredient)] = info
	print "Read %d of %d episodes from the listing" % (len(episodes.listing),len(data))
	return data
		
def sorted_videos(directory, videos=[]):
	for root, dirs, files in os.walk(directory, topdown=False):
		for name in files:
			if name.endswith('.avi'):
				videos.append(name)
	videos.sort()
	return videos

def matching_video(data, videos, assigned=[]):
	for name in videos:	
		match = None
		m2 = re_iron_chef_2.search(name)
		if m2: 
			match = data.get((m2.group("IRON"),m2.group("CHALLENGER"),m2.group("INGREDIENT")))
			if not match:
				for k, info in data.iteritems():
					if (checklists(m2.group("IRON"),info['IRON']) and
						checklists(m2.group("INGREDIENT"),info['INGREDIENT']) and 
						checklists(m2.group("CHALLENGER"),info['CHALLENGER']) and 
						info['title'] not in assigned):
						match = info
						break
			if match:
				match['errata'] = '%s%s - %s vs %s' % (m2.group("INGREDIENT"), m2.group("BATTLE"), m2.group("IRON"), m2.group("CHALLENGER"))
		else:
			for title, season, episode in episodes.listing:
				if (title[:8]==name[12:20]) and title not in assigned:
					match = {'season':season, 'episode':episode, 'errata': title.replace(':',''), 'title': title}
					break
		if match:
			match['name'] = name
			assigned.append(match['title'])
			yield match, assigned
		else:
			print 'Could not match file', name
			
def organize_files(data, videos):
	for match, assigned in matching_video(data, videos):
		filename = "Iron Chef - s%se%s - %s.avi" % (match['season'], match['episode'], match['errata'])
		folder = os.path.join(directory,'Season %s' % match['season'])
		if not os.path.exists(folder):
			os.mkdir(folder)
		shutil.move(os.path.join(directory,match['name']),os.path.join(directory,folder,filename))
	print "Matched %d of %d video files in %s" % (len(assigned), len(videos), directory)
			
			
def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
		
	directory = argv[0]
	data = episode_data()
	videos = sorted_videos(directory)
	organize_files(data, videos)

if __name__ == '__main__':
    sys.exit(main())
			

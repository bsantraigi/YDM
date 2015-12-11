
# coding: utf-8

# In[2]:

# Name: youParse.py
# Version: 1.3
# Author: pantuts
# Description: Parse URLs in Youtube User's Playlist (Video Playlist not Favorites)
# Use python3 and later
# Agreement: You can use, modify, or redistribute this tool under
# the terms of GNU General Public License (GPLv3).
# This tool is for educational purposes only. Any damage you make will not affect the author.
# Usage: python3 youParse.py youtubeURLhere

# sudo pip install youtube-dl
# download pafy from github

import re
import urllib.request
import urllib.error
import sys
import time
from pafy import pafy

def crawl(url):
    sTUBE = ''
    cPL = ''
    amp = 0
    final_url = []
    
    if 'list=' in url:
        eq = url.index('=') + 1
        cPL = url[eq:]
        if '&' in url:
            amp = url.index('&')
            cPL = url[eq:amp]
            
    else:
        print('Incorrect Playlist.')
        exit(1)
    
    try:
        yTUBE = urllib.request.urlopen(url).read()
        sTUBE = str(yTUBE)
    except urllib.error.URLError as e:
        print(e.reason)
    
    tmp_mat = re.compile(r'watch\?v=\S+?list=' + cPL)
    mat = re.findall(tmp_mat, sTUBE)

    if mat:
        
        if mat[0] == mat[1]:
            mat.remove(mat[0]) #if there is duplicate, remove
            
        for PL in mat:
            yPL = str(PL)
            if '&' in yPL:
                yPL_amp = yPL.index('&')
            final_url.append('http://www.youtube.com/' + yPL[:yPL_amp])
                
        i = 0
        while i < len(mat):
#             sys.stdout.write(final_url[i] + '\n')
            i = i + 1
        return final_url, len(mat)
        
    else:
        print('No videos found.')
        exit(1)

def listParser(list_url):
    final_url, l = crawl(list_url)
    uset = set(final_url)
    print("Please hold on...")
    # print(uset)
    fHTML = open("temp.html","w")
    i = 0
    l = len(uset)
    for u in uset:
        url = u
        video = pafy.new(url)
        s = video.getbest()
        # print(s.resolution, s.url)
        fHTML.write("<a href='"+s.url+"'>" + video.title + "</a><br>")
        i = i+1
        print("Done: " + '{0:.2f}'.format(i*100/l) + " %")
    fHTML.close()
        
if len(sys.argv) < 2 or len(sys.argv) > 2:
    print('USAGE: python3 youParse.py YOUTUBEurl')    
    exit(1)
    
else:
    url = sys.argv[1]
    if 'http' not in url:
        url = 'http://' + url
    listParser(url)





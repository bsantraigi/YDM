
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
from pafy import pafy
from tkinter import *
from tkinter import ttk
import tkinter.constants as Tkconstants
import tkinter.filedialog as tkFileDialog
import os
import subprocess 
from threading import Thread
import queue as Queue
import time 

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
        
# if len(sys.argv) < 2 or len(sys.argv) > 2:
#     print('USAGE: python3 youParse.py YOUTUBEurl')    
#     exit(1)
    
# else:
#     url = sys.argv[1]
#     if 'http' not in url:
#         url = 'http://' + url
#     listParser(url)

dir_opt = options = {}
options['initialdir'] = 'C:/'
options['mustexist'] = False
options['title'] = 'This is a title'

def askdirectory():
    """Returns a selected directoryname."""
    newPath = tkFileDialog.askdirectory(**dir_opt)
    if(newPath != ""):
        savePath.set(newPath)
    else:
        print("Hick")
    

# Get the list of videos
def listParser(list_url, q, progressQ):
    final_url, l = crawl(list_url)
    uset = set(final_url)
    # print("Please hold on...")
    # print(uset)
    i = 0
    l = len(uset)
    linkArr = []
    for u in uset:
        url = u

        video = pafy.new(url)
        s = video.getbest()
        fname = re.sub(r'[<>:\"\/\\|\?\*]+', "_", s.title)+"."+s.extension
        # print(s.title)
        # print(fname)
        linkArr.append({
            'url':s.url,
            'title':s.title,
            'ext':s.extension,
            'filename':fname
            })
        # print(s.resolution, s.url)
        i = i+1
        # pb["value"] = int(i*100/l)
        progressQ.put(int(i*100/l))
        # print("Done: " + '{0:.2f}'.format(i*100/l) + " %")
    # print("Finished Getting List...")
    q.put(linkArr)
    # return linkArr


# Fire IDM for downloading
def downloadVideos():
    global allDownComplete
    global downGenerator
    print("Start Download next 3 video")
    if allDownComplete:
        if q.empty():
            print("Download queue not ready yet.")
            return
        allDownComplete = False
        downGenerator = downloaderCoroutine()
        print(next(downGenerator))
    else:
        print(next(downGenerator))

def downloaderCoroutine():
    global downStatus
    downStatus = 0
    root.after(100, update_downStatus)
    linkArr = q.get()
    counter = 0
    limit = 4
    prcs = []

    size = len(linkArr)
    done = 0
    for l in linkArr:
        # C:\Program Files (x86)\Internet Download Manager\IDMan.exe" /n /d <link> /p <path> /f <filename>
        comm = '\"C:\Program Files (x86)\Internet Download Manager\IDMan.exe\" /n /d \"' + l['url'] + '\" /p \"' + savePath.get() + '\" /f \"' + l['filename'] + '\"'
        # os.system(comm)
        prcs.append(subprocess.Popen(comm))
        time.sleep(2)
        done = done + 1
        downStatus = int(done*100/size)
        counter = counter + 1
        print("Counter: "+str(counter))
        print(l['filename'])        
        if(counter >= limit):
            print("Press download again to continue...")
            counter = 0
            if done == size:
                allDownComplete = True
                return
            yield downStatus

def update_downStatus():
    downloadPb["value"] = downStatus
    if(downStatus == 100):
        return
    root.after(100, update_downStatus)

def update_bar(parserThread):
    if not progressQ.empty():
        p = progressQ.get()
        pb["value"] = p
        if p == 100:            
            parserThread.join()
            print("Parsing Complete")
            return
    root.after(100, update_bar, parserThread)


# Code for downloading
progressQ = Queue.Queue()
q = Queue.Queue()
def process():
    print("URL:", listURL.get())
    print("SAVE TO:", savePath.get())
    url = listURL.get()
    if(url != ""):
        parserThread = Thread(target = listParser, args = [url, q, progressQ])
        parserThread.daemon = True
        parserThread.start()        
        update_bar(parserThread)
    else:
        print("Nothing to get!!!")
    # print("Ikes!!!")
    

root = Tk()
root.resizable(width=FALSE, height=FALSE)
# root.geometry('{}x{}'.format(600,400))
root.title("Youtube Playlist using IDM")

mainframe = ttk.Frame(root, padding="3 3 12 12")
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
mainframe.columnconfigure(0, weight=1)
mainframe.rowconfigure(0, weight=1)

listURL = StringVar()
savePath = StringVar()


# Default Path:
listURL.set("")

# Default Save path
savePath.set(os.getcwd())
# savePath.set("C:/Users/Bishal/Shared/Youtube/")

# Labels
ttk.Label(mainframe, text = "Playlist URL: ").grid(column = 1, row=1, sticky = E)
ttk.Label(mainframe, text = "Save Path: ").grid(column = 1, row=2, sticky = E)
ttk.Label(mainframe, text = "Parse Progress: ").grid(column = 1, row=3, sticky = E)
ttk.Label(mainframe, text = "Download Progress: ").grid(column = 1, row=4, sticky = E)

inputWid = 100
# URL Input
url_entry = ttk.Entry(mainframe, textvariable = listURL, width = inputWid)
url_entry.grid(column = 2, row=1, columnspan = 4, sticky = (W, E))

# Path Input
path_entry = ttk.Entry(mainframe,textvariable = savePath)
path_entry.grid(column = 2, row=2, columnspan = 3,sticky = (W, E))

# Progressbar
pb = ttk.Progressbar(mainframe, orient=HORIZONTAL, mode='determinate')
pb.grid(column = 2, row=3, sticky = (W, E), columnspan=3)
pb["value"] = 0
pb["maximum"] = 100

# Progressbar
downloadPb = ttk.Progressbar(mainframe, orient=HORIZONTAL, mode='determinate')
downloadPb.grid(column = 2, row=4, sticky = (W,E), columnspan=3)
downloadPb["value"] = 0
downloadPb["maximum"] = 100

# Buttons
ttk.Button(mainframe, text = "Change Folder", command = askdirectory).grid(column = 5, row=2, sticky = (W,E))
ttk.Button(mainframe, text = "Parse", command = process).grid(column = 5, row=3, sticky = (W,E))
ttk.Button(mainframe, text = "Download", command = downloadVideos).grid(column = 5, row=4, sticky = (W,E))

# Global variables
downStatus = 0
allDownComplete = True
downGenerator = None

for child in mainframe.winfo_children(): child.grid_configure(padx=5, pady=5)
url_entry.focus()

root.mainloop()


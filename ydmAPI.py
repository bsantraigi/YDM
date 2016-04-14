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
from os.path import expanduser
from PyQt4 import QtCore, QtGui

def getDownloadDir():
    return expanduser("~") + '\Downloads'

def askdirectory(initDir=""):
    dialog = QtGui.QFileDialog()
    dialog.setFileMode(QtGui.QFileDialog.Directory)
    if(initDir==""):
        initDir = getDownloadDir()
    dialog.setDirectory(initDir)
    dialog.setOption(QtGui.QFileDialog.ShowDirsOnly)
    newPath = ""
    if(dialog.exec_()):
        newPath = dialog.selectedFiles()[0]
        print(newPath)
    return newPath

def getVideoDetails(pageURL):
    video = pafy.new(pageURL)
    det = []
    for s in video.streams:
        size = int(round(s.get_filesize()/1024/1024))
        print(s.resolution, s.extension, size)
        # REMOVE RESTRICTED CHARACTERS FROM TITLE & ADD EXTENSION
        fname = re.sub(r'[<>:\"\/\\|\?\*]+', "_", s.title)+"."+s.extension
        # print(fname)
        det.append({
            'url':s.url,
            'title':s.title,
            'ext':s.extension,
            'filename':fname,
            'resolution':s.resolution,
            'size':size
            })

    return det

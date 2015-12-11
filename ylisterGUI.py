from tkinter import *
from tkinter import ttk
import tkinter.constants as Tkconstants
import tkinter.filedialog as tkFileDialog
import os


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
    

# Code for downloading
def process():
	print("URL:", listURL.get())
	print("SAVE TO:", savePath.get())
	

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
savePath.set(os.getcwd())


inputWid = 42
# URL Input
url_entry = ttk.Entry(mainframe, width = inputWid, textvariable = listURL)
url_entry.grid(column = 2, row=1, sticky = (W, E))

# Path Input
path_entry = ttk.Entry(mainframe, width=inputWid, textvariable = savePath)
path_entry.grid(column = 2, row=2, sticky = (W, E))

# Labels
ttk.Label(mainframe, text = "Playlist URL: ").grid(column = 1, row=1, sticky = E)
ttk.Label(mainframe, text = "Save Path: ").grid(column = 1, row=2, sticky = E)
ttk.Label(mainframe, text = "Progress: ").grid(column = 1, row=3, sticky = E)

# Buttons
ttk.Button(mainframe, text = "Change Folder", command = askdirectory).grid(column = 2, row=4, sticky = W)
ttk.Button(mainframe, text = "Download", command = process).grid(column = 2, row=4, sticky = E)

# Progressbar
pb = ttk.Progressbar(mainframe, orient=HORIZONTAL, length=300, mode='determinate')
pb.grid(column = 2, row=3, sticky = E)
pb["value"] = 0
pb["maximum"] = 100

for child in mainframe.winfo_children(): child.grid_configure(padx=5, pady=5)
url_entry.focus()

root.mainloop()
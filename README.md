# YDM (Youtube Playlist Downloader Addon for IDM)
-----------

YDM is an open source addon for **Internet Download Manager** (IDM) for downloading videos from Youtube playlists.

## Table of Contents
* [Features](#features)
* [Requirements](#requirements)
* [Installation](#installation)
* [Usage Example](#usage)
* [Team Members](#team-members)

## <a name="features"></a>Features
* Download any playlists from Youtube
* Choose which videos to download
* Save all videos to a folder
* Uses IDM

## <a name="requirements"></a>Requirements
This program is only for `Windows` and requires `Python 3.4` or greater installed in your system. It also need the following python modules to be installed in your system. 

* `youtube-dl`


## <a name="installation"></a>Installation

**Installing the program**

If your system meets all the requirements downlaod this program by clicking the <a href="https://github.com/studiobytestorm/YDM/archive/master.zip">![downloadbutton](http://i.stack.imgur.com/0SWhD.png)</a> button above. Unzip it into a folder say `C:\YDM`. Then open command prompt and run 

```python
C:\Users\Name> cd C:\YDM
C:\YDM> python yListerFull.py
```

**Installing the requirements**

You can install `Python 3.4` from [here](https://www.python.org/). Once you have installed Python you can install `youtube-dl` using pip.

```python
pip install youtube-dl
```


## <a name="usage"></a>Usage Example
Here is an example of how to use this program.

```python
C:\YDM> python yListerFull.py
```
Once you execute the above line it will open up a GUI as shown below. Enter an Youtube playlist url and the path to save the downloaded files. Then press the parse button. Once parsing is complete press download button to start downloading first 4 videos and once finished click download again to continue downloading the next 4 videos and so on.

**Here's a screeshot...**

<img src="http://i.stack.imgur.com/R0NRb.png" alt="Screeshot1" style="width: 100%;"/>

## <a name="team-members"></a>Contributors
* "Bishal Santra" <bsantraigi@gmail.com>

## <a name="refs"></a>References
* [rg3/youtube-dl](https://github.com/rg3/youtube-dl/)
* [mps-youtube/pafy](https://github.com/mps-youtube/pafy)


----------

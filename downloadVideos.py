import os
import yt_dlp
import pandas as pd
from dataTransfer import saveListDownloaded, getPathChange, loadListDownloaded
def downloadVideos(oscar):
    """
    do the previous version of the algorithm, instead downloading all of the videos instead. 

    THIS WORKS, as does saving videos and concatenation. 
    """
    path = getPathChange(oscar)
    centeringParams, categories = loadCenteringParams(path)
    listDownloaded = []
    for category in categories:
        listDownloadedCat = loadCategoryDownload(path, category)
        listDownloaded+=listDownloadedCat
    saveListDownloaded(listDownloaded, oscar)

def loadCategoryDownload(path, category):
    link = path + "annotations/" + category
    listFilesAnnotated = os.listdir(link)
    preset = "https://www.youtube.com/watch?v="
    count = 0
    listDownloaded = []
    for count in range(len(listFilesAnnotated)):
        video = listFilesAnnotated[count]
        videoDownloaded, name = downloadVideo(preset + video, path, category, count)
        if videoDownloaded:
            listDownloaded.append(name)
    return listDownloaded
def downloadVideo(link, path, category, count):
    downloadPath = path + "annotatedVideos/"
    name = "{cat}{num}".format(cat = category, num = count)
    ydl_opts={ 'format': 'best', 'outtmpl':downloadPath + name + ".mp4"}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([link])
        return True, name
    except :
        print("Exception on video num: ", count)
        return False, name
def loadCenteringParams(path):
    """
    Loads centering parameters and list of categories as lists. 
    """
    link = path + "categories.csv"
    categoryCSV = pd.read_csv(link)
    #ordered in alphabetical categories.  
    #.values gets numpy array. 
    centeringParams = categoryCSV.loc[:, "CENTERING_PARAM"].values
    catList = categoryCSV.loc[:, "DIR_NAME"].values
    return centeringParams, catList

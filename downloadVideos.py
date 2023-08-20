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
    listLinks = []
    for category in categories:
        listDownloadedCat, listDownloadedLinks = loadCategoryDownload(path, category)
        listDownloaded+=listDownloadedCat
        listLinks +=listDownloadedLinks
    saveListDownloaded(listDownloaded,listLinks, oscar)

def loadCategoryDownload(path, category):
    link = path + "annotations/" + category
    listFilesAnnotated = os.listdir(link)
    preset = "https://www.youtube.com/watch?v="
    count = 0
    listDownloaded = []
    listLinks = []
    for count in range(len(listFilesAnnotated)):
        video = listFilesAnnotated[count]
        #get rid of .fps1.csv
        #how did it work before this??? Maybe automatically ignores the extra stuff. 
        videoLink = video[:-9]
        videoDownloaded, name = downloadVideo(preset + videoLink, path, category, count)
        if videoDownloaded:
            listDownloaded.append(name)
            listLinks.append(videoLink)
    return listDownloaded, listLinks
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
#downloadVideos(True)
#639 videos downloaded. 
#print(len(loadListDownloaded(True)[0]))
import yt_dlp
import pandas as pd
import os
import numpy as np
from multiprocessing.pool import Pool
import cv2
from functools import partial
import math
from PIL import Image
from imageDisplay import displayFrames
from dataTransfer import videoPath, video, loadListDownloaded
from extractFrames import extractFrames
from annotations import loadAnnotations, annotations

        
def loadFramesPreDownloaded(desiredSize, oscar):
    """
    FINISH THIS METHOD AND ANNOTATIONS AND MAKE SURE THEY MATCH UP WITH THE NAMES. 
    THEN RUN OSCAR ONCE READY. 
    """
    #loadAnnotations
    listDownloaded, listLinks = loadListDownloaded(oscar)

    #want to load in annotations. How to assure that they match the actual file names? 
    listFrames = []
    count = 0
    #can use some condition with count. 
    for i in range(len(listDownloaded)):
        if count>5:
            break
        name = listDownloaded[i]
        link = listLinks[i]
        indices, valid = annotations(name, link, oscar)
        if valid:
            frames = extractFrames(videoPath(name, oscar), indices, desiredSize)
            if frames is not None:
                #could save the frames here to use for later. 
                listFrames.append(frames)
                count+=1
    return np.stack(listFrames, dtype=np.uint8)


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


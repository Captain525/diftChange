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
from annotations import loadAnnotations

        
def loadFramesPreDownloaded(path, desiredSize, oscar):
    """
    FINISH THIS METHOD AND ANNOTATIONS AND MAKE SURE THEY MATCH UP WITH THE NAMES. 
    THEN RUN OSCAR ONCE READY. 
    """
    #loadAnnotations
    listDownloaded = loadListDownloaded(oscar)


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


import yt_dlp
import pandas as pd
import os
import numpy as np

from multiprocessing.pool import Pool
import cv2
from functools import partial
import math


"""
Load the videos with annotations. 
"""


def loadFrames():
    """
    Loads the desired frames from the youtube video 
    directly without having to download the .mp4 file. 
    """


def loadChangeIt(oscar):
    """
    Load videos with annotations, there are 667 of them so doable.
    """
    path =   "/mnt/c/Users/dheff/CodingProjects/PythonProjects/PALM Research/data/ChangeIt/"

    if(oscar):
        #need to create this folder and put the data in there. 
        path = "/users/dheffren/data/dheffren/ChangeIt/"
    centeringParams, categories = loadCenteringParams(path)
    for category in categories:
        categoryLinks = loadCategoryAnnotated(category, path)

    


def loadCategoryAnnotated(category, path):
    link = path + "annotations/" + category
    listFilesAnnotated = os.listdir(link)
    preset = "https://www.youtube.com/watch?v="
    #each ends with .fps1.csv 9 characters
    #see if this works properly. 
    #youtubeLinks = [preset + name[0:-9] for name in listFilesAnnotated]
    for video in listFilesAnnotated:
        print(link + "/" + video)
        indices = loadAndProcessAnnotations(link+ "/" + video)
        videoLink = preset + video[0:-9]
        youtubeLoadDirect(videoLink, indices)
def process_video_parallel(url, desiredSize, process_number):
    cap = cv2.VideoCapture(url)
    num_processes = os.cpu_count()
    
    #divides total frames in video into num cpus amounts.
    frames_per_process = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))//num_processes
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    #print("fps: ", fps)
    #cap_PROP_POS_FRAMES = 0 based index of frame to  be decoded/captured next. 
    #processes labelled starting at 0, so it allocates frames_per_Process frames for each. 
    
    print("frame count: ", cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print("frames per process: ", frames_per_process)
    #want to round up to nearest whole number. 

    #method wrong if already is a whole number. 
    numberOfFramesFromDesired = 0
    modulo = (frames_per_process*process_number)%fps
    if(modulo != 0):
        numberOfFramesFromDesired = fps - (frames_per_process*(process_number))%fps
    startingIndex = frames_per_process*(process_number) + numberOfFramesFromDesired
    print("starting index: ", startingIndex)
    
    print("begin interval: ", frames_per_process*(process_number))
    print("end interval: ", frames_per_process*(process_number+1))
    endIndex = frames_per_process*(process_number+1)
    if(endIndex>cap.get(cv2.CAP_PROP_FRAME_COUNT)):
        endIndex = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    count = 0
    listFrames = []
    listStarting = []
    cap.set(cv2.CAP_PROP_POS_FRAMES, startingIndex)
    while count+startingIndex<endIndex:
        ret,frame = cap.read()
        if not ret:
            break
        #filename =  os.getcwd() + "/images/frame" + str(startingIndex + count) + ".jpg"
        image = cv2.resize(frame, desiredSize)
        value = np.array(image, np.uint8)
        #print("frame shape: ", value.shape)
        listFrames.append(value)
        listStarting.append(startingIndex+count)
        #try:
            #print(frame.shape)
            #cv2.imwrite(filename, image)
            #print("written")
        #except:
            #print("problem")
        count+=fps
        
        cap.set(cv2.CAP_PROP_POS_FRAMES,startingIndex + count)
    cap.release()
    frameArray = np.stack(listFrames, dtype=np.uint8)
    print("frame array shape: ", frameArray.shape)
    print("starting list: ", len(listStarting))
    print("starting list: ", listStarting)
    assert(len(frameArray.shape) ==4)
    return frameArray
def youtubeLoadDirect(link, indices):

    """
    https://stackoverflow.com/questions/66272740/extract-specific-frames-of-youtube-video-without-downloading-video
    Had to change some of the stuff in the link. 
    ALSO, CHANGE THE FORMAT. FIGURE OUT HOW TO MAKE IT BETTER THEN DOWNSIZE. 

    DONT FORGET TO DEAL WITH THE -1s. 
    """
    ydl_opts = {}
    ydl = yt_dlp.YoutubeDL(ydl_opts)
    info_dict = ydl.extract_info(link, download=False)
    duration = info_dict.get('duration')
    print("video duration: ", duration)
    #this value changes later. 
    print("fps: ", info_dict.get('fps'))
    desiredSize = (480, 270)
    formats = info_dict.get('formats', None)
    for f in formats:
        if f.get('format_note', None)=='144p':
            url = f.get('url', None)
            cpu_count = os.cpu_count()
            print("cpu count: ", cpu_count)
            with Pool(cpu_count) as pool:
                #how does it divide the indices up. 
                videoImagesArray = np.concatenate(pool.map(partial(process_video_parallel, url, desiredSize), range(cpu_count)), axis=0)
            beginImage = videoImagesArray[indices[0]]
            actionImage = videoImagesArray[indices[1]]
            endImage = videoImagesArray[indices[2]]
            
            
def loadAndProcessAnnotations(csvLink):
    """
    Everything already in integers. 

    picks the first occurence of each of initial state, final state, and action. 
    If one of these doesn't occur in the video, gives an index of -1. 
    """
    #0 = nothing 1= initial 2 = action 3 = final. 
    annotationCSV = pd.read_csv(csvLink)
    #should be list of values for states. 
    #convert to ints i think. 
    #dataframe -> numpy -> list

    listAnnotations = annotationCSV.iloc(axis=1)[1].values.tolist()
    indices = -1*np.ones(shape = (3,), dtype=int)
    for i in range(3):
        try:
            #if the given index doesn't exist in the labels, give it a dne. 
            index = listAnnotations.index(i+1)
            indices[i] = index
        except:
            print("label: ", i+1, " dne")
    
    return indices


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
loadChangeIt(False)
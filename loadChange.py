import yt_dlp
import pandas as pd
import os
import numpy as np
from multiprocessing.pool import Pool
import cv2
from functools import partial
import math
from PIL import Image

def loadChangeIt(oscar):
    """
    Load videos with annotations, there are 667 of them so doable.
    """
    path =   "/mnt/c/Users/dheff/CodingProjects/PythonProjects/PALM Research/data/ChangeIt/"
    #x, y
    desiredSize = (480, 270)
    if(oscar):
        #need to create this folder and put the data in there. 
        path = "/users/dheffren/data/dheffren/ChangeIt/"
    centeringParams, categories = loadCenteringParams(path)
    for category in categories:
        categoryAnnotatedFrames = loadCategoryAnnotated(category, path, desiredSize)
        print("shape of category annotated: ", categoryAnnotatedFrames.shape)
        


def loadCategoryAnnotated(category, path, desiredSize):
    """
    Loads all the desired frames from valid annotated videos of a given video with the right
    size and as 8 bit integers. 
    """
    link = path + "annotations/" + category
    listFilesAnnotated = os.listdir(link)
    preset = "https://www.youtube.com/watch?v="
    #each ends with .fps1.csv 9 characters
    listFrames = []
    count = 0
    for video in listFilesAnnotated:
        print("count: ", count)
        if count>=5:
            break
        print("video: ", video)
        indices, valid = loadAndProcessAnnotations(link+ "/" + video)
        if valid: 
            videoLink = preset + video[0:-9]
            frames = processVideoSimple(videoLink, indices, desiredSize)
            
            if frames is not None:
                listFrames.append(frames)
                count+=1
    print("numframes: ", len(listFrames))
    return np.stack(listFrames, dtype = np.uint8)


def processVideoSimple(link, indices, desiredSize):
    """
    Simpler version without threading, extracts the indices from the video. 
    """
    print("begin process info")
    try:
        ydl_opts = {}
        ydl = yt_dlp.YoutubeDL(ydl_opts)
        info_dict = ydl.extract_info(link, download=False)
        formats = info_dict.get('formats', None)
    except:
        print("YOUTUBE DOWNLOAD FAILED")
        return None
    print("done that part. ")
    for f in formats:
        #pick a format, initially was 144p
        if f.get('format_note', None)=='720p':
            print("in format")
            url = f.get('url', None)
            cap = cv2.VideoCapture(url)
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            #indices in which second the frame occurs in. 
            #hould get the FIRST frame in each interval, if want something else, change it. 
            frameForEach = fps*indices
            cap.set(cv2.CAP_PROP_POS_FRAMES, frameForEach[0])
            listFrames = []
            for i in range(3):
                print("i is : ", i)
                cap.set(cv2.CAP_PROP_POS_FRAMES, frameForEach[i])
                unattained = True
                count = 0
                #only stay within the second. 
                while unattained and count<fps:
                    ret, frame = cap.read()
                    print(frame)
                    if ret:
                        print("returned")
                        unattained = False
                        #720p is y vert direciton, so 720 y 1080 x. 
                        #(480 x 270 y)
                        #changes it to y then x. 
                        image  = cv2.resize(frame, desiredSize)
                        imageColorChanged = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                        
                        listFrames.append(imageColorChanged)
                    count = count+1
                if unattained:
                    raise Exception("Couldn't find a viable frame")
            frames = np.stack(listFrames)
            print("frames shape: ", frames.shape)
            return frames
    print("Failed video format")
    return None


            
def loadAndProcessAnnotations(csvLink):
    """

    picks the first occurence of each of initial state, final state, and action. 
    If one of these doesn't occur in the video, gives an index of -1. 
    also return boolean if VALID or not. For now ,valid means it has all 3 states, maybe not later. 
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
    valid = True
    if -1 in indices:
        valid = False
    return indices, valid
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
def process_video_parallel(url, desiredSize, process_number):
    """
    Called by each thread to load the video frames as desired. Use this when you want a frame for 
    each second of the video, not when you just want the 3 desired frames. Too slow and inefficient for that. 

    """
    print("SHOULDN'T BE CALLED")
    cap = cv2.VideoCapture(url)
    num_processes = os.cpu_count()
    
    #divides total frames in video into num cpus amounts.
    frames_per_process = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))//num_processes
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    print("fps: " , fps)
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
        #automatically makes the image 270x480. Not sure which dimension is which. 
        image = cv2.resize(frame, desiredSize)
        print(image.shape)
        value = np.array(image, np.uint8)
        print("value shape: ", value.shape)
        listFrames.append(value)
        listStarting.append(startingIndex+count)
        count+=fps
        cap.set(cv2.CAP_PROP_POS_FRAMES,startingIndex + count)
    cap.release()
    frameArray = np.stack(listFrames, dtype=np.uint8)
    print("frame array shape: ", frameArray.shape)
    print("starting list: ", listStarting)
    assert(len(frameArray.shape) ==4)
    return frameArray
def youtubeLoadDirect(link, indices):

    """
    Given a youtube video link, and list of indices to extract frames for initial, action, and end states, 
    downloads those frames without saving the video into storage, makes it so you can do everything at once. 

    Loads a frame for each second.  
    Uses multiprocessing. 
    Partially derived from:
    https://stackoverflow.com/questions/66272740/extract-specific-frames-of-youtube-video-without-downloading-video
    Had to change some of the stuff in the link. 
    ALSO, CHANGE THE FORMAT. FIGURE OUT HOW TO MAKE IT BETTER THEN DOWNSIZE. 
    """
    ydl_opts = {}
    ydl = yt_dlp.YoutubeDL(ydl_opts)
    info_dict = ydl.extract_info(link, download=False)
    desiredSize = (480, 270)
    formats = info_dict.get('formats', None)
    #save the 3 desired frames from this video. 
    for f in formats:
        #pick a format, initially was 144p
        if f.get('format_note', None)=='720p':
            url = f.get('url', None)
            cpu_count = os.cpu_count()
            #allows for accessing the whole video with all frames potentially. 
            with Pool(cpu_count) as pool:
                #divides total frames into groups based on number of cpus, explain this later. 
                videoImagesArray = np.concatenate(pool.map(partial(process_video_parallel, url, desiredSize), range(cpu_count)), axis=0)
            return videoImagesArray

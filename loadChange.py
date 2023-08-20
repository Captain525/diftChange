import numpy as np
from imageDisplay import displayFrames
from dataTransfer import videoPath
from extractFrames import extractFrames
from annotations import  annotations
        
def loadFramesPreDownloaded(listDownloaded, listLinks, desiredSize, oscar):
    """
    Called after downloading youtube videos and saving a file with their names and links, then loading the names and links
    as listDownloaded and listLinks. 
    Accesses annotations and uses those to extract desired frames from the downloaded videos. 

    doesn't save anything, not done until diftcalc. 
    """
    #want to load in annotations. Links assure they match the actual file names. 
    listFrames = []
    count = 0
    numDesiredVideos = 3
    #can use some condition with count. 
    for i in range(len(listDownloaded)):
        #optional parameter to limit number of videos. Used mostly for testing. 
        if count>=numDesiredVideos:
            break
        name = listDownloaded[i]
        link = listLinks[i]
        #get annotations from the link to the video, since they're labeled via youtube link. 
        indices, valid = annotations(name, link, oscar)
        #if the annotations are valid for our task. 
        if valid:
            #get the annotation frames from the downloaded video. 
            frames = extractFrames(videoPath(name, oscar), indices, desiredSize)
            if frames is not None:
                #Save the frames in diftCalc method. 
                listFrames.append(frames)
                count+=1
    return np.stack(listFrames, dtype=np.uint8)

import cv2
import numpy as np
def extractFrames(videoLink, indices, desiredSize):
    """
    Extract the frames desired from a downloaded youtube video. Also want intermediate frames at 1/3 and 2/3 between 
    Way we'll do it: 
    don't assume anything about if the initial state is before or after the end state.
    
    Returns the frames in order initialState + third closest to initial +third closest to end + end
    doesn't use action. 
    """
    cap = cv2.VideoCapture(videoLink)
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    #number of frames into the "second" that we want to choose our frames from. 
    offset = fps//2
    frameForEach = fps*indices + offset
    assert(indices[2] != indices[0])
    if indices[2]<indices[0]:
        first = frameForEach[2]
        last = frameForEach[0]
    else:
        #gets the number of frames between. 
        first = frameForEach[0]
        last = frameForEach[2]
    #number of frames in between two chosen. 
    difference = last-first
    third = difference//3
    firstThird = first + third
    secondThird = firstThird + third
    #could start with final state then end with the first state. 
    desiredFrames = [first, firstThird, secondThird, last]
    if indices[2]<indices[0]:
        desiredFrames = desiredFrames[::-1]
    listImages= []
    for frame in desiredFrames:
        image = extractFrame(frame, cap, desiredSize)
        listImages.append(image)
    frames = np.stack(listImages, dtype = np.uint8)
    print("frames shape: ", frames.shape)
    return frames
def extractFrame(frameNumber, cap, desiredSize):
    """
    Gets a specific frame based on the framenumber. 
    Could change to try all frames within a certain range, ie within the given second. 
    However, haven't done this yet. 
    """
    #if frameNumber>max:
       # raise Exception("Extracting frame didn't work")
    cap.set(cv2.CAP_PROP_POS_FRAMES, frameNumber)
    ret, frame = cap.read()
    if not ret:
        print("Frame {} didn't work".format(frameNumber))
        #extractFrame(frameNumber + 1, cap, desiredSize, max)
        raise Exception("Extracting frame didn't work")
    image = cv2.resize(frame, desiredSize)
    imageColorChanged=  cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return imageColorChanged


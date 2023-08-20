import gc
import torch
from torchvision.transforms import PILToTensor
from src.models.dift_sd import SDFeaturizer
import numpy as np
import torch.nn as nn
import time
from imageDisplay import convertPIL
from dataTransfer import saveResults, savePoints, saveFrames
def callDift(frames, points, names, oscar=True):
    """
    Does all the dift calculations and operations on the frames to get the result points. 
    numVideos x numFrames x desiredSize[1] x desiredSize[0] x 3
    points is numVideos x numPoints x 2
    First in numFrames is the point frame, others are inference frames. 
    """
    torch.cuda.set_device(0)
    #use default model weights. 
    dift = SDFeaturizer()
    sizeNetwork = 768
    sizeFinal = 768
    listResultPoints = []
    #for each video. 
    for i in range(frames.shape[0]):
        print("Video {}/{}".format(i+1, frames.shape[0]))
        frame = frames[i]
        name = names[i]
        pointsFrame = points[i]
        #checking it isn't JUST the beginning frame. 
        assert(frame.shape[0]>1)
        beginningFrame = frame[0]
        #frames we want to run the matching algorithm on. 
        otherFrames = frame[1:]
        print("other frames shape: ", otherFrames.shape)
        #maybe add prompt later. 
        #hopefully this loop is fast enough of a way to do it.
        listMatched = [] 
        for j in range(otherFrames.shape[0]):
            print("Step: ", str(j))
            inferenceFrame = otherFrames[j]
            matchedArrayPoints = doMatching(dift, beginningFrame, inferenceFrame, "", sizeFinal, sizeNetwork, pointsFrame)
            listMatched.append(matchedArrayPoints)
        frameMatched = np.stack(listMatched, dtype = np.uint16)
        print("frameMatched size: ", frameMatched.shape)
        listResultPoints.append(frameMatched)

        #SAVE EVERYTHING ONCE DONE SO KNOW IT'S VALID. 
        
        #save Frames. 
        saveFrames(frame, name, oscar)
        #save the points. Would have to combine this with saveResults if we implemented TODO in diftChange. 
        savePoints(pointsFrame, name, oscar)
        #had wrong thing here earlier got bad results. 
        saveResults(frameMatched, name, oscar)
    arrayPoints = np.stack(listResultPoints)
    return arrayPoints
def doMatching(dift, beginningFrame, endFrame, prompt, sizeFinal, sizeNetwork, beginningPoints):
    """
    Takes in the beginning frame and one of the inference frames and does the calculations on them. 
    This basically is the same as it was before changing for multiple inference frames, just call on each individually. 
    """
    #get features to do interesting stuff with. 
    cos = nn.CosineSimilarity(dim=1)
    numPoints = beginningPoints.shape[0]
    #use sizeNetwork for diffusion calculation. 
    startCalc = time.time()
    features = diffusionCalc(dift, [beginningFrame, endFrame], [prompt, prompt], sizeNetwork)
    endCalc = time.time()
    print("Time Calculate Features: {} seconds".format(endCalc-startCalc))
    numChannels = features.shape[1]
    #1 x channelDepth x imgHeightDif ximgWidthDif
    #upsample feature map until it has the dimensions of the image we desire. 
    #will definitely increase in size. this is likely to be a place where size effects the results. 
    startUp = time.time()
    #get these upsampled feature sizes with sizeFinal. 
    beginningFeaturesImage = nn.Upsample(sizeFinal, mode='bilinear')(features[0].unsqueeze(0))
    
    #don't need to unsqueeze with colon
    endFeaturesImage = nn.Upsample(sizeFinal, mode = "bilinear")(features[1:])
    endUp = time.time()
    print("Time Upsampling: {} seconds".format(endUp-startUp))
    del features
    endPoints = np.zeros_like(beginningPoints, dtype = np.uint16)
    startProd = time.time()
    for i in range(numPoints):
        x = beginningPoints[i, 0]
        y = beginningPoints[i, 1]
        
        #not sure how to vectorize this.
        beginningFeatureVector = beginningFeaturesImage[0, :, y, x].view(1, numChannels, 1, 1)
        cosMap = cos(beginningFeatureVector, endFeaturesImage).cpu().numpy()
        del beginningFeatureVector
        #print("shape cos map: ", cosMap.shape)
        maxValue = cosMap[0].max()
        max_yx = np.unravel_index(cosMap[0].argmax(), cosMap[0].shape)
        del cosMap
        maxX = max_yx[1].item()
        maxY = max_yx[0].item()
        endPoints[i, 0] = maxX
        endPoints[i, 1] = maxY
        
        
        #print("beginning coords: ", x, y)
        #print("max coords(x,y): ", maxX, maxY)
        #print("Max value: ", maxValue)
        gc.collect()
        torch.cuda.empty_cache()
    #now, want to pick out the point we wish to cosine with the end features. But want to do multiple points. 
    del beginningFeaturesImage
    del endFeaturesImage
    gc.collect()
    torch.cuda.empty_cache()
    endProd = time.time()
    print("Time inner for calc: {} seconds".format(endProd-startProd))
    return endPoints
def diffusionCalc(dift, listFrames, listPrompts, sizeNetwork):
    """
    Call to do the diffusion calls on any list of frames and prompts you want. 
    """
    ensemble_size = 10
    ft = []
    for i in range(len(listFrames)):
        #make sure not to record the gradients to save space. 
        with torch.no_grad():
            #FRAME CONVERTED HERE. 
            frame = listFrames[i]
            prompt = listPrompts[i]
            image = convertPIL(frame, sizeNetwork)
            #go from 0, 256 -> 0, 1 then go to -1, 1
            #Somewhere here it automatically formats the axes to be correct for input to the model. 
            img_tensor = (PILToTensor()(image) / 255.0 - 0.5) * 2
            #print("image size: ", img_tensor.shape)
            #gets the latents for a given step. 
            #up_ft_index is which upsampling block to choose from to get your learned features and such. 
            del image
            del frame
            gc.collect()
            torch.cuda.empty_cache()
            ft.append(dift.forward(img_tensor,
                           prompt=prompt,
                           ensemble_size=ensemble_size, up_ft_index = 1, t=26))
            del img_tensor

    ft = torch.cat(ft, dim=0)
    print("features shape: ", ft.shape)
    gc.collect()
    torch.cuda.empty_cache()
    return ft

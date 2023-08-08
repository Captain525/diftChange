import gc
import torch
from torchvision.transforms import PILToTensor
from src.models.dift_sd import SDFeaturizer
import numpy as np
import torch.nn as nn
from src.models.dift_sd import SDFeaturizer
from imageDisplay import displayImages, convertPIL
from dataTransfer import saveResults
def callDift(frames, points):
    """
    Frames size: 
    y, then x. 
    numVideos x 3 x desiredSize[1] x desiredSize[0] x 3
    points is numVideos x numPoints x 2
    """
    torch.cuda.set_device(0)
    #use default model weights. 
    dift = SDFeaturizer()
    sizeNetwork = 768
    sizeFinal = 768
    listResultPoints = []
    for i in range(frames.shape[0]):
        frame = frames[i]
        beginningFrame = frame[0]
        endFrame = frame[2]
        pointsFrame = points[i]
        #maybe add prompt later. 
        matchedArrayPoints = doMatching(dift, beginningFrame, endFrame, "", sizeFinal, sizeNetwork, pointsFrame)
        listResultPoints.append(matchedArrayPoints)
        #fix this. 
        saveResults(matchedArrayPoints, i)
    return np.stack(matchedArrayPoints)
def doMatching(dift, beginningFrame, endFrame, prompt, sizeFinal, sizeNetwork, beginningPoints):
    """
    takes in the beginning and end frames and the dift model and does the matching as desired. 
    BeginningPoints are numPOints by 2, x, y
    """
    #get features to do interesting stuff with. 
    cos = nn.CosineSimilarity(dim=1)
    numPoints = beginningPoints.shape[0]
    #use sizeNetwork for diffusion calculation. 
    features = diffusionCalc(dift, [beginningFrame, endFrame], [prompt, prompt], sizeNetwork)
    numChannels = features.shape[1]
    #1 x channelDepth x imgHeightDif ximgWidthDif
    #upsample feature map until it has the dimensions of the image we desire. 
    #will definitely increase in size. this is likely to be a place where size effects the results. 
    
    #get these upsampled feature sizes with sizeFinal. 
    beginningFeaturesImage = nn.Upsample(sizeFinal, mode='bilinear')(features[0].unsqueeze(0))
    
    #don't need to unsqueeze with colon
    endFeaturesImage = nn.Upsample(sizeFinal, mode = "bilinear")(features[1:])
    del features
    endPoints = np.zeros_like(beginningPoints)
    for i in range(numPoints):
        x = beginningPoints[i, 0]
        y = beginningPoints[i, 1]
        #not sure how to vectorize this.
        beginningFeatureVector = beginningFeaturesImage[0, :, y, x].view(1, numChannels, 1, 1)
        cosMap = cos(beginningFeatureVector, endFeaturesImage).cpu().numpy()
        del beginningFeatureVector
        print("shape cos map: ", cosMap.shape)
        maxValue = cosMap[0].max()
        max_yx = np.unravel_index(cosMap[0].argmax(), cosMap[0].shape)
        del cosMap
        maxX = max_yx[1].item()
        maxY = max_yx[0].item()
        endPoints[i, 0] = maxX
        endPoints[i, 1] = maxY
        print("beginning coords: ", x, y)
        print("max coords(x,y): ", maxX, maxY)
        print("Max value: ", maxValue)
        gc.collect()
        torch.cuda.empty_cache()
    #now, want to pick out the point we wish to cosine with the end features. But want to do multiple points. 
    del beginningFeaturesImage
    del endFeaturesImage
    gc.collect()
    torch.cuda.empty_cache()
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
            print("image size: ", img_tensor.shape)
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

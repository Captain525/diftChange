import pandas as pd
import numpy as np
from dataTransfer import getAnnotationPath
"""
This file contains methods dealing with loading annotations and different ways 
of choosing valid indices. 
"""
def annotations(name, link, oscar):
    """
    This works now, gets the annotations for a given name. Name in form categoryNumber
    """
    #is alpha gets only letters. This method gets rid of numbers at the end of the name. 
    category = "".join(list([val for val in name if val.isalpha()]))
    annotationFileName = getAnnotationPath(link, category, oscar)
    return loadAnnotations(annotationFileName)
    

def loadAnnotations(csvLink):
    """
    General method to load the annotations, however, we are able to pick the specific technique used to get specific indices. 
    """
    annotationCSV = pd.read_csv(csvLink)
    listAnnotations = annotationCSV.iloc(axis=1)[1].values.tolist()
    #print("list annotations: ", listAnnotations)
    return middleFirst(listAnnotations)
def middleFirst(listAnnotations):
    """
    Chooses the middle of the annotations, choosing the first of each. 
    """
    indices = -1*np.ones(shape = (3,), dtype=int)
    for i in range(3):
        try:
            index = listAnnotations.index(i+1)
            chosenIndex = getMiddleContig(index, listAnnotations)
            indices[i] = chosenIndex
        except:
            continue
    valid = True
    #if action never found don't care. 
    if indices[1] ==-1:
        indices[1] == indices[0]
    #check if the initial state and end state both exist. 
    if indices[0] == -1 or indices[2]==-1:
        valid = False
    return indices, valid

def getMiddleContig(contigStart, listAnnotations):
    """
    Helper method which is given the start of a contig of annotations then gets 
    the middle frame from the given contig. 
    """
    rightMost = False
    newArrayDiff = np.diff(listAnnotations[contigStart:])
    endIndex = np.nonzero(newArrayDiff !=0)[0][0]
    indexChoice = (endIndex+ int(rightMost))//2
    chosenIndex = contigStart + indexChoice
    return chosenIndex
def middleLogic(listAnnotations):
    """
    Chooses middle of annotations, 
    uses logic to choose the ones where the
    end state follows the first. 

    Need to find if a 3 follows a 1. 
    """
    indices = -1*np.ones(shape = (3,), dtype=int)
    try:
        #O(n) b ut good for now. 
        lastLocation3 = max(loc for loc, val in enumerate(listAnnotations) if val == 3)
        firstLocation1 = listAnnotations.index(1)
        if(lastLocation3<firstLocation1):
            raise Exception("Didn't follow the required logic")
        
    except:
        return 






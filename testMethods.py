def testLoadProcessAnnotations():
    list = [1,0, 0, 0, 1, 1, 2, 2, 2,2, 0, 0]
    for i in range(3):
        try:
            #if the given index doesn't exist in the labels, give it a dne. 
            index = list.index(i+1)
            print("index: ", index)
            #if this does exist, want this CONTIGUOUS stretch of frames, and to find the middle.
            newArrayDiff = np.diff(list[index:])
            print("diff: ", newArrayDiff)
            #starts with 0s until end
            #where is the change. List indices in order of where it isn't 0. 
            #gets first element in the tuple. 
            endIndices = np.nonzero(newArrayDiff !=0)[0]
            print(endIndices)
            #get the first index where that's nonzero
            endIndex = endIndices[0]
            print("end Index: ", endIndex)
            #if first index is nonzero, means there was just ONE. 
            #number of consecutive values is endIndex + 1. 
            

            #to get the leftmost, take (endIndex)/2 
            indexChoice = endIndex//2
            #choose rightmost value in the middle 2. 
            #indexChoice = (endIndex + 1)/2

            print("Index choice: ", indexChoice)
            chosenIndex = index + indexChoice
            print("chosen for int: {}".format(i+1), " is : ", chosenIndex)
        except:
            print("value: {}".format(i+1), " is not in list")
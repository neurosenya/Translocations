import os # for work with directories 
import numpy as np
from PIL import Image, ImageSequence # generally for image processing
import cv2
from image_proc_func import mat2gray,imadjust, pairwise, Align, BGR_correction, roicolor


#_____________________________________________Constants and names________________________________
Name_dir2 = 'D:\\Lab\\Translocations_HPCA\\Cell31\\corr'
Name_dir_proc = '\\bgr'
Name_seq_t = '\\p'
amin = 0
amax = 17000
MaskA = 'Fluorescence 435nm'
MaskB = 'Fluorescence FRET'
Name_MasterImg = 'Fluorescence 435nm'


g = 0.2
Nfiles = []
#_________________________________________________________________________________________________
# for loop that gets names of files in the directory
for r, d, f in os.walk(Name_dir2):
    for file in f:
        Nfiles.append(file)

#os.mkdir(Name_dir2 + Name_dir_proc) # creates a folder for processed images

# This loop counts .tif files in the directory 
count_tifs = []
for name in Nfiles:
    if name[-4:] == '.tif' and  name[0:len(MaskA)]:
        count_tifs.append(name)

#print(count_tifs)
#________________________________________Loop over .tif files________________________________________

ind = 0 # for keeping the no. of a .tif image
for i in count_tifs: 
    ind +=1 
    Name = i 
    Name505 = i[:-4]
    S = list(Name505)
    # change the name to "FRET"
    S[0:18] = 'Fluorescence  FRET'
    Name505 = ''.join(S)
    Name505 = Name505 + '.tif'
    path_to_tif = Name_dir2 + '\\' + Name

    Name_seq_temp1  = Name_dir2 + Name_dir_proc + '\\' + Name 
    Name_seq_temp2 = Name_dir2 + Name_dir_proc + '\\' + Name505 
    print(Name)
    img_tif = Image.open(path_to_tif)

    # loops over .png images in a .tif file: 2 PNG images per loop
    Img_big_float = np.zeros(np.shape(img_tif)) # it reads only the dimensions of a single image
#_____________________________________________________________________________________________
    frame_ind = 0
    for frame in ImageSequence.Iterator(img_tif):
        frame_ind += 1
        #print("max value of frame:", np.array(frame).max())  # here should be a vector summation over all frames in a .tif
        Img_big_float += np.array(frame)
    #______________________________background correction___________________________________________________________

    bgr = BGR_correction(Img_big_float, d, g)
    low = (bgr + 2.4)/amax # the value can be adjusted in order to extrac the cell
    bw = roicolor(Img_big_float, low, 1)



    # Adjusting bgr coordinates for each .tif file
    if ind == 1:
        NumCellPixels = np.sum(np.sum(bw))
    NumCellPixels_new = np.sum(np.sum(bw))


    while NumCellPixels_new > NumCellPixels:
        low = low + 0.1 / amax
        bw = roicolor(Img_big_float, low, 1)
        NumCellPixels_new = np.sum(np.sum(bw)) 

    while NumCellPixels > NumCellPixels_new:
        low = low - 0.1 / amax
        bw = roicolor(Img_big_float, low, 1)
        NumCellPixels_new = np.sum(np.sum(bw))
  
    print(NumCellPixels, NumCellPixels_new, bw.min())   
    frame_index = 0
    imlist = []
    for frame in ImageSequence.Iterator(img_tif):
        frame_index += 1
        frame = frame - (np.ones(np.shape(frame)) * bgr) 
        frame *= bw # we have values zero everywhere but a soma with dendrites
        imlist.append(Image.fromarray(frame))

    imlist[0].save(Name_seq_temp1, save_all=True, append_images=imlist[1:])
#_____________________________________finding the coordinates of somas__________________________________
    Img_big_float = (Img_big_float - bgr*np.ones(np.shape(Img_big_float)) * bw
    if ind == 1:
        SomaMax = np.max(np.max(Img_big_float))
        bw_soma = roicolor(Img_big_float, aMask*SomaMax, 1)

        XD = np.sum(bw_soma, 1) # making a vector in X-axis of an image

        X0 = 0 # coordinate from the right
        while XD[XO] == 0:
            X0 += 1

        if X0 > dXYMask:
            X0 -= dXYMask
        else:
            X0 = 0

        X1 = Xval # coordinate from the left
        while XD[Xval] == 0:
            X1 -= 1

        if X1 < Xval - dXYMask:
            X1 += dXYMask
        else:
            X1 = Xval
        # the same procedure for the Y-axis of the image
        YD = np.sum(bw_soma, 0)

        Y0 = 0 # the coordinate from the top
        while YD[Y0] == 0:
            Y0 += 1

        if Y0 > dXYMask:
            Y0 -= dXYMask
        else:
            Y0 = 1

        Y1 = Yval # the coordinate from the bottom
        while YD[Y1] == 0:
            Y1 -= 1

        if Y1 < Yval - dXYMask:
            Y1 += dXYMask
        else:
            Y1 = Yval

#_______________________________________________fotobleaching compensation_________________________________________
        

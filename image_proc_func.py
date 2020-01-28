import os # for work with directories 
import numpy as np
from PIL import Image, ImageSequence, ImageEnhance # generally for image processing

import cv2


def mat2gray(matrix, amin, amax):
	"""MATLAB equivalent of mat2gray"""
	matrix = np.asarray(matrix)
	# converts to float
	matrix = matrix.astype('float32') 
	# set thresholds for minimum intensity value and maximum
	matrix[matrix <= amin] = 0; matrix[matrix >= amax] = 1 
	# rescale the values that are not 0 and 1 to 0/1 scale
	matrix[matrix != 1] /= amax
	return matrix

def imadjust(matrix, perc = 1):
	'''MATLAB equivalent of imadjust. Enhances the contrast of image by saturating
	the bottom percent of pixels and top percent pf pixels by rescaling.'''
	matrix = matrix.astype('float32')
	 # rescale an image to [0,1] range if it is in [0,255]
	if matrix.max() > 1: # if the image is not in 0/1 scale
		matrix /= matrix.max()
		print('here')
	amin = matrix.min()
	amax = matrix.max()
	# find the value amax when perc% of pixels will be greater than amax
	while (np.count_nonzero(matrix >= amax)) / (np.shape(matrix)[0]*np.shape(matrix)[1]) <= (perc/100): 
		amax = amax - 0.001
	# find the value amin when perc% of pixels will be less than amin
	while (np.count_nonzero(matrix <= amin)) / (np.shape(matrix)[0]*np.shape(matrix)[1]) <= (perc/100):
		amin = amin + 0.001
	# rescale everuthing between amin and amax to [0,1] range with amin and amax
	matrix[(matrix > amin) & (matrix < amax)] = (matrix[(matrix > amin) & (matrix < amax)] - amin) / (amax - amin)
	#matrix *=255 # this line is not required, it is just my windows 10 image viewer cannot displa 0/1 images
	contrasted_image = Image.fromarray(matrix)
	return contrasted_image 

# taken from AV
def Align(Image1, Image2):
		Image1 = np.array(Image1)
		Image2 = np.array(Image2)
		def Gradient(Image):
			# Calculate the x and y gradients using Sobel operator
			grad_x = cv2.Sobel(Image, cv2.CV_32F, 1, 0, ksize = 3)
			grad_y = cv2.Sobel(Image, cv2.CV_32F, 0, 1, ksize = 3)
			# Combine the two gradients
			grad = cv2.addWeighted(np.absolute(grad_x), 0.5, np.absolute(grad_y), 0.5, 0)
			return grad
		
		Temp1 = cv2.resize(np.float32(Image1), dsize = (0, 0), fx = 1, fy = 1, interpolation = cv2.INTER_LANCZOS4)
		Temp2 = cv2.resize(np.float32(Image2), dsize = (0, 0), fx = 1, fy = 1, interpolation = cv2.INTER_LANCZOS4)
		warp_mode = cv2.MOTION_AFFINE
		WarpMatrix = np.eye(2, 3, dtype = 'float32')
		criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 5000,  1e-10)
		(cc, WarpMatrix) = cv2.findTransformECC(Gradient(Temp1), Gradient(Temp2), WarpMatrix, warp_mode, criteria, None, 1)
		WarpMatrix[:, 2] = WarpMatrix[:, 2] / 1
		return cv2.warpAffine(Image2, WarpMatrix, Image2.shape[::-1], flags=cv2.INTER_LANCZOS4 + cv2.WARP_INVERSE_MAP), WarpMatrix


def pairwise(iterable):
	''' function for iterating by two elements in a list'''
	a = iter(iterable)
	return zip(a, a)

def roicolor(img, low, high):
	''' MATLAB euqivalent of roicolor. Set pixels that less than low to 0 and
	pixels between low and high to 1'''
	img = np.array(img)
	img[img < low] = 0
	img[(img >= low) & (img <= high)] = 1
	img = img.fromarray(img)
	return img
import numpy as np
import pandas as pd
import cv2
from scipy.ndimage.interpolation import map_coordinates
from scipy.ndimage.filters import gaussian_filter
import matplotlib.pyplot as plt



# Function to distort image
def elastic_transform(image, alpha, sigma, alpha_affine, random_state=None):
	"""Elastic deformation of images as described in [Simard2003]_ (with modifications).
	.. [Simard2003] Simard, Steinkraus and Platt, "Best Practices for
		 Convolutional Neural Networks applied to Visual Document Analysis", in
		 Proc. of the International Conference on Document Analysis and
		 Recognition, 2003.

	 Based on https://gist.github.com/erniejunior/601cdf56d2b424757de5
	"""
	if random_state is None:
		random_state = np.random.RandomState(None)

	shape = image.shape
	shape_size = shape[:2]
	
	# Random affine
	center_square = np.float32(shape_size) // 2
	square_size = min(shape_size) // 3
	pts1 = np.float32([center_square + square_size, 
				[center_square[0]+square_size, center_square[1]-square_size], 
				center_square - square_size])
	pts2 = pts1 + random_state.uniform(-alpha_affine, alpha_affine, size=pts1.shape).astype(np.float32)
	M = cv2.getAffineTransform(pts1, pts2)
	image = cv2.warpAffine(image, M, shape_size[::-1], borderMode=cv2.BORDER_REFLECT_101)

	dx = gaussian_filter((random_state.rand(*shape) * 2 - 1), sigma) * alpha
	dy = gaussian_filter((random_state.rand(*shape) * 2 - 1), sigma) * alpha
	dz = np.zeros_like(dx)

	x, y, z = np.meshgrid(np.arange(shape[1]), np.arange(shape[0]), np.arange(shape[2]))
	indices = np.reshape(y+dy, (-1, 1)), np.reshape(x+dx, (-1, 1)), np.reshape(z, (-1, 1))

	return map_coordinates(image, indices, order=1, mode='reflect').reshape(shape)


im = cv2.imread("train/10_1.tif", -1)
im_mask = cv2.imread("train/10_1_mask.tif", -1)

# Merge images into separete channels (shape will be (cols, rols, 2))
im_merge = np.concatenate((im[...,None], im_mask[...,None]), axis=2)

# Apply transformation on image
im_merge_t = elastic_transform(im_merge, im_merge.shape[1] * 2, im_merge.shape[1] * 0.08, im_merge.shape[1] * 0.08)
# Split image and mask
im_t = im_merge_t[...,0]
im_mask_t = im_merge_t[...,1]
from __future__ import print_function

import os
import numpy as np
import cv2

from preprocess import elastic_transform 

data_path = './'

image_rows = 420
image_cols = 580


def create_train_data():
	train_data_path = os.path.join(data_path, 'train')
	images = os.listdir(train_data_path)
	total = len(images) / 2

	imgs = np.ndarray((total, 1, image_rows, image_cols), dtype=np.uint8)
	imgs_mask = np.ndarray((total, 1, image_rows, image_cols), dtype=np.uint8)

	imgs_t = np.ndarray((total, 1, image_rows, image_cols), dtype=np.uint8)
	imgs_mask_t = np.ndarray((total, 1, image_rows, image_cols), dtype=np.uint8)

	i = 0
	print('-'*30)
	print('Creating training images...')
	print('-'*30)
	for image_name in images:
		if 'mask' in image_name:
			continue
		image_mask_name = image_name.split('.')[0] + '_mask.tif'
		img = cv2.imread(os.path.join(train_data_path, image_name), cv2.IMREAD_GRAYSCALE)
		img_mask = cv2.imread(os.path.join(train_data_path, image_mask_name), cv2.IMREAD_GRAYSCALE)

		img = np.array([img])
		img_mask = np.array([img_mask])

		imgs[i] = img
		imgs_mask[i] = img_mask

		# do elastic transform
		img_new = cv2.imread(os.path.join(train_data_path, image_name), -1)
		img_mask_new = cv2.imread(os.path.join(train_data_path, image_mask_name), -1)
		img_merge = np.concatenate((img_new[...,None], img_mask_new[...,None]), axis=2)
		img_merge_t = elastic_transform(img_merge, img_merge.shape[1] * 2, img_merge.shape[1] * 0.08, img_merge.shape[1] * 0.08)
		imgs_t[i] = img_merge_t[...,0]
		imgs_mask_t[i] = img_merge_t[...,1]

		if i % 100 == 0:
			print('Done: {0}/{1} images'.format(i, total))
		i += 1
	print('Loading done.')

	np.save('imgs_train.npy', imgs)
	np.save('imgs_mask_train.npy', imgs_mask)
	print('Saving to .npy files done.')

	np.save('imgs_train_t.py', imgs_t)
	np.save('imgs_mask_train_t.npy', imgs_mask_t)
	print('Saving of elastic transform files to .npy done.')

def load_train_data():
	imgs_train = np.load('imgs_train.npy')
	imgs_mask_train = np.load('imgs_mask_train.npy')
	imgs_train_t = np.load('imgs_train_t.npy')
	imgs_mask_train_t = np.load('imgs_mask_train_t.npy')
	imgs_res = np.vstack((imgs_train, imgs_train_t))
	imgs_res_mask = np.vstack((imgs_mask_train, imgs_mask_train_t))
	return imgs_res, imgs_res_mask


def create_test_data():
	train_data_path = os.path.join(data_path, 'test')
	images = os.listdir(train_data_path)
	total = len(images)

	imgs = np.ndarray((total, 1, image_rows, image_cols), dtype=np.uint8)
	imgs_id = np.ndarray((total, ), dtype=np.int32)

	i = 0
	print('-'*30)
	print('Creating test images...')
	print('-'*30)
	for image_name in images:
		img_id = int(image_name.split('.')[0])
		img = cv2.imread(os.path.join(train_data_path, image_name), cv2.IMREAD_GRAYSCALE)

		img = np.array([img])

		imgs[i] = img
		imgs_id[i] = img_id

		if i % 100 == 0:
			print('Done: {0}/{1} images'.format(i, total))
		i += 1
	print('Loading done.')

	np.save('imgs_test.npy', imgs)
	np.save('imgs_id_test.npy', imgs_id)
	print('Saving to .npy files done.')


def load_test_data():
	imgs_test = np.load('imgs_test.npy')
	imgs_id = np.load('imgs_id_test.npy')
	return imgs_test, imgs_id

if __name__ == '__main__':
	create_train_data()
	create_test_data()

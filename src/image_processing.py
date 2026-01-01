from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import logging
import config

logger = logging.getLogger(__name__)

def grayscaling_image(image_path: str) -> str:
	try:
		logger.info('Grayscaling is started')

		img = Image.open(image_path)

		# Convert image to numpy array
		img_array = np.array(img)

		# Function that make convertation
		def grayscaling(rgb):
			# Calculate grayscale value
			return int(0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2])

		# Create a new list for gray Image
		gray_array = np.zeros((img_array.shape[0], img_array.shape[1]), dtype=np.uint8)

		# Iterate over each pixel and convert to grayscale
		for i in range(img_array.shape[0]):
			for j in range(img_array.shape[1]):
				gray_array[i, j] = grayscaling(img_array[i, j])

		# Convert the numpy array back to an image
		gray_image = Image.fromarray(gray_array, mode='L')

		old_image_name = image_path.split('/')[-1]
		# Reaname an image to add gray_ to the beggining
		new_image_name = 'gray_' + old_image_name
		logger.info(f'New image name - {new_image_name}')
		
		# Take all objects before image name
		not_full_path = image_path.split('/')[:-1]

		# Create a full path with new image name
		new_image_path = '/'.join(not_full_path) + '/' + new_image_name
		logger.info(f'New full path - {new_image_path}')

		gray_image.save(new_image_path)

		config.new_image_path = new_image_path
		config.grayscaling_flag = True
		config.message_to_display = 'Grayscaling was finished, you can check the new black and white pic, in the same directory where pic was'

		logger.info('Grayscaling is over')

	except Exception as e:
		logger.error(f'Error in grayscaling_image, error - {e}')

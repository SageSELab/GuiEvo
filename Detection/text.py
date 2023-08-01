from config import *
import cv2
import re
import pytesseract
from PIL import Image
from easyocr import Reader
import copy
import requests
import base64


def extract_text_color(image):
	image_array = Image.fromarray(image)
	color = '#%02x%02x%02x' % sorted(image_array.getcolors(image_array.size[0]*image_array.size[1]))[-1][1]
	return color


def extract_text(image):
	endpoint_url = "https://vision.googleapis.com/v1/images:annotate"
	headers = {'Content-Type': 'application/json'}
	_, encoded_image = cv2.imencode('.png', image)
	encoded_image = base64.b64encode(encoded_image).decode('utf-8')
	payload = {"requests":[{"image": {"content": encoded_image},"features":[{"type": "TEXT_DETECTION"}],"imageContext": {"languageHints": ['en']}}]}
	response = requests.post(endpoint_url, params={'key': api_key}, headers=headers, json=payload)
	response_data = response.json()

	if 'error' in response_data:
		detected_text = ""
	else:
		if 'textAnnotations' in response_data['responses'][0]:
			texts = response_data['responses'][0]['textAnnotations']
			if texts:
				detected_text = texts[0]["description"]
			else:
				detected_text = ""
		else:
			detected_text = ""
	return detected_text


def detect_text_changes(old_img, new_img):
	old_text = extract_text(old_img)
	new_text = extract_text(new_img)
	if old_text == new_text:
		text_changed = False
	else:
		text_changed = True

	old_text_color = extract_text_color(old_img)
	new_text_color = extract_text_color(new_img)
	if old_text_color == new_text_color:
		text_color_changed = False
	else:
		text_color_changed = True
	
	return text_changed, text_color_changed, new_text
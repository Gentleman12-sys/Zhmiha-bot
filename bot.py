from PIL import Image
import os, threading
# from moviepy.editor import VideoFileClip

a = os.path.basename('bot.py')
url = os.path.abspath('bot.py').replace(a, '')

def resizing(imagename, resize):
	global url
	input_image_path = url+imagename
	output_image_path = url+'test_'+imagename
	new_size = resize
	with Image.open(input_image_path) as image:
		image = image.resize(new_size)
		image.save(output_image_path, subsampling=0, quality=100)
	return output_image_path

# def resizing_video(videoname, resize):
# 	global url
# 	resize = list(resize)
# 	clip = VideoFileClip(url+videoname)
# 	clip_resized = clip.resize(width=resize[0], height=resize[1]) # make the height 360px ( According to moviePy documenation The width is then computed so that the width/height ratio is conserved.)
# 	clip_resized.write_videofile(url+'test_'+videoname)
# 	return url+'test_'+videoname

import telebot
from telebot import types

token = 'BotAPI'
bot = telebot.TeleBot(token)

@bot.message_handler(commands=['start'])
def start(message):
	bot.send_message(message.chat.id, 'Здравствуйте {1.username}, вас приветствует {0.first_name}. Отправьте фотографии и уровень сжиманию от 1 до 10 и бот отправит вам результат.'.format(bot.get_me(), message.from_user))

@bot.message_handler(content_types=['photo'])
def new_sizing_photo(message):
	try:
		photo_id = message.photo[-1].file_id
		file_info = bot.get_file(photo_id)
		file_path = file_info.file_path
		downloaded_file = bot.download_file(file_path)
		file_name = str(message.chat.id)+'.png' # Change the file name if desired
		with open(url+file_name, 'wb') as f:
		    f.write(downloaded_file)
		kb = types.InlineKeyboardMarkup()
		for i in range(10):
			spisok = list(map(str, [i+1, file_name, message.photo[-1].width, message.photo[-1].height]))
			kb.add(types.InlineKeyboardButton(text=str(i+1), callback_data=' '.join(spisok)))
		bot.send_message(message.chat.id, 'Во сколько раз вы хотите уменьшить фото', reply_markup=kb)
	except Exception as e:
		print(e)

@bot.callback_query_handler(func=lambda callback: '.png' in callback.data)
def callbackPhoto(callback):
	size = int(callback.data.split()[0])
	file_name = callback.data.split()[1]
	width = int(callback.data.split()[2])
	height = int(callback.data.split()[3])
	try:
		file_name_out = resizing(file_name, (width//size, height//size))
		photo_file = open(file_name_out, 'rb') # Change the file name if desired
		bot.send_photo(callback.message.chat.id, photo_file)
		photo_file.close()
		os.remove(file_name_out)
	except:
		bot.send_message(callback.message.chat.id, 'Данное фото удаленно из базы из-за времени\nПожалуйста переотправьте фото')


# @bot.message_handler(content_types=['video'])
# def new_sizing_video(message):
# 	print(message.video.file_id)
# 	print(message.video.width)
# 	try:
# 		video_id = message.video.file_id
# 		file_info = bot.get_file(video_id)
# 		file_path = file_info.file_path
# 		downloaded_file = bot.download_file(file_path)
# 		file_name = str(message.chat.id)+'.mp4' # Change the file name if desired
# 		with open(url+file_name, 'wb') as f:
# 		    f.write(downloaded_file)
# 		kb = types.InlineKeyboardMarkup()
# 		for i in range(2):
# 			spisok = list(map(str, [i+1, file_name, message.video.width, message.video.height]))
# 			kb.add(types.InlineKeyboardButton(text=str(i+1), callback_data=' '.join(spisok)))
# 		bot.send_message(message.chat.id, 'Во сколько раз вы хотите уменьшить видео', reply_markup=kb)
# 	except Exception as e:
# 		print(e)

# @bot.callback_query_handler(func=lambda callback: '.mp4' in callback.data)
# def callbackVideo(callback):
# 	bot.send_message(callback.message.chat.id, 'Ждите')
# 	size = int(callback.data.split()[0])
# 	file_name = callback.data.split()[1]
# 	width = int(callback.data.split()[2])
# 	height = int(callback.data.split()[3])
# 	try:
# 		file_name_out = resizing_video(file_name, (width//size, height//size))
# 		photo_file = open(file_name_out, 'rb') # Change the file name if desired
# 		bot.send_video(callback.message.chat.id, photo_file)
# 		photo_file.close()
# 		os.remove(file_name_out)
# 	except Exception as e:
# 		print(e)
# 		bot.send_message(callback.message.chat.id, 'Данное видео удаленно из базы из-за времени\nПожалуйста переотправьте фото')

def deliting():
	import time
	global url
	t = time.time()
	while True:
		if (time.time()-t) >= 60*60*2:
			from os.path import isfile, join
			onlyfiles = [f for f in os.listdir(url) if isfile(join(url, f))]
			for file in onlyfiles:
				if '.py' not in file:
					os.remove(url+file)
			t = time.time()

threading.Thread(target=bot.infinity_polling).start()
threading.Thread(target=deliting).start()
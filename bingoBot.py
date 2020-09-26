# coding=utf-8


import json
import requests
import datetime
import time
import urllib
import sys
import math
import random

######################################################################
#################### PARÁMETROS MODIFICABLES #########################
######################################################################

TOKEN = "" ##IMPORTANTE: añade aquí el token de bot que te proporcionará @BotFather al crear tu bot

ADMIN = [112157322]

gamesOngoing = {}


######################################################################

URL = "https://api.telegram.org/bot{}/".format(TOKEN)


def get_url(url):
	response = requests.get(url)
	content = response.content.decode("utf8")
	return content


def get_json_from_url(url):
	content = get_url(url)
	js = json.loads(content)
	return js


def get_updates(offset=None):
	url = URL + "getUpdates?timeout=500"
	if offset:
		url += "&offset={}".format(offset)
	js = get_json_from_url(url)
	return js


def get_last_update_id(updates):
	update_ids = []
	for update in updates["result"]:
		update_ids.append(int(update["update_id"]))
	return max(update_ids)

def get_last_chat_id_and_text(updates):
	num_updates = len(updates["result"])
	last_update = num_updates - 1
	text = updates["result"][last_update]["message"]["text"]
	chat_id = updates["result"][last_update]["message"]["chat"]["id"]
	return (text, chat_id)


def build_keyboard(items):
	keyboard = [[item] for item in items]
	reply_markup = {"keyboard":keyboard, "one_time_keyboard": True}
	return json.dumps(reply_markup)


def send_message(text, chat_id, reply_markup=None):
	text = urllib.parse.quote_plus(text)
	url = URL + "sendMessage?text={}&chat_id={}&parse_mode=html".format(text, chat_id)
	if reply_markup:
		url += "&reply_markup={}".format(reply_markup)
	get_url(url)


def send_photo(fileID, chat_id):
	url = URL + "sendPhoto?&chat_id={}&photo={}&parse_mode=html".format(chat_id, fileID)
	get_url(url)

def send_gif(fileID, chat_id):
	url = URL + "sendAnimation?&chat_id={}&animation={}&parse_mode=html".format(chat_id, fileID)
	get_url(url)



def menu(updates):

	# print(timeStr)

	for update in updates["result"]:
		print(update)
		if 'message' in update and 'text' in update["message"]:
			text = update["message"]["text"]
			chat = update["message"]["chat"]["id"]
			user = update["message"]["from"]["id"]
			message = update["message"]["message_id"]
			if 'username' in update["message"]["from"]:			
				username = update["message"]["from"]["username"]
			else:
				username = update["message"]["from"]["first_name"]


			# print(chat)
			if text.startswith("/nueva_partida"):

				balls = list(range(100))

				lines = ""

				bingo = ""

				gameData = []

				gameData.append(balls)
				gameData.append(lines)
				gameData.append(bingo)

				if chat in gamesOngoing.keys():

					send_message("Ya existe una partida en curso en este chat. Espera a que termine para empezar otra.", chat)

				else:

					gamesOngoing.update({chat : gameData})

					send_message("¡Partida creada con éxito! \nAhora puedes sacar bolas usando el comando /bola. \nCuando consigas una línea, puedes cantarla usando /linea y si haces bingo, usa el comando /bingo para terminar la partida.", chat)

			elif text.startswith("/bola"):
				if chat in gamesOngoing.keys():
					data = gamesOngoing[chat]

					index = random.randrange(len(data[0]))

					number = data[0][index]
					data[0].pop(index)

					gamesOngoing.update({chat : data})

					send_message("¡El {}!".format(number), chat)

					if len(data[0]) == 0:
						send_message("¡Ya no quedan bolas en el bombo! Fin de la partida", chat)
						del gamesOngoing[chat]


				else:
					send_message("No hay ninguna partida activa en este chat. Empieza una con el comando /nueva_partida.", chat)

			elif text.startswith("/linea"):
				if chat in gamesOngoing.keys():
					data = gamesOngoing[chat]

					data[1] += "{},".format(username)

					gamesOngoing.update({chat : data})

					send_message("¡<b>{}</b> ha cantado línea!".format(username), chat)

				else:
					send_message("No hay ninguna partida activa en este chat. Empieza una con el comando /nueva_partida.", chat)		

			elif text.startswith("/bingo"):
				if chat in gamesOngoing.keys():	
					data = gamesOngoing[chat]

					data[2] += "{},".format(username)

					gamesOngoing.update({chat : data})

					send_message("¡<b>{}</b> ha cantado bingo!".format(username), chat)

					report = "¡Fin del juego! \n<b>Ganador(a):</b> {} \n<b>Cantaron líneas:</b> {}\n<b>Bolas extraídas:</b> {}.".format(username, data[1], 100 - len(data[0]))

					send_message(report, chat)

					del gamesOngoing[chat]


				else:
					send_message("No hay ninguna partida activa en este chat. Empieza una con el comando /nueva_partida.", chat)				

		else:
			print("Unsupported message")



def main():

	last_update_id = None
	clearSignal = int(sys.argv[1])

	#print(clearSignal)

	while True:
		updates = get_updates(last_update_id)
		if "result" in updates:
			if len(updates["result"]) > 0:
				# print(updates)
				last_update_id = get_last_update_id(updates) + 1
				if clearSignal == 1:
					print("Unsupported message")
					updates["result"][0].clear()
					clearSignal = 0

				menu(updates)


if __name__ == '__main__':
	main()
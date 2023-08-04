import asyncio
import os
import telebot
from telebot.async_telebot import AsyncTeleBot
import requests
import speech_recognition as sr
import subprocess
import datetime
import aiohttp
from gtts import gTTS
from token import *
logfile = str(datetime.date.today()) + '.log'

bot = AsyncTeleBot(token)


def audio_to_text(dest_name: str):
    r = sr.Recognizer()
    print(f'{dest_name}')
    message = sr.AudioFile(f'{dest_name}')
    with message as source:
        audio = r.record(source)
    result = r.recognize_google(audio, language="ru_RU")
    return result


@bot.message_handler(commands=['start'])
async def send_instructions(message):
    await bot.send_message(message.chat.id,
                           text=f"привет, {message.chat.username}! я бот для расшифровки гс. скинь гс, а я"
                                f" его расшифрую. также ты мне можешь отправить мне текст, а я его озвучу")


@bot.message_handler(content_types=['voice'])
async def get_audio_messages(message):
    try:
        print("Started recognition...")
        file_info = await bot.get_file(message.voice.file_id)
        path = r'C:/Users/red1c/no_voises/'+ file_info.file_path
        print(path)
        fname = os.path.abspath(path)
        print(f'{fname=}')
        doc = requests.get(f'https://api.telegram.org/file/bot{token}/{file_info.file_path}')
        with open(fname + '.oga', 'wb') as f:
            f.write(doc.content)
            print("Done oga!")
        process = subprocess.run(['ffmpeg', '-i', fname + '.oga'])
        result = audio_to_text(fname + '.oga')
        await bot.send_message(message.chat.id, format(result))
    except sr.UnknownValueError as e:
        await bot.send_message(message.chat.id, "Прошу прощения, но я не разобрал сообщение, или оно пустое...")
        with open(logfile, 'a', encoding='utf-8') as f:
            f.write(str(datetime.datetime.today().strftime("%H:%M:%S")) + ':'
                    + str(message.from_user.id) + ':' + str(message.from_user.first_name)
                    + '_' + str(message.from_user.last_name) + ':' + str(message.from_user.username) + ':' + str(
                message.from_user.language_code) + ':Message is empty.\n')
    except Exception as e:
        await bot.send_message(message.chat.id, "Что-то пошло через жопу")
        with open(logfile, 'a', encoding='utf-8') as f:
            f.write(str(datetime.datetime.today().strftime("%H:%M:%S")) + ':' + str(message.from_user.id) + ':' + str(
                message.from_user.first_name) + '_' + str(message.from_user.last_name) + ':' + str(
                message.from_user.username) + ':' + str(message.from_user.language_code) + ':' + str(e) + '\n')
    finally:
        os.remove(fname + '.wav')
        os.remove(fname + '.oga')


@bot.message_handler(commands=['text'])
async def audio_text(message):
    try:
        audio = gTTS(text=message.text, lang="ru", slow=False)
        audio.save(f"{message.chat.username}.mp3")
        audio = open(f"{message.chat.username}.mp3", 'rb')
        await bot.send_audio(message.chat.id, audio)
        audio.close()
    except Exception as ex:
        await bot.send_message(message.chat.id, "Что-то пошло через жопу")
        with open(logfile, 'a', encoding='utf-8') as f:
            f.write(str(datetime.datetime.today().strftime("%H:%M:%S")) + ':' + str(message.from_user.id) + ':' + str(
                message.from_user.first_name) + '_' + str(message.from_user.last_name) + ':' + str(
                message.from_user.username) + ':' + str(message.from_user.language_code) + ':' + str(ex) + '\n')
    finally:
        os.remove(f"{message.chat.username}.mp3")


if __name__ == '__main__':
    try:
        asyncio.run(bot.polling(none_stop=True, interval=0))
    except Exception as e:
        with open(logfile, 'a', encoding='utf-8') as f:
            f.write(str(datetime.datetime.today().strftime("%H:%M:%S")) + str(e) + '\n')
        bot.send_message(YOUR_USER_ID, str(datetime.datetime.today().strftime("%H:%M:%S")) + str(e))

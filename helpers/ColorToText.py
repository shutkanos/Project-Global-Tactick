from PIL import Image
im = Image.open('test2.png')

pixels = list(im.getdata())
Width, Height = im.size
colors = {(13, 255, 0, 255): "field",                 #поле
          (255, 132, 0, 152): "sown field",           #поле ржи
          (247, 0, 185, 255): "field of flowers",     #поле цветов
          (199, 226, 237, 255): "snow",               #снег, тундра
          (255, 255, 0, 255): "sand",                 #песок
          (20, 69, 17, 255): "forest",                #лес
          (75, 99, 42, 255): "swamp",                 #болото
          (9, 5, 247, 255): "water",                  #вода
          (0, 187, 255, 255): "ice",                  #лёд
          (84, 84, 84, 255): "mountain",              #гора
          (120, 120, 120, 255): "mine",               #шахта
          (0, 0, 0, 255): "canyon",                   #коньён
          (53, 27, 71, 255): "city",                  #город
          (80, 44, 105, 255): "settlement",           #поселение
          (109, 48, 150, 255): "camp",                #лагерь
          (89, 43, 43, 255): "highway",               #шоссе
          (130, 55, 55, 255): "road"}                 #дорога

colors2 = {(255, 255, 255, 255): None,
           (237, 197, 197, 255): "spawn"}

pixels = [pixels[i * Width:(i + 1) * Width] for i in range(Height)]
pixels = [[colors[pixels[i][j]] for j in range(Width)] for i in range(Height)]
print(pixels)

"""
import telebot
from io import BytesIO
bot = telebot.TeleBot('6268451123:AAHelhORTuP3EUP_UeVDOHV1EQ5CsQgcKWM')

@bot.message_handler(commands=['start'])
def GetMess(mess):
    bio = BytesIO()
    bio.name = 'map.png'
    MapForTeam.save(bio, 'PNG')
    bio.seek(0)
    bot.send_photo(mess.chat.id, photo=bio)

bot.polling(none_stop=True, interval=0)
"""

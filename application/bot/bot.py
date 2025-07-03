import requests
import datetime
from bs4 import BeautifulSoup
from application import models
import pymorphy2
from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw
import os
import tweepy
import telegram



import locale
locale.setlocale(locale.LC_TIME, "ru_RU.utf8")

import environ
env = environ.Env()

def pogibli(num):
    if num[-1] in ["1"] and num != '11':
        return "погиб"
    else:
        return "погибли"


def postradali(num):
    if num[-1] in ["1"] and num != '11':
        return "пострадал"
    else:
        return "пострадали"


def get_word_form(word, number):
    morph = pymorphy2.MorphAnalyzer()
    result = morph.parse(word)[0].make_agree_with_number(int(number)).word
    if result == "людей":
        return "человек"
    return result


def get_today_data():
    response = requests.get(
        'https://xn--90adear.xn--p1ai/',
        timeout=60,
        proxies={'https': env('PROXY') or None}
    )
    soup = BeautifulSoup(response.text, 'html.parser')

    block_count = soup.find("table", "b-crash-stat")

    source_date = block_count.find("th").text.strip().split(" ")[-1]
    date = datetime.datetime.strptime(source_date, '%d.%m.%Y').date()
    string_date = date.strftime("%-d %B")
    weekday = date.strftime("%A").lower()

    data_blocks = block_count.findAll("tr")
    crashes_num = str(data_blocks[1].findChildren()[1].text)
    crashes_deaths = str(data_blocks[2].findChildren()[1].text)
    crashes_child_deaths = str(data_blocks[3].findChildren()[1].text)
    crashes_injured = str(data_blocks[4].findChildren()[1].text)
    crashes_child_injured = str(data_blocks[5].findChildren()[1].text)

    brief_data_item, created = models.BriefData.objects.get_or_create(
        date=date
    )
    brief_data_item.dtp_count = crashes_num
    brief_data_item.death_count = crashes_deaths
    brief_data_item.injured_count = crashes_injured
    brief_data_item.child_death_count = crashes_child_deaths
    brief_data_item.child_injured_count = crashes_child_injured
    brief_data_item.save()

    if created:
        return {
            "date": date,
            "weekday": weekday,
            "string_date": string_date,
            "crashes_num": crashes_num,
            "crashes_deaths": crashes_deaths,
            "crashes_child_deaths": crashes_child_deaths,
            "crashes_injured": crashes_injured,
            "crashes_child_injured": crashes_child_injured
        }
    else:
        return None


def generate_text(data, post_type):
    morph = pymorphy2.MorphAnalyzer()
    if post_type == "today_post":
        return (data['string_date'] + ", " + data['weekday'] + ", в ДТП " + pogibli(data['crashes_deaths']) + " " + data[
            'crashes_deaths'] + " " + get_word_form("человек", data['crashes_deaths']))
    elif post_type == "week_post":
        return (
        "За последнюю неделю в ДТП " + pogibli(data['crashes_deaths']) + " " + data['crashes_deaths'] + " " + get_word_form("человек", data['crashes_deaths']))
    elif post_type == "month_post":
        return (
        "За " + morph.parse(data['date'].strftime("%B"))[0].inflect({'nomn'}).word + " в ДТП " + pogibli(data['crashes_deaths']) + " " + data['crashes_deaths'] + " "  + get_word_form("человек", data['crashes_deaths']))


def make_img(source):
    img = Image.open(os.path.dirname(os.path.abspath(__file__)) + "/template.png").convert('RGBA')
    W, H = (1138, 630)

    logo = Image.open(os.path.dirname(os.path.abspath(__file__)) + "/logo.png").convert('RGBA')
    logo_w, logo_h = logo.size
    logo = logo.resize((int(logo_w/2.3),int(logo_h/2.3)), Image.ANTIALIAS)
    logo_w, logo_h = logo.size
    #logo.show()


    #date_font = ImageFont.truetype("fonts/Roboto-Regular.ttf", 35)
    #header_font = ImageFont.truetype("fonts/Roboto-Bold.ttf", 32)
    #number_font = ImageFont.truetype("fonts/Roboto-Bold.ttf", 140)
    number_font = ImageFont.truetype(os.path.dirname(os.path.abspath(__file__)) + "/Circe-Regular.ttf", 300)
    text_font = ImageFont.truetype(os.path.dirname(os.path.abspath(__file__)) + "/Circe-Regular.ttf", 45)
    low_line_font = ImageFont.truetype(os.path.dirname(os.path.abspath(__file__)) + "/Circe-Regular.ttf", 32)

    crashes_deaths_ratio = W/2

    draw = ImageDraw.Draw(img)

    # number
    text = source['crashes_deaths']
    w, h = draw.textsize(text, font=number_font)
    draw.text((crashes_deaths_ratio - w / 2, -0.02*H), text, (253, 0, 0), font=number_font)

    # text first line
    text = get_word_form("человек", source['crashes_deaths']) + " " + pogibli(source['crashes_deaths']) + " в ДТП"
    w, h = draw.textsize(text, font=text_font)
    draw.text((crashes_deaths_ratio - w / 2, 0.55*H), text, (255, 255, 255), font=text_font)

    # text second line
    text = "на дорогах России "
    w_text, h_text = draw.textsize(text, font=text_font)
    w, h = draw.textsize(text + source['string_date'], font=text_font)
    w_coord = crashes_deaths_ratio - w / 2
    h_coord = 0.65 * H
    draw.text((w_coord, h_coord), text, (255, 255, 255), font=text_font)

    text = " " + source['string_date'] + " "
    w_string, h_string = draw.textsize(text, font=text_font)
    draw.rectangle(((w_coord + w_text, h_coord*1.01),(w_coord + w_text + w_string, (h_coord + h)*1.01)), fill="white")
    draw.text((w_coord + w_text, 0.65 * H), text, (0, 0, 0), font=text_font)

    # low line
    low_line = int(0.85 * H)
    img.paste(logo, (int(0.09*W), low_line, int(int(0.09*W) + logo_w), int(low_line + logo_h)), logo)

    text = "гибдд.рф, " + source['date'].strftime("%Y")
    w, h = draw.textsize(text, font=low_line_font)
    draw.text((crashes_deaths_ratio - w / 2, low_line*0.98), text, (56,56,56), font=low_line_font)

    text = "dtp-stat.ru"
    draw.text((int(0.78*W), low_line*0.98), text, (255, 255, 255), font=low_line_font)

    img.save(os.path.dirname(os.path.abspath(__file__)) + "/img.png")


def send_tweet(text):
    consumer_key = env('TWITTER_CONSUMER_KEY')
    consumer_secret = env('TWITTER_CONSUMER_SECRET')
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    access_token = env('TWITTER_CONSUMER_TOKEN')
    access_token_secret = env('TWITTER_CONSUMER_TOKEN_SECRET')
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
    apiNew = tweepy.Client(
        access_token=access_token,
        access_token_secret=access_token_secret,
        consumer_key=consumer_key,
        consumer_secret=consumer_secret
    )

    filename = os.path.dirname(os.path.abspath(__file__)) + "/img.png"
    media = api.simple_upload(filename)
    api.create_media_metadata(media_id=media.media_id, alt_text="")
    apiNew.create_tweet(text=text, media_ids=[media.media_id])


def send_telegram_post(text):
    bot = telegram.Bot(token=env('TELEGRAM_TOKEN'))

    channels_str = os.getenv('TELEGRAMM_CHANNELS', '')
    channels = [ch.strip() for ch in channels_str.split(';') if ch.strip()]

    photo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img.png")
    
    with open(photo_path, 'rb') as photo:
        for channel in channels:
            bot.sendPhoto(channel, photo, caption=text)
            photo.seek(0)


def main(message="today"):
    if message == "today":
        data = get_today_data()
        if data:
            text = generate_text(data, "today_post")
            make_img(data)

            if os.getenv("SEND_TWEETER") == "1":
                send_tweet(text)

            if os.getenv("SEND_TELEGRAM") == "1":
                send_telegram_post(text)

            if os.getenv("SEND_VK") == "1":
                send_vk_post(text)
#Telegram bot

import telebot
import json
import requests
from datetime import date
from haversine import haversine, Unit

#returns boolean meaning of includence to the area
def geo_distance(coor1, coor2):
    distance=haversine(coor1,coor2)
    if distance>2:
        return False
    else:
        return True

#returns amount of events in radius of 2km, and creates json file with all events 
def near_coordinates(lat,lon,username,cnt):
    url = "https://m.egov.kz/covid-proxy-app/api/v1/covid/patient"
    r = requests.get(url)
    newdata = r.json()
    point=[]

    for a in newdata:
        if a['longtitude']=='76.1750.2':
            a['longtitude']='76.17502'

    for a in newdata:
        b=[float(lat),float(lon)]
        c=[float(a['latitude']),float(a['longtitude'])]
        if geo_distance(b,c):
            point.append(a)
            cnt+=1
            #print(geo_distance(b,c))
            
    #print(p,s)
    with open('adress_data/'+str(username)+".json", 'w') as file:
	    file.write(json.dumps(point))
    
    return cnt

#return list [lat,long] of 1st and 2nd event respectively
def get_json1():
    with open('covid-new.json', 'r') as file:
	    points = json.load(file)
    p=[]
    p.append(points[0]['latitude'])
    p.append(points[0]['longtitude'])
    return p
def get_json2():

    with open('covid-new.json', 'r') as file:
	    points = json.load(file)
    s=[]
    s.append(points[1]['latitude'])
    s.append(points[1]['longtitude'])
    
    return s

#returns list with [lat,long]
def ad_co(adress):
    text=adress.replace(',','').replace(' ','+')     #яндекс ключ, загугли)
    url = "https://geocode-maps.yandex.ru/1.x/?apikey=bf4d42de-11c8-4f5c-ba5b-5816d2277853&format=json&geocode="+text 
    r = requests.get(url)
    newdata = r.json()
    data=newdata['response']["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["Point"]["pos"].replace('"',"").split()
    return data

#returns adress
def co_ad(g,gg):

    url = "https://geocode-maps.yandex.ru/1.x/?apikey=bf4d42de-11c8-4f5c-ba5b-5816d2277853&format=json&geocode="+str(gg)+'+'+str(g)
    r = requests.get(url)
    newdata = r.json()
    data=newdata["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["metaDataProperty"]["GeocoderMetaData"]["text"]
    return data

bot = telebot.TeleBot('#Телеграм апи бота')

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Привет, введите нужный адрес, мы найдем зараженные места рядом. Вначале пишите слово "адрес" например "Адрес алматы крамского 14"')



@bot.message_handler(content_types=['text'])
def send_text(message):
    
    if message.text.split()[0].lower()=='адрес':
        username=message.from_user.first_name
        print(username)
        coor=ad_co(message.text)
        count=near_coordinates(coor[1],coor[0],username,0)
        bot.send_message(message.chat.id,'По данным адресам найдено ' +str(count)+ ' очагов заражения в радиусе 2 км. Хотите узнать их адреса?')
    if (message.text.lower()=='да'):
        with open('adress_data/'+str(username)+".json", 'r') as file:
            points = json.load(file)
            for a in points:
                bot.send_message(message.chat.id,co_ad(a['latitude'],a['longtitude']))
    elif (message.text.lower()=='нет'):
        with open('adress_data/'+str(username)+".json", 'r') as file:
            points = json.load(file)
            for a in points:
                bot.send_message(message.chat.id,'Берегите себя')
    else:
        pass
    print("Ввели "+message.text)
    print()

bot.polling()


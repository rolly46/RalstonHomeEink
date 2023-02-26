
import requests,pdf2image
from bs4 import BeautifulSoup
from PIL import Image, ImageFont, ImageDraw, ImageEnhance
from flask import Flask, send_file, Response,json
import numpy as np
import cv2
import io 
from utils import prepare_image
# need pip install pdf-info as well
# also other dependacies here https://github.com/Belval/pdf2image
import pytz
from dotenv import dotenv_values
import json 
import math
from datetime import datetime, time,timedelta


app = Flask(__name__)

# local config
config = dotenv_values(".env")






# Endpoint for Club Lime Gym Utilisation 
@app.route('/servegym')
def serve_gym():
    logo_img, logo_img_width, logo_img_height = prepare_image(fetchNDrawGym())
    global i

    response = Response(
            response=logo_img.tobytes(),
            headers={
                'Image-Width': logo_img_width,
                'Image-Height': logo_img_height
            }
        )

    return response


# Endpoint for NYT Front Page
@app.route("/servenyt")
def serve_nyt():
    logo_img, logo_img_width, logo_img_height = prepare_image(fetchNYPageWSave())
    global i

    response = Response(
            response=logo_img.tobytes(),
            headers={
                'Image-Width': logo_img_width,
                'Image-Height': logo_img_height
            }
        )

    return response

# Endpoint for Eink Prefs (Old)
# @app.route("/prefs")
# def serve_prefs():
#     response = app.response_class(
#             response=json.dumps(config),
#             status=200,
#             mimetype='application/json'
#         )
#     return response

# Based on time and what's served (3-8pm GYM, NYT Outside of these times)
@app.route("/prefs")
def serve_prefs():
    
    config = {}
    
    if (isNowInTimePeriod(time(15,00), time(20,00), datetime.now().time())):
        config = {
        "MODE":"http://112.213.36.7:12345/servegym",
        "SLEEPTIME" : 15
        }
        
    else:
        # Get the current time
        now = datetime.now()
        print("SYSTEM TIME SHOWS: " + now.strftime("%m/%d/%Y, %H:%M:%S"))
        # Set the target time for 3pm
        target_time = now.replace(hour=15, minute=1, second=0, microsecond=0)
        # If current time is already past 3pm, add one day to the target time
        if now >= target_time:
            target_time = target_time + timedelta(days=1)
        # Calculate the difference between now and the target time in minutes
        time_difference = target_time - now
        sleeptime = int(time_difference.total_seconds() / 60)
        config = {
        "MODE":"http://112.213.36.7:12345/servenyt",
        "SLEEPTIME" : sleeptime
        }
    
        
    response = app.response_class(
            response=json.dumps(config),
            status=200,
            mimetype='application/json'
        )
    return response





# ~~~~~~~~~~~~~~~~~~
# Helper Functions 
def fetchNYPageWSave():
    today = datetime.now(tz=pytz.timezone('US/Hawaii'))
    # today = date.today()
    print(today.strftime('%d'))
    pdf = requests.get("https://static01.nyt.com/images/"+today.strftime('%Y')+"/"+today.strftime('%m')+"/"+today.strftime('%d')+"/nytfrontpage/scan.pdf",stream=True,timeout=30)
    image = pdf2image.convert_from_bytes(pdf.raw.read(),50)
    spinImage = image[0].transpose(Image.ROTATE_90)
    spinSave = spinImage.save("NYTToday.jpg")
    img_path = "NYTToday.jpg"
    return cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)

def fetchGARDPageWSave():
    today = datetime.now(tz=pytz.timezone('US/Hawaii'))
    pdf = requests.get("https://static01.nyt.com/images/"+today.strftime('%Y')+"/"+today.strftime('%m')+"/"+today.strftime('%d')+"/nytfrontpage/scan.pdf",stream=True,timeout=30)
    image = pdf2image.convert_from_bytes(pdf.raw.read(),50)
    spinImage = image[0].transpose(Image.ROTATE_90)
    spinSave = spinImage.save("NYTToday.jpg")
    img_path = "NYTToday.jpg"
    return cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)

def fetchNDrawGym():
    # get gym load value 
    URL = "https://www.clublime.com.au/default/includes/display_objects/custom/members/remote/clubload.cfm?cid=1&showone=&isMobile=false"
    r = requests.get(URL)  
    soup = BeautifulSoup(r.content, 'html5lib') # If this line causes an error, run 'pip install html5lib' or install html5lib
    gymload = float(soup.find_all("progress", {'class':'html5'})[0]['value'])
    print(gymload)
    
    upscaling = 2
    
    # create image or load your existing image with out=Image.open(path). Computed to the resolution of the Eink. 
    out = Image.new("RGB", (540*upscaling, 960*upscaling), (255, 255, 255))
    d = ImageDraw.Draw(out)

    # draw the progress bar to given location, width, progress and color
    # x, y, w, h, progress
    d = drawProgressBar(d, 100*upscaling, 620*upscaling, 420*upscaling, 300*upscaling, gymload,upscaling)
    outroate = out.transpose(Image.ROTATE_90)
    outroate.save("GYMLoadNow.png")
    img_path = "GYMLoadNow.png"
    return cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)

def fetchClassTimes():
    
    classdetails = {}
    # get gym load value 
    today = datetime.now()
    URL = "https://www.clublime.com.au/default/includes/display_objects/custom/classes/remote/classes.cfm?classid=80&isMobile=false&classdate=%7Bts%20%2720"+today.strftime('%y-%m-%d')+"%2000:00:00%27%7D&locationid=3&Region=ACT&show=lime&t=9E8B337C534A3AC0F4E352E5885E32E9FB917A21&{%22t%22:%229E8B337C534A3AC0F4E352E5885E32E9FB917A21%22}"
    print(UnicodeTranslateError)
    r = requests.get(URL)  
    soup = BeautifulSoup(r.content, 'html.parser') # If this line causes an error, run 'pip install html5lib' or install html5lib
    strongs = soup.findAll('strong')
    print("Contents is: " + str(strongs))
    
    return classdetails


# HELPER Functions
# https://stackoverflow.com/questions/66886200/how-do-you-make-a-progress-bar-and-put-it-on-an-image
def drawProgressBar(d, x, y, w, h, progress, upscalingtext,bg="grey", fg="black"):
    # draw background
    d.rectangle((x, y, x+w, y+h), outline ="black", width=3)

    # draw progress bar
    # w *= progress
    # box coords (x1,y1,x2,y2)
    d.rectangle((x*progress/100, y, (x+w)*progress/100, y+h),fill=fg)

    fonttitle = ImageFont.truetype("kanitbold.ttf", 50*upscalingtext)
    fontbodybold = ImageFont.truetype("kanitbold.ttf", 30*upscalingtext)
    fontbody = ImageFont.truetype("kanitlight.ttf", 30*upscalingtext)
    # TITLE
    d.text((98*upscalingtext, 5*upscalingtext),"Is CISAC Busy?",(0,0,0),font=fonttitle)
    # CAP TEXT
    d.text((136*upscalingtext, 570*upscalingtext),"Capacity currently at "+str(math.ceil(progress))+"%",(0,0,0),font=fontbodybold)
    # TIME TEXT
    current_time = datetime.now()
    # date_time = datetime.fromtimestamp(current_time)
    str_date_time = current_time.strftime("%d-%m, %H:%M")
    d.text((240*upscalingtext, 917*upscalingtext),"Updated: " + str_date_time,(0,0,0),font=fontbody)

    return d



# https://stackoverflow.com/questions/7877282/how-to-send-image-generated-by-pil-to-browser
def serve_pil_image(pil_img):
    img_io = io.BytesIO()
    pil_img.save(img_io, 'PDF', quality=70)
    img_io.seek(0)
    return send_file(img_io, mimetype='image/jpeg')
# ~~~~~~~~~~~~~~~~~~

# https://stackoverflow.com/questions/10048249/how-do-i-determine-if-current-time-is-within-a-specified-range-using-pythons-da
def isNowInTimePeriod(startTime, endTime, nowTime): 
    if startTime < endTime: 
        return nowTime >= startTime and nowTime <= endTime 
    else: 
        #Over midnight: 
        return nowTime >= startTime or nowTime <= endTime 



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=12345)
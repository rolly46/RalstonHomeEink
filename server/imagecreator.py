
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
from datetime import datetime
import pytz
from dotenv import dotenv_values
import json 


app = Flask(__name__)

# local config
config = dotenv_values(".env")




# Endpoint for Club Lime Gym Utilisation 
@app.route('/servegym')
def serve_gym():
# might be needed bad code 
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
# might be needed bad code 
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

# Endpoint for Eink Prefs
@app.route("/prefs")
def serve_prefs():
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

def fetchNDrawGym():
    # get gym load value 
    URL = "https://www.clublime.com.au/default/includes/display_objects/custom/members/remote/clubload.cfm?cid=1&showone=&isMobile=false"
    r = requests.get(URL)  
    soup = BeautifulSoup(r.content, 'html5lib') # If this line causes an error, run 'pip install html5lib' or install html5lib
    gymload = float(soup.find_all("progress", {'class':'html5'})[0]['value'])
    print(gymload)
    
    
    # create image or load your existing image with out=Image.open(path). Computed to the resolution of the Eink. 
    out = Image.new("RGB", (540, 960), (255, 255, 255))
    d = ImageDraw.Draw(out)

    # draw the progress bar to given location, width, progress and color
    # inputpic, x, y,w,h,progress
    d = drawProgressBar(d, 10, 480, 490, 25, gymload/100)
    out.save("GYMLoadNow.png")
    img_path = "GYMLoadNow.png"
    return cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)



# HELPER Functions
# https://stackoverflow.com/questions/66886200/how-do-you-make-a-progress-bar-and-put-it-on-an-image
def drawProgressBar(d, x, y, w, h, progress, bg="black", fg="red"):
    # draw background
    d.ellipse((x+w, y, x+h+w, y+h), fill=bg)
    d.ellipse((x, y, x+h, y+h), fill=bg)
    d.rectangle((x+(h/2), y, x+w+(h/2), y+h), fill=bg)

    # draw progress bar
    w *= progress
    d.ellipse((x+w, y, x+h+w, y+h),fill=fg)
    d.ellipse((x, y, x+h, y+h),fill=fg)
    d.rectangle((x+(h/2), y, x+w+(h/2), y+h),fill=fg)

    return d



# https://stackoverflow.com/questions/7877282/how-to-send-image-generated-by-pil-to-browser
def serve_pil_image(pil_img):
    img_io = io.BytesIO()
    pil_img.save(img_io, 'PDF', quality=70)
    img_io.seek(0)
    return send_file(img_io, mimetype='image/jpeg')
# ~~~~~~~~~~~~~~~~~~



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
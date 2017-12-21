import threading
import time
from flask import Flask
from flask import request
from flask import abort
from gpiozero import LED
from gpiozero import Button
from guizero import *
from PIL import Image
import base64
import io
import imageio

app = Flask(__name__)
alert = 0
image = ""

class LedAlertThread(threading.Thread):
   def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, verbose=None):
        super(LedAlertThread, self).__init__()
        self.target = target
        self.name = name

   def run(self):
       global alert
       green = LED(4)
       red = LED(17)
       yellow = LED(27)
       button = Button(18)
       while True:
            #print("alert = " + str(alert))
            if alert == 0:
                red.off()
                green.on()
            else:
                if button.is_pressed:
                    print("Button pressed!!")
                    alert = 0
                    continue
                green.off()
                red.on()
                time.sleep(0.5)
                red.off()
                yellow.on()
                time.sleep(0.5)
                yellow.off()
       return

class AppGUIThread(threading.Thread):
   gui = None
   def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, verbose=None):
        super(AppGUIThread, self).__init__()
        self.target = target
        self.name = name

   def dismissAlert(self):
       global alert
       alert = 0
       self.gui.destroy()

   def run(self):
       global imageName, risk
       self.gui = App(title="Robbery Detection",bgcolor="#FFFFFF",height=550,width=650)
       box = Box(self.gui, layout="grid")
       picture = Picture(box,image=imageName+".gif",grid=[0,0])
       riskText = Text(box,risk,grid=[1,0])
       takeAction = PushButton(box,command=self.dismissAlert,text="Take Action",grid=[2,0])
       #build_a_snowman = yesno("A question...", "Do you want to build a snowman?")
       #if build_a_snowman == True:
       #   info("Snowman", "It doesn't have to be a snowman")
       #else:
       #   error("Snowman", "Okay bye...")
       self.gui.display()
       return

@app.route('/')
def index():
    return "Hello, World!"

@app.route('/robberyDetection/api/v1.0/notify', methods=['POST'])
def notify():
    global alert, imageName, risk
    #print(str(request.json))
    json = request.json
    if "Image" in json:
        guiT = AppGUIThread(name='Gui_Thread')
        imageString = json["Image"]
        decodedBytes = base64.b64decode(bytes(imageString,'utf-8'))
        imageByte = io.BytesIO(decodedBytes)
        image = Image.open(imageByte)
        imageName = "./DetectedAt" + str(time.time())
        image.save(imageName+".PNG")
        imageList = [imageio.imread(imageName+".PNG")]
        imageio.mimsave(imageName+".gif",imageList)
        risk = json["Risk"]
        guiT.start()
    print("Is alert = %d" %(json["Alert"]))
    if not alert == 1:
        alert = json["Alert"]
    return "complete"

if __name__ == '__main__':
    ledT = LedAlertThread(name='Led_Thread')
    ledT.start()
    time.sleep(2)
    #guiT = AppGUIThread(name='Gui_Thread')
    #guiT.start()
    app.run(host='0.0.0.0', port=2401,debug=False)

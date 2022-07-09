import asyncio,time, os,math, time
os.environ['DISPLAY'] = ':0'
from bleak import BleakScanner,BleakClient
from bleak.exc import BleakError
from toggleScreen import toggle
import pyautogui as pag

address="4C:EB:D6:4D:50:82"
name="Nano 33 IoT"


WIDTH=pag.size()[0]
HEIGHT=pag.size()[1]


SENSITIVITY=100
SCROLL_SENSITIVITY=1


KEYBOARD_MODE=0
MOUSE_MODE=1



X=0
Y=1
STICK=2
GREEN=3
RED=4
CONTROL=5
EXTRA=6


"""Connect to the controller"""
async def connect():
	print("Searching for device...")
	devices = await BleakScanner.discover()
	device=None
	for d in devices:
		if(d.address==address):
			device=d
	if(not device): 
		print("Didn't find device.")
		print("Tries again in 5 seconds")
		time.sleep(5)
		return False,None
		
	print("Found device")
	client=BleakClient(device.address)
	try:
		await client.connect()
		return True,client
	except Exception as e:
		print(e)


"""Decode and return all signals from the controller"""
def decodeSignal(bytesArray,mode):
	xValue=bytesArray[0]-128 #center at 0
	yValue=bytesArray[1]-128
	xValue=xValue/128 if abs(xValue)>2 else 0 # not perfect input
	yValue=yValue/128 if abs(yValue)>2 else 0

	stickClick= bytesArray[2]& 1
	buttonClick=int((bytesArray[2]&2) /2)
	buttonClick2 =int((bytesArray[2]&4)/4 )
	buttonClick3=int((bytesArray[2]&8) /8)
	buttonClick4 =int((bytesArray[2]&16)/16 )
	return -scaling(yValue,mode),scaling(xValue,mode),1-stickClick,buttonClick,buttonClick2,buttonClick3,buttonClick4 # configure directions here.

def scaling(value,mode):
	if(mode==MOUSE_MODE):
		return mouseScaling(value)
	return keyBoardScaling(value)	

"""Modulate the mouse movement"""
def mouseScaling(value):
	sign=lambda x: math.copysign(1,x)
	return SENSITIVITY*value**2*sign(value)
""" Move mouse"""
def moveMouse(dx,dy):
	mx,my=pag.position()
	x=mx+dx
	y=my+dy
	x=min(WIDTH-3,x)
	x=max(1,x)
	y=min(HEIGHT-3,y)
	y=max(1,y)
	pag.moveTo(x,y,duration=0.01)
"""Mouse click"""
def click(newValue,oldValue,button="left",clicks=1):
	if(newValue==1 and newValue!=oldValue):
		pag.click(button=button,clicks=clicks)
"""Scroll"""
def scroll(value,oldValue, up):
	if(value==1):
		pag.scroll(SCROLL_SENSITIVITY if up else -SCROLL_SENSITIVITY)

def keyBoardScaling(value):
	return round(value)

"""Keyboard nav"""
def keyboardNavigation(x,oldX,y,oldY):
	if(x==1):
		pag.press("right")
	elif(x==-1 ):
		pag.press("left")	
	if(y==1 ):
		pag.press("down")
	elif(y==-1):
		pag.press("up")			
"""Keyboard click"""
def pressKey(newValue,oldValue,key):
	if(newValue==1 and newValue!= oldValue):
		pag.press(key)


def goBack(controller,newValue,oldValue):
	if(controller==0):
		pressKey(newValue,oldValue,"backspace")	
	else:
		if(newValue==1 and newValue!= oldValue):
			pag.hotkey("alt","f4")
		


"""Toggle screen"""
def toggleScreen(controller,button,oldButton):
	if(controller==1 and button!= oldButton and button==1):
		toggle()

"""Toggle mode"""
def toggleMode(controller,button,oldButton,mode):
	if(controller==1 and button!= oldButton and button==1):
		return 1-mode
	return mode



async def main():
	successful=False
	while not successful:
		successful,client=await connect()
	
	mode=MOUSE_MODE
	values=(0,0,0,0,0,0,0)
	while(client.is_connected):
		oldValues=values

		bytesArray=await client.read_gatt_char("e5c9e235-7cee-4640-ba95-7073c4afbbf8")
		values=decodeSignal(bytesArray,mode)

		mode=toggleMode(values[CONTROL],values[GREEN],oldValues[GREEN],mode)
		toggleScreen(values[CONTROL],values[EXTRA],oldValues[EXTRA])

		if(mode==MOUSE_MODE):
			moveMouse(values[X],values[Y])
			
			click(values[STICK],oldValues[STICK],clicks=2)
			click(values[GREEN],oldValues[GREEN])
			click(values[RED],oldValues[RED],button="right")
			

		else:
			keyboardNavigation(values[X],oldValues[X],values[Y],oldValues[Y])
			pressKey(values[STICK],oldValues[STICK],"enter")
			pressKey(values[GREEN],oldValues[GREEN],"enter")
			goBack(values[CONTROL],values[RED],oldValues[RED])


		

if __name__ == '__main__':
	try:
		while(True):
			try:
				asyncio.run(main())
			except BleakError:
				print("Bluetooth exception happened, will try to reconnect")
				time.sleep(5)
	except KeyboardInterrupt:
		print("Shutting down")

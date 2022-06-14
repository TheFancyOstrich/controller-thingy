import asyncio,time, os,math
os.environ['DISPLAY'] = ':0'
from bleak import BleakScanner,BleakClient
from bleak.exc import BleakError
import pyautogui as pag

address="4C:EB:D6:4D:50:82"
name="Nano 33 IoT"


WIDTH=pag.size()[0]
HEIGHT=pag.size()[1]

SENSITIVITY=40

SCROLL_SENSITIVITY=1

def moveMouse(dx,dy):
	mx,my=pag.position()
	x=mx+dx
	y=my+dy
	x=min(WIDTH-3,x)
	x=max(1,x)
	y=min(HEIGHT-3,y)
	y=max(1,y)
	pag.moveTo(x,y)

def click(newValue,oldValue,button="left",clicks=1):
	if(newValue==1 and newValue!=oldValue):
		pag.click(button=button,clicks=clicks)

def scroll(value,oldValue, up):
	if(value==1):
		pag.scroll(SCROLL_SENSITIVITY if up else -SCROLL_SENSITIVITY)


def decodeSignal(bytesArray):
	xValue=bytesArray[0]-128 #center at 0
	yValue=bytesArray[1]-128
	xValue=xValue/128 if abs(xValue)>10 else 0 # not perfect input
	yValue=yValue/128 if abs(yValue)>10 else 0

	stickClick= bytesArray[2]& 1
	buttonClick=int((bytesArray[2]&2) /2)
	buttonClick2 =int((bytesArray[2]&4)/4 )
	buttonClick3=int((bytesArray[2]&8) /8)
	buttonClick4 =int((bytesArray[2]&16)/16 )
	return -scaleRule(yValue),scaleRule(xValue),1-stickClick,buttonClick,buttonClick2,buttonClick3,buttonClick4 # configure directions here.

def scaleRule(value):
	sign=lambda x: math.copysign(1,x)
	return SENSITIVITY*value**2*sign(value)

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
async def main():
	successful=False
	while not successful:
		successful,client=await connect()
		
	leftClick=0
	rightClick=0
	doubleClick=0
	scrollUp=0
	scrollDown=0
	while(client.is_connected):
		oldLeftClick=leftClick
		oldRightClick=rightClick
		oldDoubleClick=doubleClick
		oldScrollUp=scrollUp
		oldScrollDown=scrollDown

		bytesArray=await client.read_gatt_char("e5c9e235-7cee-4640-ba95-7073c4afbbf8")
		xValue,yValue,leftClick,doubleClick,rightClick,scrollUp,scrollDown=decodeSignal(bytesArray)
		moveMouse(xValue,yValue)
			
		click(leftClick,oldLeftClick)
		click(rightClick,oldRightClick,button="right")
		click(doubleClick,oldDoubleClick,clicks=2)
		scroll(scrollUp,oldScrollUp,True)
		scroll(scrollDown,oldScrollDown,False)


if __name__ == '__main__':
	try:
		asyncio.run(main())
	except BleakError:
		print("Bluetooth exception happened, will try to reconnect")
		time.sleep(5)
		asyncio.run(main())
	
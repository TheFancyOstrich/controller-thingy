# mouse-thingy
Code to a bluetooth mouse thingy, built with an arduino.

### Install notes:
- install pyautogui, bleak and asyncio for python
- enable I2C in raspi config
- edit, if necessary, mouse.service to point to the location of bluetoothController.py
- add mouse.service to /home/pi/.config/systemd/user/mouse.service or similar

### Useful links:
- [About service managing python](https://www.linux.org/threads/restart-python3-scripts-if-they-exit-fail.38924/)

### Schematics:
Joystick with 5v, gnd, vrx ,vry, sw pins and unknown serial number, and 4 additional buttons (can of course be altered) all connected to an arduino 33 IoT . 

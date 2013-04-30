#! /usr/bin/python2.7

# client program

# import required modules
import os
import pygame, sys
import time
from pygame import locals
from time import sleep
import socket
import threading
import urllib

# detect OS
myOS = sys.platform
print "Operating System: " + str(myOS)

# set window location
x = 50
y = 50
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (x,y)

# initialize pygame module
pygame.init()

# set up joystick
joy = pygame.joystick
myJoystickID = joy.get_count() - 1
myJoystickName = ""
myJoystickAxisNum = 0
myJoystickButtonNum = 0
myJoystickHatNum = 0
x1 = 0
x2 = 0
y1 = 0
y2 = 0
triggers = 0

# get monitor resolution
monitorInfo = (pygame.display.Info().current_w, pygame.display.Info().current_h)
print "Monitor Resolution: " + str(monitorInfo)


# set up common functions -----------------------------------------------------------------------------------------------

# load logo
if myOS == "win32":
  logo = pygame.image.load(os.path.join(os.path.dirname(__file__), 'logo.png'))
else:
  logo = pygame.image.load("/home/pi/Desktop/wreXplorerChanged/logo.png")
icon = pygame.transform.scale(logo, (32,32))
logo = pygame.transform.scale(logo, (200,200))
logoPos = logo.get_rect()

# define Live Image display function
def displayImage():
  if myOS == "win32":
    urllib.urlretrieve("http://192.168.1.113/image.jpg", os.path.join(os.path.dirname(__file__), 'image.jpg')) #"http://192.168.1.113/image.jpg"
    image = pygame.image.load(os.path.join(os.path.dirname(__file__), 'image.jpg'))
  else:
    urllib.urlretrieve("http://192.168.1.113/image.jpg", "/home/pi/Desktop/wreXplorerChanged/image.jpg") #"http://192.168.1.113/image.jpg"
    image = pygame.image.load("/home/pi/Desktop/wreXplorerChanged/image.jpg")
  imagePos = image.get_rect()
  imagePos.centerx = background.get_rect().centerx
  imagePos.centery = background.get_rect().centery + 100
  background.blit(image, imagePos)

# define logo display function
def displayLogo(xOffset, yOffset):
  logoPos.centerx = background.get_rect().centerx + xOffset
  logoPos.centery = background.get_rect().top + yOffset
  background.blit(logo, logoPos)

# define data retrieval thread function
def updateInfo():
  while True:
    #Get all new data
    try:
      gatheredData = s.recv(1024)
      if "$" in gatheredData and "@" in gatheredData:
        print(gatheredData)
        param, gatheredData = gatheredData.split("$",1)
        gatheredData, param = gatheredData.split("@",1)
        dta1, rcvd, dta2, ltsSts, volts, lock = gatheredData.split(",")
        volts = round(((((float(volts))/100)/4.361)*14),2)
      else:
        print('Not enough data received' + gatheredData)
        dta1 = "?"
        rcvd = "?"
        dta2 = "?"
        ltsSts = "?"
        volts = "?"
        lock = "?"
    except socket.timeout:
      print('Socket Timeout')
      dta1 = "?"
      rcvd = "?"
      dta2 = "?"
      ltsSts = "?"
      volts = "?"
      lock = "?"
    
    # Clear display
    background.fill((200, 200, 200))
  
    # refresh Light Status text
    if ltsSts == "+":
      ltsSts = "ON"
    elif ltsSts == "-":
      ltsSts = "OFF"
    else:
      ltsSts = "?"
    displayText(('Light Status: ' + str(ltsSts)), 0, 40)
  
    # refresh Current Depth text
    displayText(('Current Depth: ' + str(dta1)+'ft'), 0, 80)
    
    # refresh Set Depth text
    displayText(('Set Depth: ' + str(dta2)+'ft'), 0, 120)
  
    # refresh depth lock text
    if lock == "+":
      lock = "ON"
    elif lock == "-":
      lock = "OFF"
    else:
      lock = "?"
    displayText(('Depth Lock: ' + str(lock)), 0, 160)
  
    # refresh Voltage text
    displayText(('Voltage: ' + str(volts)), 0, 200)
    
    # Display logo
    displayLogo(350,500)
    
    # Display image from live cam
    displayImage()

    # blit everything to the screen
    screen.blit(background, (0, 0))
    pygame.display.flip()
  
    # sleep for a second
    time.sleep(0.1)

# define text updating function
def displayText(newText, xOffset, yOffset):
  text = font.render(newText, 1, (10, 10, 10))
  textpos = text.get_rect()
  textpos.centerx = background.get_rect().centerx + xOffset
  textpos.centery = background.get_rect().top + yOffset
  background.blit(text, textpos)
  
# --------------------------------------------------------------------------------------------------------------------


# create window to display values
(width, height) = (900, 600)
pygame.display.set_icon(icon)
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('WreXplorer ONE Control Module')
pygame.display.flip()

# background
background = pygame.Surface(screen.get_size())
background = background.convert()
background.fill((200, 200, 200))

# add text
font = pygame.font.Font(None, 36)
text = font.render("Loading...", 1, (10, 10, 10))
textpos = text.get_rect()
textpos.centerx = background.get_rect().centerx
textpos.centery = background.get_rect().top + 320
background.blit(text, textpos)

displayLogo(0,200)

# blit everything to the screen
screen.blit(background, (0, 0))
pygame.display.flip()

sleep(3)

# set the socket parameters
socket.setdefaulttimeout(1)
host = '192.168.1.122'
port = 8080
addr = (host,port)

# set up joystick
try:
  myJoystick = joy.Joystick(myJoystickID)
  myJoystick.init()
  myJoystickName = myJoystick.get_name()
  myJoystickAxisNum = myJoystick.get_numaxes()
  myJoystickButtonNum = myJoystick.get_numbuttons()
  myJoystickHatNum = myJoystick.get_numhats()
  print "ID: " + repr(myJoystickID)
  print "Name: " + repr(myJoystickName)
  print "Number of Axis: " + repr(myJoystickAxisNum)
  print "Number of Buttons: " + repr(myJoystickButtonNum)
  print "Number of POV hats: " + repr(myJoystickHatNum)
except pygame.error:
  # Clear display
  background.fill((200, 200, 200))
  
  # refresh text
  displayText('ERROR: JOYSTICK NOT FOUND', 0, 320)
  
  # Display logo
  displayLogo(0,200)

  # blit everything to the screen
  screen.blit(background, (0, 0))
  pygame.display.flip()
  sleep(4)
  pygame.quit()
  sys.exit("Exit: No Joystick")
  
# Clear display
background.fill((200, 200, 200))

# refresh text
displayText('Connecting to WreXplorer ONE...', 0, 320)

# Display logo
displayLogo(0,200)

# blit everything to the screen
screen.blit(background, (0, 0))
pygame.display.flip()
sleep(2)

# create sockets
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
  s.connect(addr)
except socket.timeout:
  # Clear display
  background.fill((200, 200, 200))
  
  # refresh text
  displayText('ERROR: COULD NOT CONNECT', 0, 320)
  
  # Display logo
  displayLogo(0,200)

  # blit everything to the screen
  screen.blit(background, (0, 0))
  pygame.display.flip()
  sleep(4)
  pygame.quit()
  sys.exit("Exit: Failed connection")
  
# Clear display
background.fill((200, 200, 200))

# refresh text
displayText('Connected', 0, 320)

# Display logo
displayLogo(0,200)

# blit everything to the screen
screen.blit(background, (0, 0))
pygame.display.flip()
sleep(2)

# set messages
msg = 's'

# only send new messages
check1 = ""
send = True

# start data retrieval thread
t1 = threading.Thread(target=updateInfo)
t1.daemon = True
t1.start()

# Main control process
while True:
  if myJoystickName <> "Logitech Extreme 3D":
    for e in pygame.event.get():
      if e.type == pygame.QUIT:
        pygame.quit()
        sys.exit("Exit: Window Closed")
      if(check1 == 's'):
        send = True
      # get joystick values with OS specific setup
      if myOS == "win32":
        x1 , y1, triggers, y2, x2 = myJoystick.get_axis(0)*100, myJoystick.get_axis(1)*100, myJoystick.get_axis(2)*100, myJoystick.get_axis(3)*100, myJoystick.get_axis(4)*100
      else:
        x1 , y1, x2, y2, triggers = myJoystick.get_axis(0)*100, myJoystick.get_axis(1)*100, myJoystick.get_axis(2)*100, myJoystick.get_axis(3)*100, myJoystick.get_axis(4)*100
      # x1, y1, triggers, y2, x2 = windows
      # x1, y1, triggers, x2, y2 = linux
      if(y2>60):
        msg = 'x' # backward
      elif(y2<-60):
        msg = 'w' # forward
      elif(x2>60):
        msg = 'd' # right
      elif(x2<-60):
        msg = 'a' # left
      elif (x1>60):
        msg = 'e' # clockwise
      elif(x1<-60):
        msg = 'q' # counter-clockwise
      else:
        if(myJoystick.get_hat(0) == (0,1)):
          msg = 'z'# ascend
        elif(myJoystick.get_hat(0) == (0,-1)):
          msg = 'c' # descend
        elif(myJoystick.get_button(0) == True):
          msg = 'l' # lights on
        elif(myJoystick.get_button(1) == True):
          msg = 'k' # lights off
        elif(myJoystick.get_button(2) == True):
          msg = 'b' # toggle depth lock
        else:
          msg = 's' # null message
          send = True
  else:
	# get joystick values for each event call
    for e in pygame.event.get():
      if e.type == pygame.QUIT:
        pygame.quit()
        sys.exit("Exit: Window Closed")
      if(check1 == 's'):
        send = True
      x , y, z = myJoystick.get_axis(0) * 100, myJoystick.get_axis(1) * 100, myJoystick.get_axis(3) * 100
      # x , y, z
      if(y>60):
        msg = 'x' # backward
      elif(y<-60):
        msg = 'w' # forward
      elif(x>60):
        msg = 'd' # right
      elif(x<-60):
        msg = 'a' # left
      elif (z>60):
        msg = 'e' # clockwise
      elif(z<-60):
        msg = 'q' # counter-clockwise
      else:
        if(myJoystick.get_button(8)):
          msg = 'z'# ascend
        elif(myJoystick.get_button(10)):
          msg = 'c' # descend
        elif(myJoystick.get_button(2)):
          msg = 'l' # lights on
        elif(myJoystick.get_button(3)):
          msg = 'k' # lights off
        else:
          msg = 's' # null message
          send = True
  # send only new messages to server
  if check1<>msg and send == True:
    try:
      s.send(msg)
    except socket.timeout:
      print('Could not send')
  
    check1 = msg
    send = False
    
# close socket
UDPSock.close()

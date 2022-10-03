from controller import Robot
from controller import Motor
from controller import DistanceSensor
from controller import Camera
from controller import LED
from controller import Supervisor
import math
import time
robot = Robot()

# get the time step of the current world
timestep = 8
robot.step(timestep)

#camera     
cam = robot.getDevice("camera")
cam.enable(64)
# Leff motor, Right motor   
lm = robot.getDevice("left wheel motor")
lm.setPosition(float("inf"))
lm.setVelocity(0)

rm = robot.getDevice("right wheel motor")
rm.setPosition(float("inf"))
rm.setVelocity(0)

# Sensors
NB_GROUND_SENS = 8
gs = []
gsNames = [
    'gs0', 'gs1', 'gs2', 'gs3',
    'gs4', 'gs5', 'gs6', 'gs7'
]
for i in range(NB_GROUND_SENS):
    gs.append(robot.getDevice(gsNames[i]))
    gs[i].enable(timestep)

# LEDs
NB_LEDS = 5
leds = []
led_Names = [
    'led0', 'led1', 'led2', 'led3', 'led4'
]
for i in range(NB_LEDS):
    leds.append(robot.getDevice(led_Names[i]))

### Private Functions ###
# Function to control LEDs
def LED_Alert():
    if (robot.getTime() - initTime)*1000 % 3000 >= 2000:
        #leds[1].set(not(leds[1].get()))
        leds[1].set(1)
        #for i in range(NB_LEDS):
            #leds[i].set(not(leds[i].get()))
    return

# Waiting for completing initialization
### thí sinh không được bỏ phần này
initTime = robot.getTime()
while robot.step(timestep) != -1:
    if (robot.getTime() - initTime) * 1000.0 > 200:
        break


### Phần code cần chỉnh sửa cho phù hợp ##
# Định nghĩa các tín hiệu của xe
NOP = -4
MID = 0
LEFT = 1
RIGHT = -1
RIGHT_VUONG = -2
LEFT_VUONG = 2
FULL_SIGNAL  = 3
BLANK_SIGNAL = -3

# MAX_SPEED <= 1000
MAX_SPEED = 30
threshold = [330, 330, 330, 330, 330, 330, 330, 330]
preFilted = 0b00000000

# Biến lưu giá trị tỉ lệ tốc độ của động cơ
left_ratio = 0.0
right_ratio = 0.0

# Hàm đọc giá trị của sensors
def ReadSensors():
    gsValues = []
    filted = 0x00
    for i in range(NB_GROUND_SENS):
        gsValues.append(gs[i].getValue())
        if gsValues[i] > threshold[i]:
            filted |= (0x01 << (NB_GROUND_SENS - i - 1))
    #print(*gsValues, sep = '\t')
    return filted

# Phần code điều khiển xe

#xác định độ lệch của xe từ việc đọc giá trị cảm biến
def DeterminePosition(filted):
    if (filted == 0b11100111 or filted == 0b11101111 or filted == 0b11110111):
        return MID
    elif (filted == 0b10011111 or filted == 0b11001111 or filted == 0b11011111 or filted == 0b10111111 or filted == 0b11101111
    or filted == 0b01111111 or filted == 0b00111111 ):
        return LEFT
    elif (filted == 0b11111001 or filted == 0b11110011 or filted == 0b11111101 or filted == 0b11111011 or filted == 0b11110111
    or filted == 0b11111110 or filted == 0b11111100 ):
        return RIGHT
    elif filted == 0b11111111:
        return BLANK_SIGNAL
    elif filted == 0b00000000:
        return FULL_SIGNAL
    elif (filted == 0b10000111 or filted == 0b00000111 or filted == 0b00001111 or filted == 0b00011111 or filted == 0b11000111):
        return LEFT_VUONG
    elif (filted == 0b11100001 or filted == 0b11100000 or filted == 0b11110000 or filted == 0b11111000 or filted == 0b11100011):
        return RIGHT_VUONG
    return MID
       
#các hàm điều khiển xe di chuyển
def GoStraight():
    lm.setVelocity(1.0 * MAX_SPEED)
    rm.setVelocity(1.0 * MAX_SPEED)
    return
        
def TurnLeft():
    #if pos == :
    lm.setVelocity(0.5 * MAX_SPEED)
    rm.setVelocity(1.0 * MAX_SPEED)
    return  
def TurnRight():
    #if pos == :
    lm.setVelocity(1.0 * MAX_SPEED)
    rm.setVelocity(0.5 * MAX_SPEED)
    return

def TurnLeftVuong():
    for i in range(52):
        a = robot.step(timestep)
        lm.setVelocity(0.3 * MAX_SPEED)
        rm.setVelocity(1.3 * MAX_SPEED)
        
    return
def TurnRightVuong():
    for i in range(52):
        a = robot.step(timestep)
        lm.setVelocity(1.3 * MAX_SPEED)
        rm.setVelocity(0.3 * MAX_SPEED)
        
    return
def NgaTuLeft():
    print('T_L')
    for i in range(160):
        
        a = robot.step(timestep)
        lm.setVelocity(0.67 * MAX_SPEED)
        rm.setVelocity(1 * MAX_SPEED)
    return
def NgaTuRight():
    print('T_R')
    for i in range(160):
     
        a = robot.step(timestep)
        lm.setVelocity(1 * MAX_SPEED)
        rm.setVelocity(0.67 * MAX_SPEED)

    return
lastPos = 0  
# Main loop:
# Chương trình sẽ được lặp lại vô tận 
while robot.step(timestep) != -1:

    filted = ReadSensors()
    
    #pos: position - vị trí của xe
    pos = DeterminePosition(filted)
    # In ra màn hình giá trị của filted ở dạng nhị phân
    print('Position: ' + str(format(filted, '08b')), sep = '\t')
    print(pos )
    print('lastpos' + str(lastPos))
    #Gọi các hàm điều khiển
    if (pos == MID and lastPos == MID):
        GoStraight()
    elif (pos == LEFT and lastPos == MID) or (pos == LEFT and lastPos == LEFT) :
        TurnLeft()
    elif (pos == RIGHT and lastPos == MID) or (pos == RIGHT and lastPos == RIGHT):
        TurnRight() 
        
        
    if ((pos == BLANK_SIGNAL and lastPos ==LEFT_VUONG) or (pos == LEFT and lastPos ==LEFT_VUONG)) :
       print('LV')
       TurnLeftVuong()     
    elif ((pos == BLANK_SIGNAL and lastPos ==RIGHT_VUONG) or (pos == RIGHT and lastPos ==RIGHT_VUONG) ):
      print('RV')
      TurnRightVuong() 
      
      
    elif ((pos == MID and lastPos == LEFT_VUONG)) :
       print("NTL---------------------")
       NgaTuLeft();
    elif ((pos == MID and lastPos ==RIGHT_VUONG)) :
       print("NTR-------------------------")
       NgaTuRight();
    
     
    elif pos == BLANK_SIGNAL:
        GoStraight()
    
  
    
      
    preFilted = filted
    lastPos = pos
    
    pass

# Enter here exit cleanup code.D

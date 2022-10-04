from controller import Robot
from controller import Motor
from controller import DistanceSensor
from controller import Camera
from controller import LED
from controller import Supervisor
import math
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
NOP = -3
MID = 0
LEFT = 1
RIGHT = -1
FULL_SIGNAL  = 2
BLANK_SIGNAL = -2
LEFT_VUONG = 4
RIGHT_VUONG = -4
# MAX_SPEED <= 1000
MAX_SPEED = 20
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
    #print(gs[7].getValue(), sep = '\t')
    return filted

# Phần code điều khiển xe
#(str_filted[7] == '0') and (str_filted[0] == '1'))
#xác định độ lệch của xe từ việc đọc giá trị cảm biến
#filted == 0b11100001 or filted == 0b11100000 or filted == 0b11111100 or filted == 0b11111110 or filted == 0b11111000
#filted == 0b10000111 or filted == 0b00000111 or filted == 0b00000011 or filted == 0b00000001 or filted == 0b11000111
def DeterminePosition(filted):
    print(str_filted)
    if filted == 0b11100111 or filted == 0b11000011 or filted == 0b10000001:
        return MID
    elif (str_filted[0] == '0' and str_filted[5:8] == '111'):
        return LEFT_VUONG
    elif (str_filted[4:8] == '1111' and str_filted[:4] != '1111'):
        return LEFT
    elif ((str_filted[7] == '0') and (str_filted[:3] == '111')):
        return RIGHT_VUONG
    elif ((str_filted[:4] == '1111') and (str_filted[4:8] != '1111')):
        return RIGHT
    elif filted == 0b11111111:
        return FULL_SIGNAL
    elif filted == 0b00000000:
        return BLANK_SIGNAL
    return NOP
       
#các hàm điều khiển xe di chuyển
def GoStraight(filted):
    if filted == 0b11100111 or filted == 0b11000011 or filted == 0b10000001:
        return 1.0, 1.0
    return 1.0, 1.0
       
def TurnLeft(filted):
    #if pos == :
    #filted == 0b00000011 or filted == 0b00000001 or filted == 0b11000111
    
    if filted == 0b11101111:
        return 0.866, 1.0
    elif filted == 0b11001111:
        return 0.707, 1.0
    elif filted == 0b10011111:
        return 0.5, 1.0
    return 0.5, 1.0
        
def TurnRight(filted):
    #if pos == :
    if filted == 0b11110111:
        return 1.0, 0.866
    elif filted == 0b11110011:
        return 1.0, 0.707
    elif filted == 0b11111001:
        return 1.0, 0.5
    return 1.0, 0.5
def TurnRightVuong():
    for i in range(54):
        robot.step(timestep)
            #left_ratio = 10
            #right_ratio = 0
        #if str_filted[0] == '0':
         #   left_ratio = 0
          #  right_ratio = 10
    #elif lastPos == RIGHT_VUONG and pos == FULL_SIGNAL:
        lm.setVelocity(1 * MAX_SPEED)
        rm.setVelocity(0 * MAX_SPEED)
    
def TurnLeftVuong():
    for i in range(54):
        robot.step(timestep)
            #left_ratio = 0
            #right_ratio = 10
        #if str_filted[7] == '0':
         #   left_ratio = 10
          #  right_ratio = 0
    #elif lastPos == LEFT_VUONG and pos == FULL_SIGNAL:
        lm.setVelocity(0 * MAX_SPEED)
        rm.setVelocity(1 * MAX_SPEED)
       
lastPos = 0  
NgaTuLeft_Signal = False
NgaTuRight_Signal = False
VongXuyen_Signal = False
# Main loop:
# Chương trình sẽ được lặp lại vô tận 
while robot.step(timestep) != -1:
    filted = ReadSensors()
    #pos: position - vị trí của xe
    str_filted = (str(bin(filted))[2:]).zfill(8)
    pos = DeterminePosition(filted)
    # In ra màn hình giá trị của filted ở dạng nhị phân
    print('Position: ' + str(format(filted, '08b')), sep = '\t')
    #Gọi các hàm điều khiển
    if pos == MID:
        left_ratio, right_ratio = GoStraight(filted)
    elif filted == 0b00111100 or filted == 0b00011000 and VongXuyen_Signal:
        TurnRightVuong()
    elif pos == NOP and VongXuyen_Signal:
        for i in range(55):
            robot.step(timestep)
            #left_ratio = 0
            #right_ratio = 10
        #if str_filted[7] == '0':
         #   left_ratio = 10
          #  right_ratio = 0
    #elif lastPos == LEFT_VUONG and pos == FULL_SIGNAL:
            lm.setVelocity(0 * MAX_SPEED)
            rm.setVelocity(1 * MAX_SPEED)
        VongXuyen_Signal = False 
    elif preFilted == 0b00000000 and filted != 0b00000000:
        if NgaTuRight_Signal:
            TurnRightVuong()
            NgaTuRight_Signal = False 
        elif NgaTuLeft_Signal:
            TurnLeftVuong()
            NgaTuLeft_Signal = False 
        else:
            VongXuyen_Signal = True
            for i in range(5):
                robot.step(timestep)
                lm.setVelocity(1 * MAX_SPEED)
                rm.setVelocity(1 * MAX_SPEED)  
    elif lastPos == LEFT_VUONG and filted == 0b11111111:
        TurnLeftVuong()
    elif lastPos == RIGHT_VUONG and filted == 0b11111111:
        TurnRightVuong() 
    elif pos == RIGHT:
        left_ratio, right_ratio = TurnRight(filted)
    elif pos == LEFT:
        left_ratio, right_ratio = TurnLeft(filted)        
    else:  
        left_ratio, right_ratio = 1.0 , 1.0  
    if lastPos == LEFT_VUONG and pos != FULL_SIGNAL and pos != LEFT_VUONG:
        NgaTuLeft_Signal = True
    elif lastPos == RIGHT_VUONG and pos != FULL_SIGNAL and pos != RIGHT_VUONG:
        NgaTuRight_Signal = True
    lm.setVelocity(left_ratio * MAX_SPEED)
    rm.setVelocity(right_ratio * MAX_SPEED)
    print('right', NgaTuRight_Signal)
    print('left', NgaTuLeft_Signal)
    print('Vong xuyen: ', VongXuyen_Signal)
    preFilted = filted
    lastPos = pos
    pass

# Enter here exit cleanup code.D


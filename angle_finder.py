
import time                             #enables sleep
import board                            #imports i2c code
import adafruit_icm20x                  #imports imu code
import math

i2c = board.I2C()                       #create i2c object
imu = adafruit_icm20x.ICM20948(i2c)     #create imu object

cal_values = open("imu_cal.txt","r")    #open file with calibrated values
#following pulls in front/back and side/side calibrated values and converts str to float
#assumes front/back is first, and side/side is second
#assumes lines are separated by \r
angle_frontBack_cal = float(cal_values.readline())
angle_sideSide_cal = float(cal_values.readline())

while True:                             #while true
        accel_data = imu.acceleration   #get data from accelerometer

        #Code below takes accelerometer data in m/s^2 and translates to an angle
        #calculates as mounted in custom enclosure
        #frontBack is y/z
        #sideSide is y/x

        angle_frontBack = ((180/math.pi)*(math.atan2(accel_data[1],accel_data[2])))+90
        angle_sideSide = ((180/math.pi)*(math.atan2(accel_data[1],accel_data[0])))+90

        #below code finds angle until rv is level
        #for frontBack, negative means rear end is lower than front end
        #positive means front end is lower than rear end
        #for sideSide, negative means right side from front is lower than left side
        #positive means left side from front is lower than right side

        angle_frontBack_toLevel = angle_frontBack_cal - angle_frontBack
        angle_sideSide_toLevel = angle_sideSide_cal - angle_sideSide

        #below code gives calculated angle, only relevant for testing
        print("front to back angle is ", angle_frontBack)
        print("side to side angle is ", angle_sideSide)
        print("front to back angle to level is ",angle_frontBack_toLevel)
        print("side to side angle to level is ",angle_sideSide_toLevel)
        time.sleep(1)                   #sleep for a second while testing to avoid overrunning the buffer

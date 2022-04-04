import time                                     #not really necessary, but is here for testing purposes
import board                                    #contains info for IMU object
import adafruit_icm20x                          #has resources for i2c IMU
import math                                     #used for atan2 and pi

i2c = board.I2C()                               #make i2c object
imu = adafruit_icm20x.ICM20948(i2c)             #make IMU object

angle_frontBack_data = []                       #create array for front/back dataset
angle_sideSide_data = []                        #create array for side/side dataset
angle_frontBack_sum = 0                         #create variable for front/back sum for average
angle_sideSide_sum = 0                          #create variable for side/side sum for average
angle_frontBack_cal = 0                         #create variable for calibrated front/back average
angle_sideSide_cal = 0                          #create variable for calibrated side/side average
cal_samples = 100                               #give number of calibration samples

for i in range(cal_samples):                    #populate arrays for sample storage
        angle_frontBack_data.append(i)
        angle_sideSide_data.append(i)

for i in range(cal_samples):                    #collect samples
        accel_data = imu.acceleration           #gets data from IMU, takes ~5ms per sample

        #uses atan2 to collect front/back and side/side angles
        #y direction points upward
        #z direction points forward
        #x direction points to side
        angle_frontBack_data[i] = ((180/math.pi)*(math.atan2(accel_data[1],accel_data[2])))+90
        angle_sideSide_data[i] = ((180/math.pi)*(math.atan2(accel_data[1],accel_data[0])))+90

for i in range(cal_samples):                    #sums samples in arrays
        angle_frontBack_sum += angle_frontBack_data[i]
        angle_sideSide_sum += angle_sideSide_data[i]

#finds average value of collected readings
#divides sum of samples by number of samples
angle_frontBack_cal = angle_frontBack_sum / cal_samples
angle_sideSide_cal = angle_sideSide_sum / cal_samples

cal_values = open("imu_cal.txt", "w")           #open txt which holds calibrated values
cal_values.write(str(angle_frontBack_cal))      #write front/back average to file
cal_values.write("\r")                          #add newline, can use other delimiter depending on operation
cal_values.write(str(angle_sideSide_cal))       #write side/side average to file
cal_values.close()                              #close file when done, good practice

print("Calibration Successful")                 #indicate leveling is complete

import sys								#needed to do system level stuff
import glob								#needed to list available /dev/ttyA devices
import serial								#needed to communicate over serial
from time import sleep							#not needed outside testing
import matplotlib.pyplot as plotter

def adc_parse(data_in):						#function to parse serial ADC data
	data_in_str = str(data_in)					#convert input to string
	data_in_rm = data_in_str.split('\'')				#remove b' at beginning of string
	clean_data = data_in_rm[1].split('\\r')			#remove \\r\\n at end of string
	if clean_data[0].count('.') > 1:				#if it accidentally picks up two readings
		return
	elif clean_data[0].count('.') < 1:				#if it accidentally picks up no readings
		return
	adc_reading = clean_data[0].split('?')
	return adc_reading

def acquire_picos():							#function to connect to pico devices
	devices = glob.glob('/dev/tty[A]*')				#get available /dev/ttyA devices
	open_devices = []						#create return list
	print("Picos available: ", len(devices))			#print available /dev/ttyA devices
	if len(devices) == 0:						#exit if no picos are available
		print("No picos available. Now exiting")
		exit()
	for i in range(len(devices)):
		open_devices.append(i)					#add to list of available devices
		open_devices[i] = serial.Serial(devices[i],115200)	#open device for communication at baud rate of 115200
	print("Picos opened: ", len(open_devices))			#print picos connected in this step
	return open_devices						#return opened devices

									#program starts HERE
									#below are necessary global variables
open_devices = []							#list of opened serial pico connections
device_data = []							#list of device data collected from picos
collected_data = []
dcv_reading = []
dcv_datapoint = []
dci_reading = []
dci_datapoint = []

open_devices = acquire_picos()						#open all available /dev/ttyA devices
for i in range(len(open_devices)):					#create device data list
	device_data.append(i)

print("devices acquired")

#for data acquisition testing
for i in range(500):
	open_devices[0].flush()
	reading = adc_parse(open_devices[0].readline())
	if reading[0] == 'dcv ':
		dcv_reading.append(float(reading[1]))
		dcv_datapoint.append(len(dcv_reading))
		print(len(dcv_reading))
	elif reading[0] == 'dci ':
		dci_reading.append(float(reading[1]))
		dci_datapoint.append(len(dci_reading))
	else:
		continue
plotter.plot(dcv_datapoint,dcv_reading, label = 'dcv')
plotter.plot(dci_datapoint,dci_reading, label = 'dci')
plotter.legend()
plotter.show()

while True:
	for i in range(len(open_devices)):				#run through list of opened devices
		device_data[i] = adc_parse(open_devices[i].readline())	#read from serial port
		open_devices[i].flush()					#clear buffer once reading has been collected
		print(device_data[i][0],float(device_data[i][1]))
		sleep(0.1)						#sleep, time is quicker than pico sleep for testing purposes

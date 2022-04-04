#finalized pico code
#tags data before sending, reads from multiple channels
#Nickolas Moser
#Last Edited: March 30, 2022

#import necessary modules
from machine import Pin, ADC, UART
import utime

#set up ADC pins
def ADC_setup(adc_pins):
    adc_channel = []
    for i in range(len(adc_pins)):
        adc_channel.append(i)
        adc_channel[i] = machine.ADC(adc_pins[i])
    return adc_channel

#set up serial communications
def serial_setup(led):
    led.toggle()
    serial_object = machine.UART(0, 115200)
    utime.sleep(1)
    led.toggle()
    utime.sleep(1)
    return serial_object

def uart_handler(RPi_zero,led):
    led.toggle()
    while RPi_zero.any():
        print(RPi_zero.read(1))
    utime.sleep(1)
    led.toggle()

#get an adc reading
def get_reading(channel):
    window_size = 10
    samples = []
    samples_sum = 0
    for i in range(window_size):
        samples.append(channel.read_u16())
        samples_sum = samples_sum + samples[i]
    reading = samples_sum/10
    return reading

#program starts here

#global variables
adc_pins = [26,27]
adc_quantity = ['dcv','dci']

#device object setup functions
led = Pin(25, Pin.OUT)
led.toggle()
utime.sleep(1)
#RPi_zero = serial_setup(led)
adc = ADC_setup(adc_pins)
led.toggle()

#while device is turned on
while True:
    for i in range(len(adc)):
        print(adc_quantity[i],"?", get_reading(adc[i]))
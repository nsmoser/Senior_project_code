from machine import UART, Pin
import utime
import sys

#used to set up ESP device
#uses espWrite function to run through setup command list
def espSetup(espDevice,led):
    #esp station mode
    cwmode = '1'
    #wifi SSID and password
    wifiSSID = '"testSSID"'
    wifiPWD = '"testPWD"'
    #list of setup phrases to use
    setup_phrases = ['AT+GMR','AT+CWMODE='+cwmode,'AT+CWJAP='+wifiSSID+','+wifiPWD]
    #run through setup phrases
    for i in range(len(setup_phrases)):
        #write setup phrase and get write status
        espStatus = espWrite(espDevice,str(setup_phrases[i]))
        #if the write failed, return failure and give a response
        if(espStatus != 1):
            print("no ESP device found. Please connect one to UART")
            return 0
        #wait a quarter second between writes. ESP cant handle full speed
        utime.sleep(0.25)
    #set the LED high if setup and wifi connection is complete
    led.high()
    #return one if successful
    return 1

#code to simplify writing to ESP device
#takes uart object and write phrase as arguments
def espWrite(espDevice,phrase):
    #append newline to any written phrase
    endcode = '\r\n'
    #write the phrase and endcode
    espDevice.write(str(phrase)+endcode)
    #wait a quarter second. ESP cant handle full speed
    utime.sleep(0.25)
    #if there is some returned ESP info associated with the write
    while espDevice.any():
        #capture ESP response
        espResponse = str(espDevice.readline())
        #next two lines parse for printing to serial monitor
        espEndIndex = len(espResponse)
        print(espResponse[2:espEndIndex-5])
        #if the written phrase contains the wifi connection command
        if(phrase.find('CWJAP')):
            #if the response is that the IP is acquired
            if(espResponse.find('WIFI GOT IP') != -1):
                #return success
                return 1
            #if the response is any other connection phrase
            else:
                #wait this long, usually something appears in the buffer
                #which will reset the while loop
                utime.sleep(5)
    #if the write executed successfully
    if(espResponse.find('OK') != -1):
        #return success
        return 1
    #if the write did not execute successfully
    else:
        #return failure
        return 0

#PROGRAM STARTS HERE

#Create UART object for ESP device
espDevice = UART(0, baudrate=115200, tx=Pin(0), rx = Pin(1), timeout = 2)
#Create LED object to indicate connection to wifi
led = Pin(25, Pin.OUT)

#if startup command fails
if espSetup(espDevice,led) != 1:
    #indicate the startup failed, exit the program
    print("Ope. Setup failed")
    sys.exit()
    
#idling code for fun
while True:
    print(espWrite(espDevice,'AT'))
    utime.sleep(2)
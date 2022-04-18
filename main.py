#main.py
#sends ADC data over TCP connection to server
#Writen by: Nick Moser
#Last edited: April 18, 2022

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
    setup_phrases = ['AT+GMR','AT+CIPSTAMAC?','AT+CWMODE='+cwmode,'AT+CWJAP='+wifiSSID+','+wifiPWD]
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
    #if there is some returned ESP info associated with the write
    while espDevice.any() == 0:
        continue
    while espDevice.any():
        #capture ESP response
        espResponse = str(espDevice.readline())
        #next two lines parse for printing to serial monitor
        espEndIndex = len(espResponse)
        print(espResponse[2:espEndIndex-5])
        #if the written phrase contains the wifi connection command
        if(espResponse.find('CLOSED') != -1):
            while espDevice.any() == 0:
                continue
        if(phrase.find('CWJAP') != -1):
            #if the response is that the IP is acquired
            if(espResponse.find('OK') != -1):
                #return success
                utime.sleep(1)
            #if the response is any other connection phrase
            else:
                #wait until something appears in the buffer
                #which will reset the while loop
                while espDevice.any() == 0:
                    continue
        if phrase.find('CIPSTART') != -1:
            if espResponse.find('OK') != -1:
                break
            if espResponse.find('ERROR') != -1:
                break
            else:
                while espDevice.any() == 0:
                    continue
        if espResponse.find('OK') != -1:
            break
    if espResponse.find('OK') != -1:
        return 1
    else:
        return 0

#set up tcp connection
def espTCPSetup(espDevice):
    #specify protocol
    protocol = '"TCP"'
    #specify server to be connected to
    server = '"testServer.local"'
    #specify port to connect to at server
    port = '50010'
    #create conenction command
    connStart = 'AT+CIPSTART='+protocol+','+server+','+port
    #push connection command
    if espWrite(espDevice,connStart) == 0:
        return 0
    else:
        return 1
    
#write to a tcp connection
def espTCPWrite(espDevice,data,dataLen):
    endcode = '\r\n'
    #create write command
    dataSend = 'AT+CIPSEND='+str(dataLen)
    #push write command
    espDevice.write(dataSend+endcode)
    #wait for esp response
    while espDevice.any() == 0:
        continue
    #when esp responds
    while espDevice.any():
        #get & print response
        espResponse = str(espDevice.readline())
        espEndIndex = len(espResponse)
        print(espResponse[2:espEndIndex-5])
        #if there was an error in transmission, exit
        if espResponse.find('ERROR') != -1:
            print("cipsend failed")
            return 0
        #if esp is anticipating data to be sent
        if espResponse.find('>') != -1:
            #send data
            espDevice.write(str(data))
            #wait for response
            while espDevice.any() == 0:
                continue
        #if data has been transmitted, leave command
        if espResponse.find('SEND OK') != -1:
            break
        else:
            while espDevice.any() == 0:
                continue
    return 1
    

#PROGRAM STARTS HERE

machine.freq(250000000)
#Create UART object for ESP device
espDevice = UART(0, baudrate=115200, tx=Pin(0), rx = Pin(1), timeout = 2)
#setup information for ADC
adc_pins = [26, 27]
adc_tags = ['dcv','dci']
adc = []
#create ADC objects
for i in range(len(adc_pins)):
    adc.append(machine.ADC(adc_pins[i]))
#information for sending tcp data
sentBytes = 0
dataSend = ''

#Create LED object to indicate connection to wifi
led = Pin(25, Pin.OUT)

#if startup command fails
if espSetup(espDevice,led) != 1:
    #indicate the startup failed, exit the program
    print("Setup failed")
    sys.exit()

#if tcp connection fails
if espTCPSetup(espDevice) != 1:
    print("TCP connection failed")
    sys.exit()
    
machine.freq(16000000)

while True:
    #if nothing has been queried from tcp connection
    while espDevice.any() == 0:
        continue
    #if tcp connection requests something
    else:
        espResponse = str(espDevice.readline())
        #if tcp connection wants a measurement
        if espResponse.find('meas') != -1:
            utime.sleep(0.25)
            machine.freq(250000000)
            utime.sleep(0.25)
            #while buffer has less than 2kb of data
            while sentBytes < 2024:
                #collect ADC measurements from both channels
                #keep track of data in buffer
                for i in range(len(adc)):
                    adcReading = round((adc[i].read_u16() >> 4),4)
                    tagData = adc_tags[i]+'?'+str(adcReading)+';'
                    dataSend+=str(tagData)
                    sentBytes += len(tagData)
            #once buffer has filled, append end tag
            dataSend+=str('end')
            sentBytes += 3
            #write tcp data to server
            if espTCPWrite(espDevice,dataSend,sentBytes) != 1:
                print("write failed")
            #reset buffer and bytes in buffer
            dataSend = '' 
            sentBytes = 0
            machine.freq(16000000)
            utime.sleep(1)

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

def espTCPSetup(espDevice):
    protocol = '"TCP"'
    server = '"serverName.local"'
    port = '50010'
    connStart = 'AT+CIPSTART='+protocol+','+server+','+port
    if espWrite(espDevice,connStart) == 0:
        return 0
    else:
        return 1
    
def espTCPWrite(espDevice,data,dataLen):
    endcode = '\r\n'
    dataSend = 'AT+CIPSEND='+str(dataLen)
    espDevice.write(dataSend+endcode)
    while espDevice.any() == 0:
        continue
    while espDevice.any():
        espResponse = str(espDevice.readline())
        espEndIndex = len(espResponse)
        print(espResponse[2:espEndIndex-5])
        if espResponse.find('ERROR') != -1:
            print("cipsend failed")
            return 0
        if espResponse.find('>') != -1:
            espDevice.write(str(data))
            while espDevice.any() == 0:
                continue
        if espResponse.find('SEND OK') != -1:
            break
        else:
            while espDevice.any() == 0:
                continue
    return 1
    

#PROGRAM STARTS HERE

#Create UART object for ESP device
espDevice = UART(0, baudrate=115200, tx=Pin(0), rx = Pin(1), timeout = 2)
adc_pins = [26, 27]
adc_tags = ['dcv','dci']
adc = []
for i in range(len(adc_pins)):
    adc.append(machine.ADC(adc_pins[i]))

#Create LED object to indicate connection to wifi
led = Pin(25, Pin.OUT)

#if startup command fails
if espSetup(espDevice,led) != 1:
    #indicate the startup failed, exit the program
    print("Ope. Setup failed")
    sys.exit()

if espTCPSetup(espDevice) != 1:
    print("TCP connection failed")
    sys.exit()

sentBytes = 0
adcReading = []
dataSend = ''
#idling code for fun
while True:
    while sentBytes < 2024:
        for i in range(len(adc)):
            adcReading = round((3.3*((adc[i].read_u16() >> 4)/(2**12))),4)
            tagData = adc_tags[i]+'?'+str(adcReading)+';'
            dataSend+=str(tagData)
            sentBytes += len(tagData)
    dataSend+=str('end')
    sentBytes += 3
    if espTCPWrite(espDevice,dataSend,sentBytes) != 1:
        print("write failed")
    dataSend = ''
    sentBytes = 0

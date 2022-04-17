import socket                                           #needed for socket comm
import matplotlib.pyplot as plotter                     #plotting for testing data
from time import sleep                                  #sleep between intervals

def dataParser(recvData):                               #function to parse returned data
    dcv = []                                            #arrays for measurements
    dci = []
    splitData = recvData.split(';')                     #split at all semicolons
    for i in range(len(splitData)):                     #run thru new split-up array
        taggedData = splitData[i].split('?')            #split all indices at ?
        if taggedData[0].find('dcv') != -1:             #if tagged as dc voltage
            dcv.append(taggedData[1])                   #add data to dc voltage
        if taggedData[0].find('dci') != -1:             #if tagged as dc current
            dci.append(taggedData[1])                   #add data to dc durrent
        if taggedData[0].find('end') != -1:             #if end tag is found
            break                                       #exit loop
    return dcv, dci                                     #return dc voltage and current
    
#PROGRAM STARTS HERE
 
dcv_points = []                                         #create arrays for dc voltage & current
dci_points = [] 
HOST = ''                                               #gets default hostname in setup
PORT = 50010                                            #arbitrary port
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)#create socket object
sock.bind((HOST, PORT))                                 #bind socket object to port
print('socket bound')
sock.listen(1)                                          #listen for connections
print('listening')
clientSocket, address = sock.accept()                   #form connection when esp joins
print("Connection established")
while True:                                             #while active
    for i in range(30):                                 #sleep for 30 seconds
        sleep(1)    
        print('sleep time: '+str(i))
    data = 'meas'                                       #create measurement query string
    clientSocket.send(data.encode())                    #query measurement from pico
    recvData = clientSocket.recv(2048)                  #anticipate 2kb response
    dataLen = len(recvData)                             #find length of response
    parsedData = dataParser(recvData.decode('utf-8'))   #decode and parse data
    for i in range(len(parsedData[0])):                 #break parsed data into new arrays
        dcv_points.append(i)
        print(parsedData[0][i])
    for i in range(len(parsedData[1])):
        dci_points.append(i)
        print(parsedData[1][i])
    #plotter.plot(dcv_points,parsedData[0], label = 'dcv')
    #plotter.plot(dci_points,parsedData[1], label = 'dci')
    #plotter.legend()
    #plotter.show()
    dcv_points = []                                     #reset arrays after reading data
    dci_points = []
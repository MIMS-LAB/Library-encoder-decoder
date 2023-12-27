import sys
# this is where python stores modules, yours could be different
sys.path.append(r"D:\Alessandro\python39\Lib\site-packages")
sys.path.insert(1, r"D:\Alessandro\FILESFORSCHOOL\RRC-Avionics-master\Library-RRC-encoder\src")

#import tty,termios

import time as t
import rrc_decoder as d
import serial
import keyboard 

port = "COM5"
txport = "COM3"

baud  = 115200 
####    initilization    ####
i =0 
count = 0
uno_flag = False
if (uno_flag):
    uno = serial.Serial("COM9",115200)      
flag=True
radio_connect = False
rx_command = False
while True:

    try:
        radio = d.radioConnection(port, baud)

        radio_connect = True
        break
    except Exception as e:
        print(e)
        radio_connect = False
        exit(-1)

print("Connected")

#filedescriptors = termios.tcgetattr(sys.stdin) # retrieves current terminal settings 
#tty.setcbreak(sys.stdin) # allows for single character commands in terminal ; RAW mode instead of COOKED  mode
#tty and termios make sure terminal reads the key inputs 
while (radio_connect == True):
    
    #byteInWait = radio._RadioSerialBuffer.inWaiting()
    
    data_str= radio.readString()#_RadioSerialBuffer.read(byteInWait).strip().decode("utf-8")    # write a string
    if (data_str==None):
        continue
    else:
       data_str= data_str.split('\n')
       print("data is %s " % data_str[0])
    #print("# bytes in wait: %d \n" % byteInWait)
    t.sleep(1)
    print('...\n')
    if (data_str[0] == 'idle'):
        start=t.time()
        while True:
            end=t.time()
            timer=end-start
            if keyboard.is_pressed('space'):
                rx_command = True
                print("sending launch command \n") 
                t.sleep(1)
                flag=False
                break
            elif (timer>2):
                rx_command= False
                break
    if flag==False:
        break
    
    else:
        #t.sleep(0.5)
        print("data command is: %s\n"% data_str[0]) 
        t.sleep(1)
        if keyboard.is_pressed('D'):
            t.sleep(1)
            print("exitting connect loop \n")
            break
     #   break
    
    #else:
     #   print("packet error\n")


rx_command=True
print("launch successfull\n")
#termios.tcsetattr(sys.stdin, termios.TCSADRAIN, filedescriptors)
while(rx_command == True):
    packets = radio.getPackets()
    
    if packets == None:
        #radio.sendCommand("launch\n")
        t.sleep(2)
        print("an error happend")
        continue
  
    result = d.decodePackets(packets)
    print(result)
    if (uno_flag):

        if result["header"]==0:
            uno.open()
            data_long=result["data"]
            #gps_long=(str(data_long)+'\n').encode('utf-8')
            send="100\n"
            uno.write(bytes(send,'utf-8'))
            uno.readline()
            uno.close()

        if result["header"]==1:
            uno.open()
            gps_lat=result["data"]
            send2="115\n"
            uno.write(bytes(send2,'utf-8'))
            uno.close()

    if result["corrupted"]:
        print("CORRUPT: " + str(i))
        i=i+1

        continue

    result.pop("checksum")
    
    t.sleep(0.28)
    
print("ERROR!")
radio.close()
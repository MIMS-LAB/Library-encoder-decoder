import sys
# this is where python stores modules, yours could be different
sys.path.append(r"C:\Users\soham\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\LocalCache\local-packages\Python311\site-packages")
sys.path.insert(1, r"C:\Users\soham\Documents\GitHub\Library-RRC-encoder\src")
#import tty,termios

import time as t
import rrc_decoder as d
import serial
import keyboard 

port = "COM6"
baud  = 38400 
####    initilization    ####
i =0 
count = 0
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
    if data_str==None:
        continue
    else:
       data_str= data_str.split('\n')
       print("data is %s \n" % data_str[0])
    #print("# bytes in wait: %d \n" % byteInWait)
    t.sleep(1)
    if (data_str[0] == 'idle'):
        radio.sendCommand("launch\n")
        t.sleep(1)
        if keyboard.is_pressed('space'):
            rx_command = True
            print("sending launch command \n") 
            radio.sendCommand("launch\n")
            t.sleep(1.5)
            break 
        else:
            rx_command= False
    t.sleep(0.5)
     #   break
    
    #else:
     #   print("packet error\n")
    
    print("data command is: %s\n"% data_str[0]) 

    t.sleep(1)

print("launch successfull\n")
#termios.tcsetattr(sys.stdin, termios.TCSADRAIN, filedescriptors)

while(rx_command == True):
    packets = radio.getPackets()
    
    if packets == None:
        t.sleep(2)
        print("an error happend")
        continue
  
    result = d.decodePackets(packets)
    print(result)
    if result["corrupted"]:
        print("CORRUPT: " + str(i))
        continue

    result.pop("checksum")
    
    i=i+1
    t.sleep(1)
    
print("ERROR!")
radio.close()

import sys
# this is where python stores modules, yours could be different
<<<<<<< Updated upstream
sys.path.append(r"C:\Users\soham\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\LocalCache\local-packages\Python311\site-packages")
sys.path.insert(1, r"C:\Users\soham\Documents\GitHub\Library-RRC-encoder\src")
=======
<<<<<<< Updated upstream
sys.path.append(r"D:\Alessandro\python39\Lib\site-packages")
sys.path.insert(1, r"D:\Alessandro\FILESFORSCHOOL\RRC-Avionics-master\Library-RRC-encoder\src")
>>>>>>> Stashed changes

=======

sys.path.append(r"D:/Alessandro/python39/Lib/site-packages")
sys.path.insert(1, "D:/Alessandro/FILESFORSCHOOL/RRC-Avionics-master/Library-RRC-encoder/src")
#sys.path.append(r"C:\Users\soham\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\LocalCache\local-packages\Python311\site-packages")
#sys.path.insert(1, r"C:\Users\soham\Documents\GitHub\Library-RRC-encoder\src")
>>>>>>> Stashed changes
#import tty,termios

import time as t
import rrc_decoder as d
import serial
import keyboard 

<<<<<<< Updated upstream
port = "COM4"
=======
<<<<<<< Updated upstream
f = open("abcd.txt", "w")
port = "COM7"
txport = "COM3"

=======
#port = "COM11"#"COM6"
port = "COM8"
>>>>>>> Stashed changes
>>>>>>> Stashed changes
baud  = 115200 
####    initilization    ####
i =0 
count = 0
#uno = serial.Serial(port,115200)
flag=True
radio_connect = False
radio_connect2 = False

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
'''
while True:

    try:
        radio2 = d.radioConnection(port2, baud)
        radio_connect2 = True
        break
    except Exception as e:
        print(e)
        radio_connect2 = False
        exit(-1)

print("Connected2")
'''
#filedescriptors = termios.tcgetattr(sys.stdin) # retrieves current terminal settings 
#tty.setcbreak(sys.stdin) # allows for single character commands in terminal ; RAW mode instead of COOKED  mode
#tty and termios make sure terminal reads the key inputs 
<<<<<<< Updated upstream

'''
#key press code for breaking idle state 
=======
<<<<<<< Updated upstream

=======
'''
>>>>>>> Stashed changes
>>>>>>> Stashed changes
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
<<<<<<< Updated upstream
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
=======
        radio.sendCommand("launch\n")
        print("launch command sent\n")
>>>>>>> Stashed changes
        t.sleep(1)
        if keyboard.is_pressed('D'):
            t.sleep(1)
            print("exitting connect loop \n")
            break
     #   break
    
    #else:
<<<<<<< Updated upstream
    #print("packet error\n")
'''
=======
     #   print("packet error\n")

<<<<<<< Updated upstream
>>>>>>> Stashed changes

rx_command=True
print("launch successfull\n")

#termios.tcsetattr(sys.stdin, termios.TCSADRAIN, filedescriptors)
while(rx_command == True):
    data_str2= radio.readString()#_RadioSerialBuffer.read(byteInWait).strip().decode("utf-8")    # write a string
    if (data_str==None):
        continue
    else:
        f.write(data_str2)
        f.flush()
        print(data_str2)
    '''
=======
    t.sleep(1)
'''
print("launch successfull\n")
#termios.tcsetattr(sys.stdin, termios.CSADRAIN, filedescriptors)
rx_command = True
while(rx_command == True):
    '''
    radio2.sendCommand("sending\n")
    
    data_str= radio.readString()
    t.sleep(2)
    print(str("received:")+ str(data_str))
    '''

>>>>>>> Stashed changes
    packets = radio.getPackets()
    if packets ==None:
        print("packets is none \n")
        continue
    result = d.decodePackets(packets)
    '''
    if packets == None:
    gps_long=(str(random.uniform(78.10000,78.12000))+'\t').encode('utf-8')#random data
        uno.write(gps_long)
        print(gps_long)
        gps_lat=(str(random.uniform(41.10000,41.12000))+'\t').encode('utf-8')#random data
        uno.write(gps_lat)
        print(gps_lat) 
        
       t.sleep(2)
       print("an error happend")
       continue
  

    
    if result["header"]==1:
        data_lat=result["data"]
        #gps_lat=(str(data_long)+'\n').encode('utf-8')
        gps_lat=(str(random.uniform(-41.10000,-41.12000))+'\n').encode('utf-8')#random data
        uno.write(gps_lat)

    if result["header"]==0:
        data_long=result["data"]
        #gps_long=(str(data_long*10000)+'\n').encode('utf-8')
        gps_long=(str(random.uniform(79.10000,79.12000))+'\n').encode('utf-8')#random data
        uno.write(gps_long)
    

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
'''
    print(result)
    if result["corrupted"]:
        print("CORRUPT: " + str(i))
        i=i+1

        continue

    result.pop("checksum")
<<<<<<< Updated upstream
    '''
    t.sleep(0.28)
    
print("ERROR!")
radio.close()
f.close()
=======
    
    i=i+1
    t.sleep(2)

    
print("ERROR!")
radio.close()
#radio2.close()
>>>>>>> Stashed changes

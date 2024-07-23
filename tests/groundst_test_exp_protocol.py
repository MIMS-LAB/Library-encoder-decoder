import sys
sys.path.append(r"D:\Alessandro\python39\Lib\site-packages")
sys.path.append(r"D:\Alessandro\FILESFORSCHOOL\RRC-Avionics-master\Library-RRC-encoder\src")
import serial 
import rrc_decoder_experimental as d
import time as t
import keyboard

#flag=True
radio_connect = False
rx_command = False

rxport= "COM7"
baud  = 57600

while True:
    try:
        rx_ser =  d.radioConnection(rxport, baud)

        radio_connect = True
        break
    except Exception as e:
        print(e)
        radio_connect = False
        exit(-1)

print("Connected")

while radio_connect==True:
    
    data= rx_ser.readString()
    if data == None:
        t.sleep(1)

        print("none type error")
        continue
    else:
        data_str= data.split('\n')
        print("data is %s " % data_str[0])
    if (data_str[0] == 'idle'):
        start=t.time()
        while rx_command==False:
            end=t.time()
            timer=end-start
            if keyboard.is_pressed('space'):
                rx_command = True
                rx_ser.sendCommand("launch\n")
                print("sending launch command \n") 

                t.sleep(1)
                #flag=False
                break
            
            elif (timer>2):
                rx_command= False
                break
    else:

        result = d.decodePacketsExperimental()
        print(result)

          

               
    print(data_str)

    t.sleep(1)


    
rx_ser._RadioSerialBuffer.close()



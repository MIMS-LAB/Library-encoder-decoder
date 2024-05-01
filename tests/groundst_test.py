import sys
sys.path.append(r"D:\Alessandro\python39\Lib\site-packages")
sys.path.append(r"D:\Alessandro\FILESFORSCHOOL\RRC-Avionics-master\Library-RRC-encoder\src")
import serial 
import rrc_decoder as d
import time as t

rxport= "COM7"
baud  = 115200
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

while True:
    
    data= rx_ser.readByte()
    if data == None:
        print("none type error")
        continue
    else:
        print(data)
    t.sleep(500)
    rx_ser._RadioSerialBuffer.close()



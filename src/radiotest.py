import sys
sys.path.append(r"D:\Alessandro\python39\Lib\site-packages")

import serial 
import rrc_decoder as d
import time as t

txport = "COM8"
rxport= "COM5"
baud  = 115200
while True:

    try:
        rx_ser =  d.radioConnection(rxport, baud)
        #tx_ser =  d.radioConnection(txport, baud)

        radio_connect = True
        break
    except Exception as e:
        print(e)
        radio_connect = False
        exit(-1)

print("Connected")
'''
while True:

    if (radio_connect==True):
        tx_ser.sendCommand("command")  
        tx_ser.sendCommand("command")
        tx_ser.sendCommand("command")
        tx_ser.sendCommand("command")
        tx_ser.sendCommand("command")
        tx_ser.sendCommand("command")

        break
    t.sleep(1)

print("out of command loop\n")
'''
while True:
    
    data= rx_ser.readString()
    print(data)
    t.sleep(1)
    
tx_ser._RadioSerialBuffer.close()
rx_ser._RadioSerialBuffer.close()

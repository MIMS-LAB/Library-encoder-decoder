####    imports    ####

import os, sys, random
import time as t
sys.path.insert(1, "C:/Users/ahmad/OneDrive/Documents/GitHub/RRC/Library-RRC-encoder/src")
import rrc_decoder as d


####    test setup    ####

TX_PORT = "COM10"           # encoder transmitting port
RX_PORT = "COM11"           # decoder recieving port
BAUD    = "57600"           # baudrate
TEST    = d.RRC_HEAD_GPS_LONG   # data header to test


####    encoder setup    ####

PATH    = "C:/Users/ahmad/OneDrive/Documents/GitHub/RRC/Library-RRC-encoder/tests"
command = PATH+"/test"  
test    = lambda header, data, time : os.system(f"{command} {TX_PORT} {header} {data} {time}")  # encoder call lambda

os.system(f"gcc {PATH}/test.c -o {command} -std=c99")  # compile encoder using gcc


####    initilization    ####

while True:
    port = RX_PORT
    baud = BAUD

    try:
        radio = d.radioConnection(port, baud)
        break
    except Exception as e:
        print(e)
        exit(-1)

print("Connected")


####    set ranges    ####

if TEST in [d.RRC_HEAD_GPS_LAT, d.RRC_HEAD_GPS_LONG]:
    lowerRange = -1_800_000
    upperRange = 1_800_000
    multiplier = 10_000
else:
    lowerRange = -4_000
    upperRange = 4_000
    multiplier = 100


####    test for 1000 random values    ####

for i in range(1000):
    data = random.randint(lowerRange, upperRange) / multiplier
    time = random.randint(0, 0xfffff)

    test(TEST, data, time)

    packets = radio.getPackets()

    if packets == None:
        print("an error happend")
        continue

    result = d.decodePackets(packets)

    if result["corrupted"]:
        print("CORRUPT: " + str(i))
        continue

    result.pop("checksum")

    if { "header" : TEST, "data" : data, "time" : time, "corrupted" : False } == result:
        print("OK: " + str(i))
    else:
        print("ERROR: " + str(i))
    
    # print(packets)
    # print(result)
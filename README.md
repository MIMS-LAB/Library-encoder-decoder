#   Library-RRC-encoder

This is the RRC encoder and decoder protocol for data broadcasting.
Each package includes the following information:

1.  Data: the actual information to be sent.
2.  Headers: to identify the type of data.
3.  Checksum: a simple check of corruption.
4.  Timestamp: to indicate the time of data collection.


##  Data

The data is all collected as double precision floats which are 64-bit wide.
Though, the protocol aims on reduceing the package size, that's why data is
converted into signed integers with only the required decimal points needed,
this saves space and time with no real compromises. 


### GPS

The GPS data consists of longitude and latitude in the following ranges:

|  Data  |  Minimum  |  Maximum  |  Integer Magnitude  |  Signed bit-width  |
|--------|:---------:|:---------:|:-------------------:|:------------------:|
|  LONG  | -180.0000 | 180.0000  |      1,800,000      |       22 bit       |
|  LAT   |  -90.0000 |  90.0000  |        900,000      |       21 bit       |


### Accelerometer

The accelerometer collects measurements on 3 axis in G's.

|  Data  |  Minimum  |  Maximum  |  Integer Magnitude  |  Signed bit-width  |
|--------|:---------:|:---------:|:-------------------:|:------------------:|
|   X    |  -40.00   |   40.00   |        4,000        |       13 bit       |
|   Y    |  -40.00   |   40.00   |        4,000        |       13 bit       |
|   Z    |  -40.00   |   40.00   |        4,000        |       13 bit       |


### Barometer

The barometer collects data for pressure in mbar and temperature in celcius.

|  Data  |  Minimum  |  Maximum  |  Integer Magnitude  |  Signed bit-width  |
|--------|:---------:|:---------:|:-------------------:|:------------------:|
|  PRES  |   10.00   | 1200.00   |      120,000        |       18 bit       |
|  TEMP  |  -40.00   |   85.00   |        8,500        |       15 bit       |


##  Headers

8 headers are needed.

|       Description      |    Header name    |  Hex |  Bin  |
|:----------------------:|:------------------|:----:|:-----:|
|  GPS Longitude         | RRC_HEAD_GPS_LONG | 0x00 | 0b000 |
|  GPS Latitude          | RRC_HEAD_GPS_LAT  | 0x01 | 0b001 |
|  Accelerometer X-axis  | RRC_HEAD_ACC_X    | 0x02 | 0b010 |
|  Accelerometer Y-axis  | RRC_HEAD_ACC_Y    | 0x03 | 0b011 |
|  Accelerometer Z-axis  | RRC_HEAD_ACC_Z    | 0x04 | 0b100 |
|  Barometer Pressure    | RRC_HEAD_PRES     | 0x05 | 0b101 |
|  Barometer Temperature | RRC_HEAD_TEMP     | 0x06 | 0b110 |
|  Package Terminating   | RRC_HEAD_T_END    | 0x07 | 0b111 |


##  Checksum

4 bits used for checksum
dbcf

d = LSB of highest byte
b = MSB of middle byte
c = MSB of lowest byte
f = LSB of lowest byte


##  Timestamp

range   0, 4095

12 bits needed
covers 68 minutes for 1 second representation
covers 34 minutss for 500 milliseconds representation
requires launch signal for higher accuracy


##  Overall

h = header
c = checksum
d = data
t = time

form 1

byte 1: hhhc cccd
byte 2: hhhd dddd
byte 3: hhhd dddd
byte 4: hhhd dddd
byte 5: hhhd dddd
byte 6: hhhd ddtt
byte 7: hhht tttt
byte 8: 111t tttt

last header is set to 111 to indicate end of packet
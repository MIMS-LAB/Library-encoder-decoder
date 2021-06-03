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

4 bits used for checksum DBCF

D = LSB of highest byte\
B = MSB of middle byte\
C = MSB of lowest byte\
F = LSB of lowest byte


##  Timestamp

The system is expected to be running for 2 hours at a 5Hz 
sampling and trasmission rate. With the timestamp as an integer
this gives a maximum stamp of 36000 readings which is 16-bit wide. 
A 16-bit timestamp will give even more space up to 65535 readings.


##  Overall

|  Byte  |   Content   |
|:------:|:-----------:|
| byte 1 | `HHHC CCCD` |
| byte 2 | `HHHD DDDD` |
| byte 3 | `HHHD DDDD` |
| byte 4 | `HHHD DDDD` |
| byte 5 | `HHHD DDDD` |
| byte 6 | `HHHD DDTT` |
| byte 7 | `HHHT TTTT` |
| byte 8 | `111T TTTT` |

H = Header, C = Checksum, D = Data, T = Timestamp
#   Library-RRC-encoder

This is the RRC encoder and decoder protocol for data broadcasting.
Each package includes the following information:

1.  Data: the actual information to be sent.
2.  Headers: to identify the type of data.
3.  Checksum: a simple check of corruption.
4.  Timestamp: to indicate the time of data collection.

The decoder has one dependency which is 
[pyserial](https://pypi.org/project/pyserial/).
You can install with `pip install pyserial`


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


##  Scaling Magnitudes

Each data type will be scaled with a constant magnitude to convert into an integer.

|  Data  |  Magnitude |
|--------|:----------:|
|  LONG  |  10,000    |
|  LAT   |  10,000    |
|   X    |     100    |
|   Y    |     100    |
|   Z    |     100    |
|  PRES  |     100    |
|  TEMP  |     100    |


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

Each piece of data will consist of 24 bits, 4 bits of which will be copied for checksum

```xxxx xxxD   Bxxx xxxG   Cxxx xxxF```

D = LSB of highest byte\
B = MSB of middle byte\
G = LSB of middle byte\
C = MSB of lowest byte\
F = LSB of lowest byte


##  Timestamp

The system is expected to be running for 2 hours at a 5Hz 
sampling and trasmission rate (STR). With the timestamp as an integer
this gives a maximum stamp of 36000 readings which is 16-bit wide. 

##  Overall

The overall protocol will be as the following:

*   The largest piece of data is 22-bit wide => 24 bits will be used to pad to a whole byte.
*   Headers will use 3 bits of each packet, with a terminating header for the last one in a package.
*   Checksum will use 5 bits and will be inserted in the first packet.
*   Timestamp will use 20 bits giving more time of operation and/or higher STR.

|  Byte  |   Content   |
|:------:|:-----------:|
| byte 0 | `HHHC CCCC` |
| byte 1 | `HHHD DDDD` |
| byte 2 | `HHHD DDDD` |
| byte 3 | `HHHD DDDD` |
| byte 4 | `HHHD DDDD` |
| byte 5 | `HHH0 DDDD` |
| byte 6 | `HHHT TTTT` |
| byte 7 | `HHHT TTTT` |
| byte 8 | `HHHT TTTT` |
| byte 9 | `111T TTTT` |

H = Header, C = Checksum, D = Data, T = Timestamp
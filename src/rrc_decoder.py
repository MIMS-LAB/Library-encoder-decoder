import serial

####    global constants    ####
## version
RRC_ENCODER_VERSION = 3

## headers
RRC_HEAD_GPS_LONG = 0x00            #  gps longitude   (000)
RRC_HEAD_GPS_LAT  = 0x01            #  gps latitude    (001)
RRC_HEAD_ACC_X    = 0x02            #  accelerometer x (010)
RRC_HEAD_ACC_Y    = 0x03            #  accelerometer y (011)
RRC_HEAD_ACC_Z    = 0x04            #  accelerometer z (100)
RRC_HEAD_PRESS    = 0x05            #  baromete        (101)
RRC_HEAD_TEMP     = 0x06            #  temperature     (110)
RRC_HEAD_END      = 0x07            #  end             (111)

## Bit Shift
RRC_SHIFT_CHECKS  = 0               #  checksum shift  (000x xxxx) >> 0  => (000x xxxx)
RRC_SHIFT_HEADER  = 5               #  header shift    (xxx0 0000) >> 5  => (1110 0xxx)

## Bit Masks
RRC_MASK_CHECKS   = 0x1f            #  0001 1111
RRC_MASK_DATA     = 0x1f            #  0001 1111
RRC_MASK_TIME     = 0x1f            #  0001 1111
RRC_MASK_HEADER   = 0xe0            #  1110 0000

## package size
RRC_DATAPACK_SIZE = 10              #  each package is 10 bytes


####    radioConnection class    ####
class radioConnection:
    '''
    A class to represent a radio connection.

    ...

    Attributes
    ----------
    _inSerialBuffer : Serial
        the serial connection to use

    Methods
    -------
    __init__(port, baudrate):
        initilze a connection with the specified port and baudrate
    _readByte():
        Read a byte from serial port if there are available bytes
    getPackets(retries):
        Get a valid package of data
    '''


    _RadioSerialBuffer   = None

    def __init__(self, port, baudrate):
        '''
        __init__(self, port, baudrate) --> None
        
        Create decoder object and set port for input buffer.

        params:
        port -- Port number, either "COM*" for windows or "tty*" for nix systems.
        baudrate -- Baud rate for connection.
        '''
        self._RadioSerialBuffer = serial.Serial(port, baudrate) 

    def _readByte(self):
        '''
        readByte(self)

        Read a byte from serial port if there are available bytes

        Params:
        None

        Return:
        int - if byte was read
        None - of not byte are available
        '''
        
        if self._RadioSerialBuffer.inWaiting() == 0:
            return None

        return int.from_bytes(self._RadioSerialBuffer.read(), byteorder="big", signed=False)

    def sendCommand(self, command: str):
        '''
        sendCommand(self, command: str):

        Send a string command to the RFD on the rocket with a terminating newline feed

        Params:
        command: str -- a string to be sent to the rocket

        Return:
        None
        '''

        command += '\n'
        command  = bytes(command, 'utf-8')
        self._RadioSerialBuffer.write(command)

    def getPackets(self, retries=-1):
        '''
        getPackets(self, retries) --> list
        
        Get a valid package of data.

        Params:
        retries -- 

        Return:
        An 8 byte list of the same header type.
        '''
        goodToGo   = True
        readHeader = lambda x : (x & RRC_MASK_HEADER) >> RRC_SHIFT_HEADER  #  extract header from a packet (0xe0 = 1110 0000)

        while retries > 0 or retries < 0:
            retries -= 1

            if goodToGo:               #  read first byte from buffer and store it
                byte = self._readByte()
                if byte == None:
                    return None

                packet = [byte]
            
            header   = readHeader(packet[0])              #  store the header on its own
            goodToGo = True
            
            for i in range(RRC_DATAPACK_SIZE - 2):        #  read remaining bytes
                byte = self._readByte()                   #  read one byte from buffer
                if byte == None:
                    return None

                packet.append(byte) 

                if readHeader(packet[i+1]) != header:     #  if got a different header give signal to restart and break
                    goodToGo = False                      #  signal an issue
                    packet = [packet[-1]]                 #  set last byte as the first one to restart getting packets
                    break
            
            if not goodToGo:           #  restart if not good to go
                continue
            
            byte = self._readByte()     #  read the last byte
            if byte == None:
                return None

            packet.append(byte) 

            if readHeader(packet[-1]) != RRC_HEAD_END:  #  check last byte has ending header
                goodToGo = False                             #  if not, signal an issue
                packet = [packet[-1]]                        #  and restart

            if goodToGo:               #  return value if everything is fine
                return packet


def generateChecksum(data):
    '''
    generateChecksum(data) --> int

    Generate the checksum of a piece of data.

    Params:
    data -- A 3 byte integer.

    Return:
    An integer with the least 4 bits set to the checksusm
    '''

    result  = 0x01 &  (data & 0x01)             #  LSB of the lowest byte (0x01    = 0000 0000 0000 0000 0000 0001)
    result |= 0x02 & ((data & 0x80)    >> 6)    #  MSB of the lowest byte (0x80    = 0000 0000 0000 0000 1000 00x0)
    result |= 0x04 & ((data & 0x100)   >> 6)    #  LSB of the middle byte (0x100   = 0000 0000 0000 0001 0000 0x00)
    result |= 0x08 & ((data & 0x8000)  >> 12)   #  MSB of the middle byte (0x8000  = 0000 0000 1000 0000 0000 x000)
    result |= 0x10 & ((data & 0x10000) >> 12)   #  LSB of the higest byte (0x10000 = 0000 0001 0000 0000 000x 0000)

    return result


def fixData(data, header):
    '''
    fixData(data, header) --> int

    Fix data to proper sign and decimal points.

    Params:
    data -- Raw integer recieved.
    header -- the header, aka type of data received.

    Return:
    The data with the proper sign and decimal points
    '''

    if data & 0x800000:    #  if last bit is set then the number is negative
        data ^= 0x800000   #  remove the last bit to get the actual value
        data *= -1         #  multiply data by -1 to
    
    #  check README for scaling magnitudes selection
    if header in [RRC_HEAD_GPS_LAT, RRC_HEAD_GPS_LONG]:
        data /= 10000
    else:
        data /= 100

    return data
    

def decodePackets(packets):
    '''
    decodePackets(packets) --> dict
    
    Decode the packets to get data timestamp checksum and header.

    Params:
    packets -- The 8 byte list recieved using the getPackets function

    Return:
    A dictionary with the following variables.
    [0] -- int(header) -- The header in the packets.
    [1] -- int(checksum) -- The checksum sent in the packets for later verification.
    [2] -- float(data) -- Fixed data to proper decimal point and sign.
    [3] -- int(time) -- The time stamp of the data when sent.
    [4] -- bool(corrupted) -- True if the calculated checksum doesn't match the recieved checksum False otherwise.
    '''
    header   = (packets[0] & RRC_MASK_HEADER) >> RRC_SHIFT_HEADER  #  extract header from first byte   (0xe0 = 1110 0000)
    checksum = (packets[0] & RRC_MASK_CHECKS) >> RRC_SHIFT_CHECKS  #  extract checlsum from first byte (0x1e = 0001 1111)

    data  = (packets[1] & RRC_MASK_DATA) << 19      #  extract data (mask = 0x1f = 0001 1111) 1111 1000 0000 0000 0000 0000
    data |= (packets[2] & RRC_MASK_DATA) << 14      #  extract data (mask = 0x1f = 0001 1111) 0000 0111 1100 0000 0000 0000
    data |= (packets[3] & RRC_MASK_DATA) << 9       #  extract data (mask = 0x1f = 0001 1111) 0000 0000 0011 1110 0000 0000
    data |= (packets[4] & RRC_MASK_DATA) << 4       #  extract data (mask = 0x1f = 0001 1111) 0000 0000 0000 0001 1111 0000
    data |= (packets[5] & RRC_MASK_DATA)            #  extract data (mask = 0x1f = 0001 1111) 0000 0000 0000 0000 0000 1111

    time  = (packets[6] & RRC_MASK_TIME) << 15      #  extract time (mask = 0x1f = 0001 1111) 1111 1000 0000 0000 0000
    time |= (packets[7] & RRC_MASK_TIME) << 10      #  extract time (mask = 0x1f = 0001 1111) 0000 0111 1100 0000 0000
    time |= (packets[8] & RRC_MASK_TIME) << 5       #  extract time (mask = 0x1f = 0001 1111) 0000 0000 0011 1110 0000
    time |= (packets[9] & RRC_MASK_TIME)            #  extract time (mask = 0x1f = 0001 1111) 0000 0000 0000 0001 1111

    # print("{0:b}".format(header))
    # print("{0:b}".format(data))
    # print("{0:b}".format(time))
    # print("{0:b}".format(checksum))
    # print(generateChecksum(data))

    corrupted = checksum != generateChecksum(data)  #  check for data corruption by checking the checksum

    data = fixData(data, header)    #  fix data

    return { "header"    : header, 
             "checksum"  : checksum,
             "data"      : data,
             "time"      : time,
             "corrupted" : corrupted }
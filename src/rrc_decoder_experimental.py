import serial
####    global constants    ####
## version
RRC_ENCODER_VERSION = 4

## headers
RRC_HEAD_GPS_LONG = 0x00            #  gps longitude   (000)
RRC_HEAD_GPS_LAT  = 0x01            #  gps latitude    (001)
RRC_HEAD_ACC_X    = 0x02            #  accelerometer x (010)
RRC_HEAD_ACC_Y    = 0x03            #  accelerometer y (011)
RRC_HEAD_ACC_Z    = 0x04            #  accelerometer z (100)
RRC_HEAD_PRESS    = 0x05            #  baromete        (101)
RRC_HEAD_TEMP     = 0x06            #  temperature     (110)
#RRC_HEAD_BATT_V   = 0X07
RRC_HEAD_END      = 0x08            #  end             (111)

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
    readByte():
        Read a byte from serial port if there are available bytes

    For actual decoder:
    # please see hamming codes online for the algorithm behind this madness

    # Unstaggers data
    # The logic behind this is that Hamming squares only work for 1 bit flip. If we get two bit flips in one hamming square,
    # the data is lost. So instead of putting our hamming squares sequentially, like
    # 1111 1111 1111 1111 2222 2222 2222 2222 ...
    # where 1,2,3,4 are bits to different hamming blocks,
    # we "swizzle" them to
    # 1234 1234 1234 1234 1234 1234 1234 1234...
    # so if four bit flips happen one after the other, it still transmits fine!
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

    def readByte(self):
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
    
    def readString(self):
        '''
        readString(self)

        Read a byte from serial port if there are available bytes

        Params:
        None

        Return:
        int - if byte was read
        None - of not byte are available
        '''
        inWaitStr = self._RadioSerialBuffer.inWaiting()
        
        if inWaitStr == 0:
            return None

        return self._RadioSerialBuffer.read(inWaitStr).decode("utf-8")

    def sendCommand(self, command: str):
        '''
        sendCommand(self, command: str):

        Send a string command to the RFD on the rocket with a terminating newline feed

        Params:
        command: str -- a string to be sent to the rocket

        Return:
        1-success
        None-fail to write
        '''

        command += '\n'
        command  = bytes(command, 'utf-8')
        self._RadioSerialBuffer.write(command)
        
        outWait = self._RadioSerialBuffer.out_waiting

        if (outWait == 0):
            return 1
        else:
            return 0
        

    def deswizzle(data_in, data_out):
        length = len(data_out)
        write_pos = [15] * length

        for read_index in range(0, length):
            for read_pos in range(15, -1, -1):
                bit = (data_in[read_index] & (1 << read_pos)) >> read_pos
                write_index = (15 - read_pos) % length
                data_out[write_index] |= (bit << write_pos[write_index])
                write_pos[write_index] -= 1

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
        #elif header==RRC_HEAD_BATT_V:
        #    data /=1000
        else:
            data /= 100

        return data

    # hamming blocks are transmitted like so:
    # RRRD RDDD RDDD DDDD
    # R -> Redundancy (to verify correctness) D -> Data
    # We want to just get the data, like
    # 0000 0DDD DDDD DDDD
    # This turns the hamming block into just data
    def unhamm_square(data):
        out = 0
        out |= (data & 0x1000) >> 2  # 0x1000 = 0001 0000 0000 0000
        out |= (data & 0x0700) >> 1  # 0x0700 = 0000 0111 0000 0000
        out |= (data & 0x007F)       # 0x007F = 0000 0000 0111 1111
        return out

    # counts number of 1 bits in a uint16
    def bitcount(data):
        # almost certainly an easier way but this works for now
        count = 0
        for x in range(0, 16):
            if data % 2 == 1:
                count += 1
            data = data >> 1
        return count

    # Detects any one-bit errors and corrects it
    def self_correct(self,square):
        # todo: make 1st bit work
        pos = 0  # error of location
        if self.bitcount(square & 0x5555) % 2 == 1:
            pos += 1
        if self.bitcount(square & 0x3333) % 2 == 1:
            pos += 2
        if self.bitcount(square & 0x0F0F) % 2 == 1:
            pos += 4
        if self.bitcount(square & 0x00FF) % 2 == 1:
            pos += 8
        if pos != 0:
            invpos = 15 - pos
            val = (square >> invpos) & 1  # flip sign
            print("Self correcting square! val:", val, " pos: ", pos)
            if val == 1:
                # Flip bit to zero
                square = square & ~(1 << invpos)
            else:
                square |= 1 << invpos
        return square


    def decodePacketsExperimental(self,packets):
        swizzled_packets = []
        for i in range(0, 8, 2):
            # assemble square (2 bytes -> 1 short)
            square: int = 0
            square |= packets[i] << 8
            square |= packets[i+1]
            swizzled_packets.append(square)

        # deswizzle data
        deswizzled_packets = [0] * len(swizzled_packets)
        self.deswizzle(swizzled_packets, deswizzled_packets)

        decoded_packets = []

        for packet in deswizzled_packets:
            packet = self.self_correct(packet)
            packet = self.unhamm_square(packet)
            decoded_packets.append(packet)


        header = decoded_packets[0] >> 8
        time  = (decoded_packets[0] & 0x8) << 11
        time |= (decoded_packets[1])

        data  = (decoded_packets[2]) << 11
        data |= (decoded_packets[3])

        data = self.fixData(data, header)
        header_list = ["GPS_LONG", "GPS_LAT", "ACC_X", "ACC_Y", "ACC_Z", "PRESS", "TEMP", "END"]
        header_string = header_list[header]

        return { "header"    : header,
                "name"      : header_string,
                "data"      : data,
                "time"      : time}
import sys
# this is where python stores modules, yours could be different
sys.path.append(r"D:\Alessandro\FILESFORSCHOOL\RRC-Avionics-master\featherweightGUI\rocketry\Lib\site-packages")


import re
import time
import argparse
from serial.serialutil import SerialException
import serial
current_version = "v1.0.4"  # changelog in repo

'''     REFERENCES:

    1. ArgParser: https://docs.python.org/3/library/argparse.html#prog
    
    2. Sikset.py: https://community.emlid.com/t/sikset-py-a-python-script-to-easily-control-your-rfd900-3dr-radio-from-the-command-line/3654


'''
# ************* RANGES: ****************************
serial_speeds =  (2400, 4800, 9600, 19200, 38400, 57600, 115200) #(2, 4, 9, 19, 38, 57, 115) #{2400: 2, 4800: 4, 9600: 9, 19200: 19, 38400: 38, 57600: 57, 115200: 115} 
#serial_speeds_list = serial_speeds.items()
#print(serial_speeds_list)
air_speeds = (4, 8, 16, 24, 32, 64, 96, 128, 192, 250)

netids = range(0, 500,1) 

txpowers = range(1, 31,1) 

ECCrange = (0, 1) 

MAVLINKrange = (0, 1) 

OP_RESEND_RANGE = (0, 1)

MIN_FREQ = range(902000, 928000, 1000)  # in kHz

MAX_FREQ = range(903000, 929000, 1000)  # in kHz

numb_channels = range(1, 50,1)

DUTY_CYCLE_RANGE = range(10, 100,1)

LBT_RSSI_range = (0, 1)

MANCHESTER_range = (0, 1)

rtscts_RANGE = (0, 1)

nodeID_range = range(0, 30,1)

NODEDESTINATION_range = range(0, 30,1)

SYNCANY_range = (0, 1)

NODECOUNT_range = range(2, 31,1)


RANGES =  [serial_speeds, air_speeds, netids, txpowers, ECCrange, MAVLINKrange, OP_RESEND_RANGE, MIN_FREQ, MAX_FREQ, numb_channels,
               DUTY_CYCLE_RANGE, LBT_RSSI_range, MANCHESTER_range, rtscts_RANGE, nodeID_range, NODEDESTINATION_range, SYNCANY_range, NODECOUNT_range]

#print(RANGES[0])

# ************* DEFAULT VALUES***********************************

DEFAULTS =  [serial_speeds[5],air_speeds[7], netids[1], txpowers[20], ECCrange[0], MAVLINKrange[0], OP_RESEND_RANGE[0], MIN_FREQ[0], MAX_FREQ[5], numb_channels[0], DUTY_CYCLE_RANGE[30], LBT_RSSI_range[0], MANCHESTER_range[0], rtscts_RANGE[0], nodeID_range[0], NODEDESTINATION_range[0], SYNCANY_range[0], NODECOUNT_range[0]]

default_serial_port = 'COM4'

DEFAULT_BAUDRATE = DEFAULTS[0]

flagStrings = ["-SS","-AS","-NETID","-PWR","-ECC","-MAV","-OP","-mf","-MF","-NC","-DC","-LBT","-MAN","-RTSCTS","-NODE_ID","-NODE_DEST","-SYN","-NODE_COUNT"]
destStrings = ["serial_speed","airSpeed","netid","TXpwr","ecc","mavlink","op_resend","min_freq","max_freq","NUM_CHANNELS","DUTY_CYCLE","LBT_RSSI","MANCHESTER_ENCODING","RTSCTS","NODE_ID","NODE_DEST","SYN","NODE_COUNT"]
helpStrings = [ " set SERIAL_SPEED: Serial speed in ‘one byte form’", "set AIR_SPEED:  ","set NET_ID: Network ID."," set TXPOWER: Transmit power in dBm."
,"set ECC: Enables or disables the golay error correcting code","  set MAVLINK:    Enables or disables the MAVLink framing and reporting","  set OPPRESEND:Opportunic Resend"," set MIN_FREQ:  Min freq in KHz"	,    " set MAX_FREQ:   Max freq in KHz", "  set NUM_CHANNELS: Number of frequency hopping channels"," set DUTY_CYCLE:    The percentage of time to allow transmit"," set LBT_RSSI:  Listen before talk threshold"," set MANCHESTER: Manchester encoding"," set RTSCTS: Ready To Send and Clear To Send","set NODEID: Node ID. Base node ID is 0. One node must be acting as a base for a multipoint environment to work. NODECOUNT must be updated first before updating this parameter with bigger number."," set NODEDESTINATION: Remote node ID to communicate with. Set the value to 65535 to broadcast to all nodes. Cannot be the same as NODEID. NODECOUNT must be updated first before updating this parameter with bigger number."," set SYNCANY: If set to 1, allows the modem to send data to all non-base nodes without finding the base. It is strongly recommended to set the value to 0 to avoid unwanted data communication confusion on a multipoint environment.","  set NODECOUNT: The total number of nodes."]
# ****************************************************************
'''
print(len(RANGES))
print(len(DEFAULTS))
print(len(flagStrings))
print(len(destStrings))
print(len(helpStrings))
'''
# set for local or remote radio
command_prefix = "AT" # "AT" for local radio, RT for remote radio
global ser
ser = serial.Serial()

# command line options
parser = argparse.ArgumentParser(description='version:' + str(current_version))

#add main radio arguments to parser 
for i in range(len(DEFAULTS)):
    default_value = DEFAULTS[i]
    range_value = RANGES[i]
    parser.add_argument(flagStrings[i],action="store",type=int,dest=destStrings[i],help=helpStrings[i] +"\tValid choices are: from {} to {}.\nDEFAULT is: {} \n" .format(min(range_value),max(range_value),DEFAULTS[i]),metavar='',default=DEFAULTS[i],choices=RANGES[i])



parser.add_argument('--version', action='version', version=current_version)

parser.add_argument("-p", action="store", type=str, dest="port",
                    help="Serial port. Default: %s" % default_serial_port, default=default_serial_port)

parser.add_argument("-v", action="store", type=bool,dest="verbose",
                    help="Enables extra information output (debugging).", default=True)

parser.add_argument("-tb", action="store",type=bool, dest="test_baud",
                    help="Test serial port for correct baud rate.", default=False) # set default to true if want to debug 


'''
parser.add_argument("-param", action="store",type=bool,
                    dest="show_parameters", help="Shows all user settable EEPROM parameters.",default=False)
'''

parser.add_argument("-b",  action="store", type=int, dest="baud", help="Choose our serial connection speed to the radio in baud If no baud specified, it will test. (factory default: {})".format(DEFAULT_BAUDRATE), default=DEFAULT_BAUDRATE)

options = parser.parse_args()

if options.verbose is True:
    ''' this function lets the program either be terse or speak freely
    use vprint() for verbose messages and print() for standard program output
    ''' 
    
    def vprint(*args):
        '''
        
        verbose=Print each argument separately so caller doesn't need to
        stuff everything to be printed into a single string also prints all characters
        
        '''
        for arg in args:
            print(arg)
else:
    vprint = lambda *a: None      # a do-nothing function

# assign command strings:

commandStrings = []#""

for i in range(1,len(DEFAULTS)+1):
    data_string = "%sS%d" % (command_prefix,i)   
    #commandStrings = commandStrings+data_string
    #print(commandStrings)
    commandStrings.append(data_string)
#print(commandStrings)

#commandStrings.split(',')
#print(commandStrings[0])



def check_OK(response):
    """
    Checks for an "OK" response within a string.
    
    """

    ok = "OK" in response
    if not ok:
        vprint("ERROR: OK not found in response")
    return ok


def get_response():
    """
    Gets a response from the serial port.
    """

    sleep_time_after_buffer_read = 2
    # vprint("Characters in receive buffer before reading:", inBuffer)
    response = b''
    while ser.inWaiting():
        # vprint("Reading serial port buffer.")
        response += ser.readline()
        # vprint("Response:", response.decode('utf-8', errors='ignore'))
        time.sleep(sleep_time_after_buffer_read)
        # vprint("Characters in receive buffer after reading and waiting %d seconds:" % sleep_time_after_buffer_read, ser.inWaiting())
    vprint("No more characters in serial port buffer.")
    return response.decode('utf-8', errors='ignore') # so response is a string==> ie- serial.read returns strings due to response.decode==> you have to decode the encoded serial string with utf-8 


def command_mode():
    """
    Enters command mode
    """

    ser.flushOutput()
    ser.flushInput()
    time.sleep(1)           # give the flush a second
    vprint("Sent newline and carriage return")
    command = "\r\nATO\r\n"     #     the ATO command must start on a newlineexit& AT command mode if we are in it
    ser.write(command.encode('utf-8'))
    vprint("Sent command: '{}'".format(command.strip())) # command.strip() takes off ends (front and back) of string command
    time.sleep(1)
    # test to see if we are stuck in AT command mode.  If so, we see a response from this.
    command = "ATI\r\n"
    vprint("Sent command: '{}'".format(command.strip()))
    time.sleep(1.5)           # minimum 1 second wait needed before +++
    command = "+++"         # +++ enters AT command mode
    ser.write(command.encode('utf-8'))
    vprint("Sent command: '{}'".format(command.strip()))
    time.sleep(2)           # minimum 1 second wait after +++
    response = get_response()
    if check_OK(response):
        return True
    else:
        return False



def test_baud():
    """ 
    tries to connect at each possible baud rate until it gets a successful response 
    
    """ 

    # Notes about serial port modes:
    # when opening the serial port,
    # possible timeout values:
    #    1. None: wait forever, block call
    #    2. 0: non-blocking mode, return immediately
    #    3. x, x is bigger than 0, float allowed, timeout block call

    for test_baud in sorted(serial_speeds, reverse=True):
        print("testing baurate at {} ...".format(test_baud))
        ser.baudrate = test_baud
        try:
            ser.open() #opens serial port at ser.baudrate; used to check if baudrate is good
        except SerialException:
            print("Couldn't open serial port {}".format(ser.port))
            sys.exit(3)
        vprint("Testing serial port at {} baud.".format(test_baud))
        if command_mode():
            vprint("Test passed at", test_baud, "baud.")
            # return the baud value and leave serial port open
            return(test_baud)
        vprint("Test failed at", test_baud, "baud.")
        ser.close()
    vprint("Could not determine baud rate!  Exiting.")
    sys.exit(9)


def init():
    '''
    initiliaze function; tests bauds,port and command mode success

    '''

    if len(sys.argv) <= 1:     #if no argument is inputted in terminal print the help page with all the info on commands
        parser.print_help()
        sys.exit(1)

    ser.port = options.port
    ser.timeout = 0 # return immedidately 
    vprint("Serial port is {}".format(ser.port))

 
    # are we testing for baudrate only?
    if options.test_baud is True:
        baud = test_baud()
        ser.close()
        print("Radio currently working at {} bauds".format(baud))
        sys.exit(0)          # if test_baud was specified, then exit after test

    if options.baud in serial_speeds:
        baud = options.baud
    else:
        vprint(options.baud, " baud is not a valid speed.")
        sys.exit(4)

    ser.baudrate = baud
    vprint("Serial port speed set to", baud, "baud.")

    # print the serial port settings
    vprint("Serial port settings:\n\t", ser)

    # open the serial port
    try:
        ser.open()
    except SerialException:
        print("Couldn't open serial port {}".format(ser.port))
        sys.exit(5)
    vprint("Serial port {} opened.".format(ser.portstr))

    # enter command mode
    if not command_mode():
        print("Couldn't enter command mode")
        print("Check the port and the baudrate (or use -b to detect baudrate)")
        sys.exit(6)

    # flush the input and output buffers
    ser.flushOutput()
    ser.flushInput()
    time.sleep(1)  # give the flush a second. 


    return 0

def parseOptions(options):
    '''
    parses the radios main option values and writes the appropriate commands to the rfd900+

    '''
    
    data =data2=""
    ii=0
    any_change = False #this var controls if radio EEPROM is going to be written 
    command = []
    dataOld = []
    # getting radio parameters:
    vprint("Getting parameters.")
    command = "%sI5\r\n" % command_prefix
    vprint("Sending command: {}".format(command.strip()))
    ser.write(command.encode('utf-8'))
    time.sleep(2)
    response = get_response()
    #make array of only numbers from response string:
    for item in response.split("="): # note:  .split() default is whitespace
        for subitem in item.split():
            if(subitem.isdigit()):
                dataOld.append(subitem)
    #vprint(dataOld)
    dataOld.pop(0)
    #{2400: 2, 4800: 4, 9600: 9, 19200: 19, 38400: 38, 57600: 57, 115200: 115}
    if(dataOld[0] == "2"):
        dataOld[0]= "2400"
    elif(dataOld[0]=="4"):
        dataOld[0] = "4800"
    elif(dataOld[0]=="9"):
        dataOld[0] = "9600"
    elif(dataOld[0]=="19"):
        dataOld[0] = "19200"
    elif(dataOld[0]=="38"):
        dataOld[0] = "38400"
    elif(dataOld[0]=="57"):
        dataOld[0] = "57600"
    elif(dataOld[0]=="115"):
        dataOld[0] = "115200"
    #vprint("********************\nresponse serial read values are:%s \n*********************"%response)

    #vprint("********************\ndataOld serial values are: {} \n**********************".format(dataOld))
    ser.close()
    ser.open() #reopening serial port for use below
    #vprint("length of default:%d"%(len(DEFAULTS)))
    #vprint("length of dataOld:%d"%(len(dataOld)))
    for i in (vars(options)):
     
        options_name = i

        options_value = getattr(options, options_name)
        #vprint("****************************")
        #vprint(options_name,options_value)
     
        #vprint("count, ii is at: %d"%(ii))
        #vprint("options name is {} and value is: {}".format(options_name,options_value))
        if ((ii>=0) and (ii<= len(dataOld)-1)): 
            vprint(" ii is in range of dataOld")
            if(str(options_value) != str(dataOld[ii])):
                vprint("options_value!= dataOld")
                if options_value in RANGES[ii]:
                    any_change =True 
                    vprint("Setting %s to %s " % (options_name,options_value))
                    vprint("Sending command: {}".format(commandStrings[ii].strip()))
                    commandStrings[ii] = (commandStrings[ii]+"=%s\r\n"%options_value)
                    vprint("command string is %s"%commandStrings[ii])
                    ser.write(commandStrings[ii].encode('utf-8'))
                    time.sleep(2)
                    response = get_response()
                    if not check_OK(response):
                        vprint("check_ok not present.Now exiting.")
                        sys.exit(90+ii) #terminates program
                else:
                    vprint("value not in range. Now exiting.")
                    sys.exit(100+ii)

        ii=ii+1
    

    return any_change


def main():
    '''
    main function, calls all other functions here

    '''
    init()
    any_change = parseOptions(options)
       

    # write to EEPROM and reboot
    if any_change:
        command = "%s&W\r\n" % command_prefix
        vprint("Sending command to write to EEPROM: {}".format(command.strip()))
        ser.write(command.encode('utf-8'))
        time.sleep(2)
        response = get_response()
        if not check_OK(response):
            print("ERROR writing parameters in EEPROM")
        command = "%sZ\r\n" % command_prefix
        vprint("Sending command: {}".format(command.strip()))
        ser.write(command.encode('utf-8'))

    # close the serial port
    ser.close()
    vprint("Serial port {} closed. Now exitting program as well.".format(ser.portstr))
    sys.exit(22)
    return 0


if __name__ == "__main__":
    main()

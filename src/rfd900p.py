import serial 
import sys
import glob


'''
******* SOME REFERENCES:******************
1. A command-line radio setup script for radios with SiK software, like the RFD900 or 3DR. written to communicate with SiK version 2.6 (multipoint firmware):

    i. https://github.com/danidask/SiKset
    ii. https://community.emlid.com/t/sikset-py-a-python-script-to-easily-control-your-rfd900-3dr-radio-from-the-command-line/3654/10
    iii. https://ardupilot.org/copter/docs/common-3dr-radio-advanced-configuration-and-technical-information.html


2. info on pyserial: 
    i. https://pyserial.readthedocs.io/en/latest/shortintro.html
    ii. https://stackoverflow.com/questions/12090503/listing-available-com-ports-with-python


******************************************

'''

#list all serial ports being used:
def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result

def RFD900():

    #assign serial port:
    ser = serial.Serial('COM4', 57600, timeout=0, parity=serial.PARITY_EVEN, rtscts=1)
    print(ser.name) # check which port was really used
    





if __name__ == '__main__':
    print(serial_ports())
    RFD900() 






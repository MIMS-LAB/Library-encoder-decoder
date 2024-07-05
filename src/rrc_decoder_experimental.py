# please see hamming codes online for the algorithm behind this madness

# Unstaggers data
# The logic behind this is that Hamming squares only work for 1 bit flip. If we get two bit flips in one hamming square,
# the data is lost. So instead of putting our hamming squares sequentially, like
# 1111 1111 1111 1111 2222 2222 2222 2222 ...
# where 1,2,3,4 are bits to different hamming blocks,
# we "swizzle" them to
# 1234 1234 1234 1234 1234 1234 1234 1234...
# so if four bit flips happen one after the other, it still transmits fine!
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
def self_correct(square):
    # todo: make 1st bit work
    pos = 0  # error of location
    if bitcount(square & 0x5555) % 2 == 1:
        pos += 1
    if bitcount(square & 0x3333) % 2 == 1:
        pos += 2
    if bitcount(square & 0x0F0F) % 2 == 1:
        pos += 4
    if bitcount(square & 0x00FF) % 2 == 1:
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


def decodePacketsExperimental(packets):
    swizzled_packets = []
    for i in range(0, 8, 2):
        # assemble square (2 bytes -> 1 short)
        square: int = 0
        square |= packets[i] << 8
        square |= packets[i+1]
        swizzled_packets.append(square)

    # deswizzle data
    deswizzled_packets = [0] * len(swizzled_packets)
    deswizzle(swizzled_packets, deswizzled_packets)

    decoded_packets = []

    for packet in deswizzled_packets:
        packet = self_correct(packet)
        packet = unhamm_square(packet)
        decoded_packets.append(packet)


    header = decoded_packets[0] >> 8
    time  = (decoded_packets[0] & 0x8) << 11
    time |= (decoded_packets[1])

    data  = (decoded_packets[2]) << 11
    data |= (decoded_packets[3])

    data = fixData(data, header)
    header_list = ["GPS_LONG", "GPS_LAT", "ACC_X", "ACC_Y", "ACC_Z", "PRESS", "TEMP", "END"]
    header_string = header_list[header]

    return { "header"    : header,
             "name"      : header_string,
             "data"      : data,
             "time"      : time}
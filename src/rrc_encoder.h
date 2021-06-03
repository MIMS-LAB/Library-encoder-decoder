#ifndef RRC_ENCODER_RRC_V2_3_H
#define RRC_ENCODER_RRC_V2_3_H


#define BAR   0x00       //  baromete        (000)
#define GPS_L 0x01       //  gps longitude   (001)
#define GPS_T 0x02       //  gps latitude    (010)
#define ACC_X 0x03       //  accelerometer x (011)
#define ACC_Y 0x04       //  accelerometer y (100)
#define ACC_Z 0x05       //  accelerometer z (101)
#define TEMP  0x06       //  temperature     (110)
#define T_END 0x07       //  end             (111)

#define C_SHIFT 1        //  checksum shift
#define H_SHIFT 5        //  header shift


/**
 * @brief Generate the checksum for a 3 byte integer.
 * @param data is the 3 byte integer.
 * @return An 8 bit integer with the calulated checksum, but only the lowest 4 bits are what matters.
 */
uint8_t _checksum(uint32_t data)
{
    uint8_t result = 0x01 &  (data & 0x01)             //  LSB of the whole thing (0x01    = 0000 0000 0000 0000 0000 0001)
                   | 0x02 & ((data & 0x80)    >> 6)    //  MSB of the lowest byte (0x80    = 0000 0000 0000 0000 1000 0000)
                   | 0x04 & ((data & 0x8000)  >> 13)   //  MSB of the middle byte (0x8000  = 0000 0000 1000 0000 0000 0000)
                   | 0x08 & ((data & 0x10000) >> 13);  //  LSB of the higest byte (0x10000 = 0000 0001 0000 0000 0000 0000)

    return result;
}


/**
 * @brief Convert float data to a 3 byte int and flip the higest bit if negative.
 * @param data is the float data to be converted.
 * @param range is the number of decimal points to be kept in the resulting integer.
 * @return A 32 bit integer with only top 24 bits used. Bit 24 is flipped to 1 if data is negative.
 */
uint32_t _float2int(float data, int header)
{
    uint32_t int_data, 
             range = header == BAR ? 100 : 10000, 
             neg = 0;

	if(data < 0)
	{
        data *= -1;                      //  We don't need 2's complement
        neg = 1;
    }

    int_data = data*range+0.5;
    if(neg) int_data |= 0x800000;        //  flip higest bit

    return int_data;
}


/**
 * @brief Encodes a float into 8 bytes with headers, checksum and time stamp.
 * @param data is the float data to be encoded.
 * @param header is the header, or type, of the data being encoded.
 * @param time is the time stamp of the time the data was encoded.
 * @param out is a pointer to the list for the resulting list.
 * @return Zero on success with the modified out list.
 */
int encode(float data, int header, uint16_t time, uint8_t *out)
{
    uint32_t int_data = _float2int(data, header);
    uint8_t checks = _checksum(int_data);

    out[0] = header << H_SHIFT | checks << C_SHIFT | (int_data & 0x800000) >> 23;  //  data (0x800000 = 1000 0000 0000 0000 0000 0000)
    out[1] = header << H_SHIFT | (int_data & 0x7c0000) >> 18;                      //  data (0x7c0000 = 0111 1100 0000 0000 0000 0000)
    out[2] = header << H_SHIFT | (int_data & 0x03e000) >> 13;                      //  data (0x03e000 = 0000 0011 1110 0000 0000 0000)
    out[3] = header << H_SHIFT | (int_data & 0x001f00) >>  8;                      //  data (0x001f00 = 0000 0000 0001 1111 0000 0000)
    out[4] = header << H_SHIFT | (int_data & 0x0000f8) >>  3;                      //  data (0x0000f8 = 0000 0000 0000 0000 1111 1000)
    out[5] = header << H_SHIFT | (int_data & 0x000007) <<  2                       //  data (0x000007 = 0000 0000 0000 0000 0000 0111)
           | (time & 0x0c00) >> 10;                                                //  time (0x0c00 = 1100 0000 0000)
    out[6] = header << H_SHIFT | (time & 0x03e0) >> 5;                             //  time (0x03e0 = 0011 1110 0000)
    out[7] = T_END  << H_SHIFT | (time & 0x001f);                                  //  time (0x001f = 0000 0001 1111)

    return 0;
}

#endif
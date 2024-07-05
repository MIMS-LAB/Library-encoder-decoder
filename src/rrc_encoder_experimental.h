// please see hamming codes online for the algorithm behind this madness

// Formats data to give gaps for redundancy
// Before, data:
// XXX XDDD DDDD DDDD
// After, with gaps for redundancy:
// XXX1 XDDD XDDD DDDD
uint16_t hamm_square(uint16_t data){
	uint16_t out = 0;
	
	out |= (data & 0x0400) << 2; // 0x0400 = 0000 0100 0000 0000
	out |= (data & 0x0380) << 1; // 0x0380 = 0000 0011 1000 0000
	out |= (data & 0x007F);      // 0x007F = 0000 0000 0111 1111
	return out;
}

// Counts # of 1 bits in a uint16
uint8_t bitcount(uint16_t data){
	// almost certainly an easier way but this works for now
	uint8_t count = 0;
	for(int i = 0; i < 16; i++){
		if(data % 2 == 1) // maybe this isn't efficient. check
			count++;
		data = data >> 1;
	}
	return count;
}

// Encodes redundancy bits into a uint16.
// Expected that room for redundancy has already been given (see hamm_square)
// TODO: Maybe use the first bit for something. But please note, it is vulnerable.
uint16_t hamm_encode(uint16_t unhammed_squared){
	uint16_t hammed_code = unhammed_squared;
	// 1 -> 0101 0101 0101 0101 -> 0x5555
	// 2 -> 0011 0011 0011 0011 -> 0x3333
	// 4 -> 0000 1111 0000 1111 -> 0x0F0F
	// 8 -> 0000 0000 1111 1111 -> 0x00FF
	
	// dry!
	if(bitcount(unhammed_squared & 0x5555) % 2 == 1)
		hammed_code |= 0x4000; // 0100 0000 0000 0000
	if(bitcount(unhammed_squared & 0x3333) % 2 == 1)
		hammed_code |= 0x2000; // 0010 0000 0000 0000
	if(bitcount(unhammed_squared & 0x0F0F) % 2 == 1)
		hammed_code |= 0x0800; // 0000 1000 0000 0000
	if(bitcount(unhammed_squared & 0x00FF) % 2 == 1)
		hammed_code |= 0x0080; // 0000 0000 1000 0000
	if(bitcount(unhammed_squared) % 2 == 1)
		hammed_code |= 0x8000; // 1000 0000 0000 0000
	return hammed_code;
}

// Staggers data
/*
 * The logic behind this is that Hamming squares only work for 1 bit flip.
 * If we get two bit flips in one hamming square,
 * the data is lost. So instead of putting our hamming squares sequentially, like
 * 1111 1111 1111 1111 2222 2222 2222 2222 ...
 * where 1,2,3,4 are bits to different hamming blocks,
 * we "swizzle" them to
 * 1234 1234 1234 1234 1234 1234 1234 1234...
 * so if four bit flips happen one after the other, it still transmits fine!
*/
void swizzle(uint16_t data_in[static 4], uint16_t data_out[static 4], int len){
	uint8_t write_pos = 15;
	uint8_t write_short = 0;
	
	for(int read_pos = 15; read_pos >= 0; read_pos--) {
		for (int i = 0; i < len; i++) {
			// Get read_pos bit of data_in[i]
			uint8_t bit = (data_in[i] & ( 1 << read_pos )) >> read_pos;
			
			// Write to data_out[write_short] at pos write_pos
			data_out[write_short] |= (bit << write_pos);
			
			// decrement write position
			write_pos--; // overflow intended
			if (write_pos == 255) { // equiv. to == -1
				write_pos = 15;
				write_short++;
			}
		}
	}
}


uint8_t encode_experimental(double data, uint8_t header, uint32_t time, uint8_t out[static 8])
{
	uint32_t int_data = _float2int(data, header);
	
	uint16_t hamming_squares[4];
	uint16_t swizzled_data[4];
	for(int i = 0; i < 4; i++) {
		hamming_squares[i] = 0; // Is this necessary?
		swizzled_data[i] = 0;
	}
		
	// Form data packets for the hamming square
	hamming_squares[0] = (header & RRC_MASK_HEADER) << 8;
	hamming_squares[0] |= (time & 0x07F80) <<  7; // 0000 0111 1111 1000 0000
	hamming_squares[1] = (time & 0x007FF);       // 0000 0000 0111 1111 1111
	hamming_squares[2] = (int_data & 0x3FF800) >> 11; // 0011 1111 1111 1000 0000 0000
	hamming_squares[3] = (int_data & 0x0007FF); // 0000 0000 0000 0111 1111 1111
	
	for(int i = 0; i < 4; i++){
		// Encode hamming code into the squares
		hamming_squares[i] = hamm_square(hamming_squares[i]);
		hamming_squares[i] = hamm_encode(hamming_squares[i]);
	}
	
	swizzle(hamming_squares, swizzled_data, 4);
	
	for(int i = 0; i < 4; i++){
		// Convert uint16_t to uint8_ts
		// intended overflow :)
		out[2*i] = swizzled_data[i] >> 8;
		out[(2*i)+1] = swizzled_data[i];
	}
	
	return 0;
}

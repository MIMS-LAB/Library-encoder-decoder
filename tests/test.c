#include <stdio.h>
#include <stdint.h>
#include <windows.h>
#include "encoder_rrc_v2_2.h"

HANDLE serialHandle;

/**
 * @brief Ask the user for a new loop
 * @param None
 * @return true for a new loop or false to exit
 */
int newLoop()
{
	return 1;
    char input;
    fflush(stdin);
    printf("Another loop? ");
    scanf("%c", &input);
    fflush(stdin);
    return input == 'y';
}


/**
 * @brief set the test COM port for use
 * @param None
 * @return a HANDLE type for the COM port
 */
HANDLE setComPort()
{
	serialHandle = CreateFile("\\\\.\\COM13", GENERIC_READ | GENERIC_WRITE, 0, 0, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, 0);

	if(serialHandle == INVALID_HANDLE_VALUE) {
		printf("handle creation failed\n");
		if(GetLastError() == ERROR_FILE_NOT_FOUND)
			printf("file not found\n");
	}

	DCB serialPropertise = {0};
	serialPropertise.DCBlength = sizeof(serialPropertise);

	if(!GetCommState(serialHandle, &serialPropertise))
		printf("error getting state\n");

	serialPropertise.BaudRate = CBR_57600;
	serialPropertise.ByteSize = 8;
	serialPropertise.fParity = 0;
	serialPropertise.Parity = NOPARITY;
	if(!SetCommState(serialHandle, &serialPropertise))
		printf("error setting state\n");

	return serialHandle;
}

int main()
{
	setComPort();

	do 
	{
		float num;
		int time, header;
		uint32_t int_data;
		uint8_t test[8];
		DWORD bytesWritten;

		printf("enter a number, header, and a time stamp: ");
		scanf("%f %d %d", &num, &header, &time);

		encode(num, header, time, test);

		printf("The encoded number is: %.4f\n", num);
		printf("The encoded data is: ");
		for(int i = 0; i < 8; i++) printf("%x ", test[i]);
		printf("\n");
		int_data = _float2int(num, header);
		printf("The integer sent is: %d\n", int_data);
		printf("The checksums is: %x\n", _checksum(int_data));
		printf("The header is: %x\n", header);
		printf("The time stamp is: %d\n", time);

		if(!WriteFile(serialHandle, test, 8, &bytesWritten, NULL))
			printf("error in writing\n");
	} while(newLoop());

	return 0;
}

#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <stdlib.h>
#include <windows.h>

#include "../src/rrc_encoder.h"




// /**
//  * @brief Ask the user for a new loop
//  * @param None
//  * @return true for a new loop or false to exit
//  */
// int newLoop()
// {
// 	return 1;
//     char input;
//     fflush(stdin);
//     printf("Another loop? ");
//     scanf("%c", &input);
//     fflush(stdin);
//     return input == 'y';
// }


/**
 * @brief set the test COM port for use
 * @param None
 * @return a HANDLE type for the COM port
 */
HANDLE setComPort(char *portName)
{
    HANDLE serialHandle = CreateFile(portName, GENERIC_READ | GENERIC_WRITE, 0, 0, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, 0);

    if(serialHandle == INVALID_HANDLE_VALUE) {
        printf("handle creation failed");
        if(GetLastError() == ERROR_FILE_NOT_FOUND)
            printf(": file not found");

        printf("\n");

        exit(-1);
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

int main(int argc, char *argv[])
{
    unsigned int  header, time;
    char     comPort[] = "\\\\.\\";
    double   data;
    uint8_t  result[RRC_DATAPACK_SIZE];
    DWORD    bytesWritten;
    HANDLE   serialHandle;

    if(argc < 5)
    {
        printf("Too few arguments\n");
        exit(-1);
    }

    strcat(comPort, argv[1]);
    header = atoi(argv[2]);
    data   = atof(argv[3]);
    time   = atoi(argv[4]);

    serialHandle = setComPort(comPort);

    encode(data, header, time, result);

    #define DEBUG 0
    if(DEBUG)
    {
        printf("The COM port is:       %s\n", comPort);
        printf("The header is:         %u\n", header);
        printf("The encoded number is: %.4lf\n", data);
        printf("The time stamp is:     %d\n", time);

        printf("\nencoded data is: [");
        for(int i = 0; i < RRC_DATAPACK_SIZE; i++)
        {
            printf("%x%s", result[i], i < RRC_DATAPACK_SIZE - 1? ", " : "");
        }
        printf("]\n");
    }


    if(!WriteFile(serialHandle, result, RRC_DATAPACK_SIZE, &bytesWritten, NULL))
    {
        printf("error in writing\n");
        exit(-1);
    }

    CloseHandle(serialHandle);

    return 0;
}

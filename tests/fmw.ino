//////////////////////////////
////                      ////
////    Very Old Draft    ////
////                      ////
//////////////////////////////


#include "../src/rrc_encoder.h"
#include <stdio.h>

#define IN_B_MAX 1000
#define OUT_B_MAX 1000

char input_b[IN_B_MAX], output_b[OUT_B_MAX];

const char enc_of[] = R"HERE(
The checksum is: %x
The header is    %d
The value is     %d
The time is:     %d
)HERE";

int time, header, value;
uint32_t int_data;
uint8_t enc_array[8];

void getLine(char *buffer, int n)
{
    char a;
    n = n > IN_B_MAX || n == 0 ? IN_B_MAX : n;
    
    for(int i = 0; i < n; i++)
    {
        a = Serial.read();

        if(a == -1) i--;
        else if(a != '\n') buffer[i] = a;
        else 
        {
            buffer[i] = '\0';
            break;
        }
    }
}

void setup()
{
    Serial.begin(115200);
    Serial3.begin(115200);
}

void loop()
{
    Serial.println("Please enter a value, a header and a timestamp: ");
    getLine(input_b, 0);
    sscanf(input_b, "%d %d %d", &value, &header, &time);

    encode((float)value, header, time, enc_array);
    int_data = header == 0 ? _float2int(value, 100) : _float2int(value, 10000);

    Serial.print("The encoded data is: ");
    for(int i = 0; i < 8; i++)
    {
        sprintf(output_b, "%x ", enc_array[i]);
        i == 7 ? Serial.println(output_b) : Serial.print(output_b);
    }

    sprintf(output_b, enc_of, _checksum(int_data), header, value, time);
    Serial.println(output_b);

    for(int i = 0; i < 8; i++) Serial3.write(enc_array[i]);
}
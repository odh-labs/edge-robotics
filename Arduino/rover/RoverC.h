#ifndef _ROVERC_H_
#define _ROVERC_H_

#include <M5StickCPlus.h>

#define ROVER_ADDRESS	0X38

// Initialise I2C robot interface
//sda  0, scl  26
void RoverC_Init(void);	//sda  0     scl  26

// transmit over I2C interface
void Send_iic(uint8_t Register, uint8_t Speed);

// basic movement methods
void Move_forward(int8_t Speed);

void Move_back(int8_t Speed);

void Move_turnleft(int8_t Speed);

void Move_turnright(int8_t Speed);

void Move_left(int8_t Speed);

void Move_right(int8_t Speed);

void Move_stop(int8_t Speed);


#endif

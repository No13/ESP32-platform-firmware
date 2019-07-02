#ifndef SYSTEM_H
#define SYSTEM_H

#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_spi_flash.h"
#include "esp_system.h"

void logo( void );
void restart( void );
int get_magic( void );

#endif

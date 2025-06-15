#include <stdio.h>
#include "esp_log.h"
#include "driver/gpio.h"
#include "driver/i2c_master.h"
#include "sdkconfig.h"
#include "math.h"
#include "esp_task.h"
#include <string.h>
#include <stdlib.h>
#include <time.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/uart.h"
#include "vars.h"


//===============>> UART

// Function for sending things to UART1
static int uart1_printf(const char *str, va_list ap) {
    char *buf;
    vasprintf(&buf, str, ap);
    uart_write_bytes(UART_NUM_1, buf, strlen(buf));
    free(buf);
    return 0;
}

// Setup of UART connections 0 and 1, and try to redirect logs to UART1 if asked
static void uart_setup() {
    uart_config_t uart_config = {
        .baud_rate = 115200,
        .data_bits = UART_DATA_8_BITS,
        .parity = UART_PARITY_DISABLE,
        .stop_bits = UART_STOP_BITS_1,
        .flow_ctrl = UART_HW_FLOWCTRL_DISABLE,
    };

    uart_param_config(UART_NUM_0, &uart_config);
    uart_param_config(UART_NUM_1, &uart_config);
    uart_driver_install(UART_NUM_0, BUF_SIZE * 2, 0, 0, NULL, 0);
    uart_driver_install(UART_NUM_1, BUF_SIZE * 2, 0, 0, NULL, 0);

    // Redirect ESP log to UART1
    if (REDIRECT_LOGS) {
        esp_log_set_vprintf(uart1_printf);
    }
}

// Read UART_num for input with timeout of 1 sec
int serial_read(char *buffer, int size){
    int len = uart_read_bytes(UART_NUM, (uint8_t*)buffer, size, pdMS_TO_TICKS(1000));
    return len;
}

static void uart_begin() {
    // esperar un BEGIN antes de comenzar el envío de datos
    char dataBEGIN[6];

    while (1) {
        int rLen = serial_read(dataBEGIN, 6);
        if (rLen > 0) {
            if (strcmp(dataBEGIN, "BEGIN") == 0) {
                uart_write_bytes(UART_NUM, "OK\0", 3);
                break;
            }
        }
    }
}

static void uart_end() {
    while (1) {
        uart_write_bytes(UART_NUM, "OK\0", 3);
    }
}

static void uart_send_ventana(float *data) {
    char dataResponse2[4];
    while(1) {
        const char *dataToSend = (const char *)data;
        int len_data = WINDOW_LENGTH * sizeof(float);
        uart_write_bytes(UART_NUM, dataToSend, len_data);
        int rLen = serial_read(dataResponse2, 4);
        if (rLen > 0) {
            if (strcmp(dataResponse2, "END") == 0) {
                break;
            }
        }
        vTaskDelay(pdMS_TO_TICKS(1000));  // Delay for 1 second

    }
}

static void uart_send_peaks(float *data) {
    char dataResponse2[4];
    while(1) {
        const char *dataToSend = (const char *)data;
        int len_data = 5 * sizeof(float);
        uart_write_bytes(UART_NUM, dataToSend, len_data);
        int rLen = serial_read(dataResponse2, 4);
        if (rLen > 0) {
            if (strcmp(dataResponse2, "END") == 0) {
                break;
            }
        }
        vTaskDelay(pdMS_TO_TICKS(1000));  // Delay for 1 second
    }
}

static void uart_send_rms(float *data) {
    char dataResponse2[4];
    while(1) {
        const char *dataToSend = (const char *)data;
        int len_data = 9 * sizeof(float);
        uart_write_bytes(UART_NUM, dataToSend, len_data);
        int rLen = serial_read(dataResponse2, 4);
        if (rLen > 0) {
            if (strcmp(dataResponse2, "END") == 0) {
                break;
            }
        }
        vTaskDelay(pdMS_TO_TICKS(1000));  // Delay for 1 second
    }
}

static void uart_send_fft(float *data_re, float *data_im) {
    char dataResponse2[4];
    while(1) {
        const char *dataToSend_re = (const char *)data_re;
        const char *dataToSend_im = (const char *)data_im;
        int len_data = sizeof(float) * WINDOW_LENGTH;
        uart_write_bytes(UART_NUM, dataToSend_re, len_data);
        uart_write_bytes(UART_NUM, dataToSend_im, len_data);
        int rLen = serial_read(dataResponse2, 4);
        if (rLen > 0) {
            if (strcmp(dataResponse2, "END") == 0) {
                break;
            }
        }
        vTaskDelay(pdMS_TO_TICKS(1000));  // Delay for 1 second
    }
}
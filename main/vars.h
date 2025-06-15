#ifndef VARS_H
#define VARS_H

#define I2C_MASTER_SCL_IO	22				//GPIO pin
#define I2C_MASTER_SDA_IO	21				//GPIO pin
#define I2C_MASTER_FREQ_HZ	10000		
#define ESP_SLAVE_ADDR		0x68
#define WRITE_BIT		0x0
#define READ_BIT		0x1
#define ACK_CHECK_EN		0x0
#define EXAMPLE_I2C_ACK_CHECK_DIS		0x0
#define ACK_VAL		0x0
#define NACK_VAL		0x1
#define Fodr (800)
#define G (8.000/32768)
#define RAD (34.90659/32768)
#define MS (78.4532/32768)
#define BUF_SIZE (128)
#define TXD_PIN (1)
#define RXD_PIN (3)
#define UART_NUM (UART_NUM_0)
#define BAUD_RATE (115200)
#define REDIRECT_LOGS (1) // Redirect ESP logs to UART1
#define M_PI (3.14159)
#define WINDOW_LENGTH 20

#endif // VARS_H
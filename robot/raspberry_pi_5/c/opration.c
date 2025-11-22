#include <stdio.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdlib.h>

#include <linux/gpio.h>
#include <sys/ioctl.h>
#include <string.h>

#include "opration.h"

#define EXE(e) {if(e != 0) return;}

enum wheel {LB, LF, RF, RB};

int GPIO(char *filename, int gpio_num, int value) {

    int gpio_fd = open(filename, O_RDWR);
    if (gpio_fd == -1) {
        perror("Failed to open GPIO device");
        return -1;
    }

    struct gpiohandle_request req;
    req.lineoffsets[0] = gpio_num;
    req.lines = 1;
    req.flags = GPIOHANDLE_REQUEST_OUTPUT;
    strcpy(req.consumer_label, "my_gpio");

    if (ioctl(gpio_fd, GPIO_GET_LINEHANDLE_IOCTL, &req) == -1) {
        perror("Failed to export GPIO");
        close(gpio_fd);
        return -1;
    }

    struct gpiohandle_data data;
    data.values[0] = value;

    if (ioctl(req.fd, GPIOHANDLE_SET_LINE_VALUES_IOCTL, &data) == -1) {
        perror("Failed to set GPIO value");
        close(req.fd);
        close(gpio_fd);
        return -1;
    }

    close(req.fd);
    close(gpio_fd);
    return 0;
}

/**
 *  Switching LED lights.
 */
int led = 1;
void change_led() {
    if (led == 0) {
        EXE(GPIO(GPIOCHIPX, GPIO_LED_NUM, 1));
        led = 1;
    } else {
        EXE(GPIO(GPIOCHIPX, GPIO_LED_NUM, 0));
        led = 0;
    }
}

void rotate_forward(enum wheel w) {
    switch(w) {
        case LB: EXE(GPIO(GPIOCHIPX, LB0, 0)); EXE(GPIO(GPIOCHIPX, LB1, 1)); break;
        case LF: EXE(GPIO(GPIOCHIPX, LF0, 0)); EXE(GPIO(GPIOCHIPX, LF1, 1)); break;
        case RF: EXE(GPIO(GPIOCHIPX, RF0, 0)); EXE(GPIO(GPIOCHIPX, RF1, 1)); break;
        case RB: EXE(GPIO(GPIOCHIPX, RB0, 0)); EXE(GPIO(GPIOCHIPX, RB1, 1)); break;
    }
}

void rotate_stop(enum wheel w) {
    switch(w) {
        case LB: EXE(GPIO(GPIOCHIPX, LB0, 1)); EXE(GPIO(GPIOCHIPX, LB1, 1)); break;
        case LF: EXE(GPIO(GPIOCHIPX, LF0, 1)); EXE(GPIO(GPIOCHIPX, LF1, 1)); break;
        case RF: EXE(GPIO(GPIOCHIPX, RF0, 1)); EXE(GPIO(GPIOCHIPX, RF1, 1)); break;
        case RB: EXE(GPIO(GPIOCHIPX, RB0, 1)); EXE(GPIO(GPIOCHIPX, RB1, 1)); break;
    }
}

void rotate_backward(enum wheel w) {
    switch(w) {
        case LB: EXE(GPIO(GPIOCHIPX, LB0, 1)); EXE(GPIO(GPIOCHIPX, LB1, 0)); break;
        case LF: EXE(GPIO(GPIOCHIPX, LF0, 1)); EXE(GPIO(GPIOCHIPX, LF1, 0)); break;
        case RF: EXE(GPIO(GPIOCHIPX, RF0, 1)); EXE(GPIO(GPIOCHIPX, RF1, 0)); break;
        case RB: EXE(GPIO(GPIOCHIPX, RB0, 1)); EXE(GPIO(GPIOCHIPX, RB1, 0)); break;
    }
}

void stop() {
    rotate_stop(LB);
    rotate_stop(LF);
    rotate_stop(RF);
    rotate_stop(RB);
}

void front() {
    rotate_forward(LB);
    rotate_forward(LF);
    rotate_forward(RF);
    rotate_forward(RB);
}

void back() {
    rotate_backward(LB);
    rotate_backward(LF);
    rotate_backward(RF);
    rotate_backward(RB);
}

void left() {
    rotate_backward(LF);
    rotate_backward(RB);
    rotate_forward(RF);
    rotate_forward(LB);
}

void right() {
    rotate_backward(RF);
    rotate_backward(LB);
    rotate_forward(LF);
    rotate_forward(RB);
}


void left_rotate() {
    rotate_backward(LF);
    rotate_backward(LB);
    rotate_forward(RF);
    rotate_forward(RB);
}

void right_rotate() {
    rotate_backward(RF);
    rotate_backward(RB);
    rotate_forward(LF);
    rotate_forward(LB);
}


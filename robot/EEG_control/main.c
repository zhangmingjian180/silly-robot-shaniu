#include <stdio.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <termios.h>
#include <stdlib.h>

#include <linux/gpio.h>
#include <sys/ioctl.h>
#include <string.h>

#define BUFFER_SIZE 200

#define EXE(e) {if(e != 0) return;}

int set_attr(int fd, speed_t speed, unsigned char vmin, unsigned char vtime){
    struct termios options, termios_chk;
    int flag;

    flag = tcgetattr(fd, &options);
    if(flag == -1) {
        perror("can't get arribute of termninal.");
        return -1;
    }

    // raw model.
    cfmakeraw(&options);

    options.c_cflag &= ~(CSIZE | PARENB);
    options.c_cflag |= CS8;
    options.c_cflag &= ~CSTOPB;
    options.c_cflag |= CREAD;

    options.c_cc[VMIN] = vmin;
    options.c_cc[VTIME] = vtime;

    flag = tcsetattr(fd, TCSANOW, &options);
    if(flag == -1) {
        perror("can't set arribute of termninal.");
        return -1;
    }

    // check whether the changes all is set.
    flag = tcgetattr(fd, &termios_chk);
    if(flag == 0) {
        if(options.c_cflag != termios_chk.c_cflag){
            perror("Failed to set the parameters of termios\n");
            return -1;
        }
    } else {
        perror("can't get arribute of termninal.");
        return -1;
    }

    flag = cfsetispeed(&options, speed); //B115200 为宏定义
    if(flag == -1) {
        perror("can't set speed of termninal.");
        return -1;
    }

    flag = tcflush(fd, TCIOFLUSH);
    if(flag == -1) {
        perror("can't tcflush of termninal.");
        return -1;
    }

    return 0;
}

int set_attr_v(int fd, unsigned char vmin, unsigned char vtime){
    struct termios options, termios_chk;
    int flag;

    flag = tcgetattr(fd, &options);
    if(flag == -1) {
        perror("can't get arribute of termninal.");
        return -1;
    }

    options.c_cc[VMIN] = vmin;
    options.c_cc[VTIME] = vtime;

    flag = tcsetattr(fd, TCSANOW, &options);
    if(flag == -1) {
        perror("can't set arribute of termninal.");
        return -1;
    }

    // check whether the changes all is set.
    flag = tcgetattr(fd, &termios_chk);
    if(flag == 0) {
        if(options.c_cflag != termios_chk.c_cflag){
            perror("Failed to set the parameters of termios\n");
            return -1;
        }
    } else {
        perror("can't get arribute of termninal.");
        return -1;
    }

    flag = tcflush(fd, TCIOFLUSH);
    if(flag == -1) {
        perror("can't tcflush of termninal.");
        return -1;
    }

    return 0;
}

int send(int fd, unsigned char *message, unsigned int length) {
    unsigned char buffer[BUFFER_SIZE] = {0};
    unsigned int n = 0, flag = 0;

	printf("-------------\n");

	flag = tcflush(fd, TCIOFLUSH);
    if(flag == -1) {
        perror("can't tcflush of termninal.");
        return -1;
    }

    puts(message);
    n = write(fd, message, length);
    if(n != length) {
        perror("failed to write. error code 001");
        return -1;
    }
    n = read(fd, buffer, BUFFER_SIZE);
    if(n == -1) {
        perror("failed to read. error code 002");
        return -1;
    }
    puts(buffer);

    return 0;
}

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

void display_bytes(unsigned char *data, unsigned int len){
    unsigned int j;
    for(j = 0;j < len;j++)
        printf("%#hhX\t", data[j]);
    printf("\n");
}

/**
 *  Switching LED lights.
 */
int led = 1;
void change_led() {
	if (led == 0) {
        EXE(GPIO("/dev/gpiochip0", 0, 1));
		led = 1;
    } else {
        EXE(GPIO("/dev/gpiochip0", 0, 0));
		led = 0;
    }
}

#define LB0 131
#define LB1 132
#define LF0 133
#define LF1 134
#define RF0 137
#define RF1 138
#define RB0 139
#define RB1 140

enum wheel {LB, LF, RF, RB};

void rotate_forward(enum wheel w) {
    switch(w) {
        case LB: EXE(GPIO("/dev/gpiochip0", LB0, 0)); EXE(GPIO("/dev/gpiochip0", LB1, 1)); break;
        case LF: EXE(GPIO("/dev/gpiochip0", LF0, 0)); EXE(GPIO("/dev/gpiochip0", LF1, 1)); break;
        case RF: EXE(GPIO("/dev/gpiochip0", RF0, 0)); EXE(GPIO("/dev/gpiochip0", RF1, 1)); break;
        case RB: EXE(GPIO("/dev/gpiochip0", RB0, 0)); EXE(GPIO("/dev/gpiochip0", RB1, 1)); break;
    }
}

void rotate_stop(enum wheel w) {
    switch(w) {
        case LB: EXE(GPIO("/dev/gpiochip0", LB0, 1)); EXE(GPIO("/dev/gpiochip0", LB1, 1)); break;
        case LF: EXE(GPIO("/dev/gpiochip0", LF0, 1)); EXE(GPIO("/dev/gpiochip0", LF1, 1)); break;
        case RF: EXE(GPIO("/dev/gpiochip0", RF0, 1)); EXE(GPIO("/dev/gpiochip0", RF1, 1)); break;
        case RB: EXE(GPIO("/dev/gpiochip0", RB0, 1)); EXE(GPIO("/dev/gpiochip0", RB1, 1)); break;
    }
}

void rotate_backward(enum wheel w) {
    switch(w) {
        case LB: EXE(GPIO("/dev/gpiochip0", LB0, 1)); EXE(GPIO("/dev/gpiochip0", LB1, 0)); break;
        case LF: EXE(GPIO("/dev/gpiochip0", LF0, 1)); EXE(GPIO("/dev/gpiochip0", LF1, 0)); break;
        case RF: EXE(GPIO("/dev/gpiochip0", RF0, 1)); EXE(GPIO("/dev/gpiochip0", RF1, 0)); break;
        case RB: EXE(GPIO("/dev/gpiochip0", RB0, 1)); EXE(GPIO("/dev/gpiochip0", RB1, 0)); break;
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
    rotate_stop(LF);
    rotate_forward(LB);
    rotate_forward(RF);
    rotate_forward(RB);
}

void right() {
    rotate_stop(RF);
    rotate_forward(LB);
    rotate_forward(LF);
    rotate_forward(RB);
}

void main() {
	int flag = 0, n = 0;
	
	printf("Starting ...\n");
    
    stop();

	int fd = 0;

    fd = open("/dev/ttyACM0", O_RDWR);
    if(fd == -1){
        perror("can't open the file.");
        return;
    }

    flag = set_attr(fd, B9600, BUFFER_SIZE, 10);
    if(flag == -1){
        perror("failed to set attribute.");
        return;
    }

	unsigned char ch = 0;
	while(1) {
		unsigned char buffer[2] = {0};
    	n = read(fd, buffer, sizeof(buffer));
    	if(n == -1) {
        	perror("failed to read. error code 002");
        	return;
    	}
    	puts(buffer);

		ch = buffer[0];
		switch(ch) {
            case 'w': front();      break;
            case 'q': stop();       break;
        }

	}

	printf("Finishing ...\n");
	return;
}

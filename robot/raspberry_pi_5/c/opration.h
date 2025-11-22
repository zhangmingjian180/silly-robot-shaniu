#define GPIOCHIPX "/dev/gpiochip4"

#define GPIO_LED_NUM 17

#define LB0 27
#define LB1 22
#define LF0 10
#define LF1 9
#define RF0 6
#define RF1 13
#define RB0 19
#define RB1 26

void change_led();
void front();
void back();
void left();
void right();
void left_rotate();
void right_rotate();
void stop();

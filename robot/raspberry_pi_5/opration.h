#define GPIOCHIPX "/dev/gpiochip0"

#define GPIO_LED_NUM 15

#define LB0 15
#define LB1 15
#define LF0 15
#define LF1 15
#define RF0 15
#define RF1 15
#define RB0 15
#define RB1 15

void change_led();
void front();
void back();
void left();
void right();
void left_rotate();
void right_rotate();
void stop();

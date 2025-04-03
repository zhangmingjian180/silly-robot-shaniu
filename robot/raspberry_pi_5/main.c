#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

#include "opration.h"

int main() {
    int sockfd;
    struct sockaddr_in serv_addr;
    unsigned char buf[1] = {0};

    stop();

    // 创建socket
    sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd < 0) {
        perror("socket creation failed");
        exit(EXIT_FAILURE);
    }
 
    // 初始化服务器地址
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(7922); // 端口号
    serv_addr.sin_addr.s_addr = inet_addr("47.108.220.136"); // IP地址
 
    // 连接到服务器
    if (connect(sockfd, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) < 0) {
        perror("connect failed");
        exit(EXIT_FAILURE);
    }
 
    printf("Connected to server\n");

    while(1) {
        if(recv(sockfd, buf, 1, 0) < 0) {
            perror("fail to read socket.");
            exit(EXIT_FAILURE);
        }

        switch(buf[0]) {
            case 'l': change_led(); break;
            case 'w': front();      break;
            case 's': back();       break;
            case 'a': left();       break;
            case 'd': right();      break;
            case 'q': left_rotate();       break;
            case 'e': right_rotate();      break;
            case 'f': stop();       break;
        }

    }

    // 关闭socket
    close(sockfd);
 
    return 0;
}

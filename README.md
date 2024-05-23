# silly-robot-shaniu

小车功能：

    远程遥控（运动控制）
    远程对话
    远征摄像
    脑控
    语音智能对话

文档说明

    小车配件表：Documents/components_car.pdf

## 安装工具
'''
安装烧写 spiflash 的工具
https://github.com/Icenowy/sunxi-tools f1c100s-spiflash 分支
'''

## 烧写镜像
'''
sudo sunxi-fel -p spiflash-write 0x0 images/boot/u-boot-sunxi-with-spl.bin
sudo sunxi-fel -p spiflash-write 0x0100000 images/boot/suniv-f1c100s-licheepi-nano.dtb
sudo sunxi-fel -p spiflash-write 0x0110000 images/boot/zImage
...

## uboot 启动参数
'''
# 该行用于从 spiflash 加载根文件系统，已被启用。
# env set bootargs console=ttyS0,115200 panic=5 rootwait root=/dev/mtdblock3 rw rootfstype=jffs2

# 从 spiflash 加载内核
env set bootcmd "sf probe 0; sf read 0x80c00000 0x100000 0x4000; sf read 0x80008000 0x110000 0x400000; bootz 0x80008000 - 0x80c00000"

# 从 TF 加载根文件系统。
env set bootargs console=ttyS0,115200 panic=5 rootwait root=/dev/mmcblk0p2 rw
'''

#ffmpeg -ac 1 -ar 11025 -f pulse -i alsa_input.usb-24ae_Rapoo_Gaming_Headset-00.mono-fallback -f flv rtmp://zhangmingjian180.love:1935:/mytv/speaker
#ffmpeg -ac 1 -ar 11025 -f pulse -i alsa_input.usb-Generic_AB13X_USB_Audio_20210926172016-00.mono-fallback -f flv rtmp://localhost:1935:/mytv/speaker
ffmpeg -ac 1 -ar 11025 -f alsa -i sysdefault:CARD=Audio -f flv rtmp://zhangmingjian180.love:1935:/mytv/speaker

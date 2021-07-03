# 流水线截图助手

本脚本的主要目的是可以自动截图并且上传到图床。目前只支持sm.ms图床。使用之前请准
备好api key。

## 预先准备

* 安装Python3并且设置好Python环境
* 安装需要的pip库
* 安装ffmpeg并确保在路径

## 使用说明

复制`example.config.yaml`到`config.yaml`, 修改`config.yaml`加入sm.ms的api key。

运行：

```
python main.py <视频文件路径>
```

脚本会自动截图，并上传到sm.ms图床。如果成功的话，你会收到一个通知告诉你。

如果你在Windows系统低下，也可以把一个视频文件拖到`run.bat`上面，效果等同与跑以
上命令。

# 打包为 EXE

将项目打包为独立可执行文件，无需安装 Python 即可运行。

## 使用方法

在项目根目录下运行：

```bash
cd package-exe
python build.py
```

打包完成后，输出目录为 `package-exe/dist/blive-vod/`。

## 分发

将 `dist/blive-vod/` 整个文件夹复制到目标电脑，双击 `启动点歌机.bat` 即可运行。

目标电脑仍需安装：
- [落雪音乐桌面版](https://github.com/lyswhut/lx-music-desktop/releases) 2.8.0+

## 注意事项

- 首次启动会自动生成 `config.json`（配置文件）
- 歌曲黑名单文件 `.A歌曲黑名单.txt` 已包含在打包目录中，可直接编辑
- 打包使用 `onedir` 模式（文件夹），启动速度比 `onefile` 更快
- 如遇杀毒软件误报，请添加信任

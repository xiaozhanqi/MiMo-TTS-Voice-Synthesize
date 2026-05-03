# MiMo TTS 语音合成器

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=Streamlit\&logoColor=white)](https://streamlit.io/)

> 一款基于小米 MiMo-V2.5-TTS 的桌面端文本转语音应用，支持音色设计、声音克隆和多种说话风格。

## ✨ 功能特性

- 🎙️ **预置音色** - 开箱即用，内置多种精品音色
- 🎨 **音色设计** - 通过文本描述定制专属音色
- 🎭 **声音克隆** - 基于音频样本复刻任意音色
- 🎵 **风格控制** - 支持语速、情绪、方言等多种风格
- 🎤 **唱歌模式** - 支持将歌词合成歌曲
- 💻 **桌面应用** - 基于 WebView2 的独立桌面程序
- 📦 **便携版本** - 单文件可执行程序，无需安装

## 🚀 快速开始

### 方式一：使用打包好的程序（推荐）

1. 下载最新版本的 `MiMoTTS语音合成器.exe`
2. 双击运行即可

### 方式二：从源码运行

```bash
# 克隆仓库
git clone https://github.com/xiaozhanqi/MiMo-TTS-Voice-Synthesize.git
cd MiMo-TTS-Voice-Synthesize

# 安装依赖
pip install -r requirements.txt

# 运行网页版
streamlit run src/mimo_tts_app.py

# 或运行桌面版
python src/desktop_app.py
```

## 📦 打包应用

```bash
python src/build_desktop_app.py
```

打包后的文件位于 `dist/MiMoTTS语音合成器.exe`

## 🔧 系统要求

- Windows 10/11
- .NET Framework 4.7.2 或更高版本
- WebView2 Runtime（首次运行会自动安装）

## 📝 使用说明

1. 获取 MiMo API Key
2. 在应用中输入 API Key
3. 选择模型和音色
4. 输入文本，点击合成
5. 下载生成的音频文件

## 🛠️ 技术栈

- [Python](https://www.python.org/) - 后端逻辑
- [Streamlit](https://streamlit.io/) - Web 界面
- [PyWebView](https://pywebview.flowrl.com/) - 桌面窗口
- [PyInstaller](https://pyinstaller.org/) - 应用打包

## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源许可证。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📧 联系

如有问题，请通过 GitHub Issues 联系。

## 免责声明

1. **本工具为第三方开源客户端**，与小米公司无任何关联，未经小米官方授权或认可。
2. **API服务由小米官方提供**，用户须自行注册小米账号并申请API密钥（Access Key）。
   本工具仅提供API调用的技术封装，不预装、不提供、不共享任何API密钥。
3. **预填的API地址**来源于小米官方公开文档，仅供技术对接参考。
   如小米官方调整接口地址，请以官方最新文档为准。
4. **内容生成责任**：TTS音频内容由小米服务器根据用户输入文本生成，
   本工具不存储、不处理、不传播任何音频数据或文本内容。
5. **用户须自行遵守**《小米开发者协议》《小米AI服务条款》及相关法律法规，
   不得将本工具用于生成违法、侵权、虚假或欺诈性内容。
   因用户违反上述规定产生的法律责任，由用户自行承担。
6. 本工具基于 MIT 许可证开源，按"现状"（AS IS）提供，作者不提供任何明示或默示的担保，包括但不限于适销性、特定用途适用性及非侵权性的默示担保。

***

<p align="center">Made with ❤️ by xiaozhanqi</p>

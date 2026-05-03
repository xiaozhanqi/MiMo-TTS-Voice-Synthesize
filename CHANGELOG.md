# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-05-03

### Added
- 首次发布 MiMo TTS 语音合成器
- 支持小米 MiMo-V2.5-TTS 系列模型
  - mimo-v2.5-tts: 预置精品音色合成
  - mimo-v2.5-tts-voicedesign: 文本描述定制音色
  - mimo-v2.5-tts-voiceclone: 音频样本复刻音色
- 多种说话风格控制
  - 基础情绪：开心、悲伤、愤怒、恐惧等
  - 复合情绪：怅然、欣慰、无奈、愧疚等
  - 方言支持：东北话、四川话、河南话、粤语
  - 唱歌模式
- 桌面应用界面
  - 基于 Streamlit 的 Web 界面
  - 基于 PyWebView 的独立桌面窗口
  - 支持 WebView2 和 MSHTML 双模式
- 自动 WebView2 Runtime 检测和安装
- 单文件便携版打包
- 浏览器回退模式（当 WebView2 不可用时）

### Features
- 🎙️ 预置音色：冰糖、茉莉、苏打、白桦、Mia、Chloe、Milo、Dean
- 🎨 音色设计：通过自然语言描述创建自定义音色
- 🎭 声音克隆：上传音频样本复刻任意声音
- 🎵 风格标签：(开心)、(悲伤)、(东北话)、(唱歌) 等
- 💻 独立桌面应用，无需浏览器
- 📦 单文件可执行程序，复制即用

### Technical
- Python 3.8+ 支持
- Streamlit 1.28+ 驱动 Web 界面
- PyWebView 4.4+ 提供桌面窗口
- PyInstaller 6.20+ 打包为独立 EXE
- 自动递归防护（解决 PyInstaller + Streamlit 进程爆炸问题）

## [Unreleased]

### Planned
- [ ] 添加更多预置音色
- [ ] 支持批量文本合成
- [ ] 音频文件管理功能
- [ ] 历史记录和收藏
- [ ] 自定义 API 地址
- [ ] 多语言界面支持

---

## 版本号说明

本项目采用 [语义化版本](https://semver.org/lang/zh-CN/)：

- **主版本号**：不兼容的 API 修改
- **次版本号**：向下兼容的功能新增
- **修订号**：向下兼容的问题修复

示例：`1.0.0` 表示第 1 个主版本的初始发布。

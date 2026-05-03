#!/usr/bin/env python3
"""
MiMo TTS 语音合成器 打包脚本（便携版）
一键打包为单文件 EXE
"""

import subprocess
import sys
import os
import shutil


def install_dependencies():
    """安装打包所需的依赖"""
    print("📦 安装打包依赖...")
    deps = ["pyinstaller", "pywebview", "pywin32" if sys.platform == "win32" else ""]
    deps = [d for d in deps if d]
    
    for dep in deps:
        subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
    
    print("✅ 依赖安装完成")


def clean_build():
    """清理之前的构建文件"""
    print("🧹 清理构建文件...")
    dirs_to_remove = ["build", "dist"]
    for dir_name in dirs_to_remove:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"  已删除: {dir_name}")
    print("✅ 清理完成")


def build_portable():
    """使用 PyInstaller 打包便携版（单文件）"""
    print("🔨 开始打包便携版...")
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--clean",
        "--noconfirm",
        "MiMoTTS_portable.spec"
    ]
    
    result = subprocess.run(cmd, capture_output=False)
    
    if result.returncode != 0:
        print("❌ 打包失败")
        sys.exit(1)
    
    print("✅ 打包完成")


def main():
    """主函数"""
    print("=" * 50)
    print("🎙️  MiMo TTS 语音合成器 便携版打包工具")
    print("=" * 50)
    print()
    
    # 检查是否在项目目录
    if not os.path.exists("src/mimo_tts_app.py"):
        print("❌ 错误: 请在项目根目录运行此脚本")
        print("   确保 src/mimo_tts_app.py 文件存在于当前目录")
        sys.exit(1)
    
    # 询问是否安装依赖
    response = input("是否安装/更新打包依赖? (y/n): ").strip().lower()
    if response == 'y':
        install_dependencies()
    
    # 清理之前的构建
    clean_build()
    
    # 打包便携版
    build_portable()
    
    print()
    print("=" * 50)
    print("🎉 打包完成!")
    print("=" * 50)
    print()
    print("📂 输出文件: dist/MiMoTTS语音合成器.exe")
    print("🚀 运行方式: 双击即可运行")
    print()
    print("💡 提示:")
    print("   - 首次运行可能需要几秒钟启动")
    print("   - 确保系统已安装 WebView2 运行时")
    print("   - Windows 10/11 通常已内置 WebView2")
    print()


if __name__ == "__main__":
    main()

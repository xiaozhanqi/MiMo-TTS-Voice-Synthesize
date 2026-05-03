#!/usr/bin/env python3
"""
MiMo TTS 语音合成器
Based on PyWebView and Chrome Engine (WebView2)
"""

import sys
import os
import subprocess
import time
import traceback
import logging

# 检测是否为 PyInstaller 打包后的环境
IS_BUNDLED = getattr(sys, 'frozen', False)

# 配置日志 - 使用 EXE 所在目录（打包后可写）
if IS_BUNDLED:
    # PyInstaller 打包后，使用 EXE 所在目录
    log_dir = os.path.dirname(sys.executable)
else:
    # 开发环境，使用脚本所在目录
    log_dir = os.path.dirname(os.path.abspath(__file__))
log_file = os.path.join(log_dir, 'desktop_app.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Configuration
STREAMLIT_PORT = 8501
STREAMLIT_HOST = "127.0.0.1"
APP_TITLE = "MiMo TTS 语音合成器"
APP_WIDTH = 1400
APP_HEIGHT = 900

# 全局标志，防止重复错误弹窗
_error_shown = False


def show_error_and_exit(title, message):
    """显示错误对话框并退出程序（防止重复弹窗）"""
    global _error_shown
    if _error_shown:
        return
    _error_shown = True
    
    logger.error(f"{title}: {message}")
    
    try:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(title, message)
        root.destroy()
    except Exception as e:
        logger.error(f"无法显示错误对话框: {e}")
        print(f"ERROR: {title}\n{message}", file=sys.stderr)
    
    sys.exit(1)


def check_dotnet_framework():
    """检查 .NET Framework 是否安装"""
    try:
        import winreg
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                r"SOFTWARE\Microsoft\NET Framework Setup\NDP\v4\Full")
            release = winreg.QueryValueEx(key, "Release")[0]
            winreg.CloseKey(key)
            if release >= 461808:  # .NET Framework 4.7.2+
                return True
        except:
            pass
    except:
        pass
    return False


def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller 打包后的临时目录
        base_path = sys._MEIPASS
    except Exception:
        # 开发环境：获取当前脚本所在目录的父目录（项目根目录）
        script_dir = os.path.dirname(os.path.abspath(__file__))
        base_path = os.path.dirname(script_dir)
    return os.path.join(base_path, relative_path)


def check_webview2_installed():
    """检查系统 WebView2 Runtime 是否已安装"""
    if sys.platform != "win32":
        return False
    try:
        # 检查 EdgeWebView 安装目录（遍历版本号）
        edge_webview_paths = [
            r"C:\Program Files (x86)\Microsoft\EdgeWebView\Application",
            r"C:\Program Files\Microsoft\EdgeWebView\Application",
        ]
        for base_path in edge_webview_paths:
            if os.path.exists(base_path):
                for item in os.listdir(base_path):
                    if item[0].isdigit():
                        exe_path = os.path.join(base_path, item, "msedgewebview2.exe")
                        if os.path.exists(exe_path):
                            logger.info(f"检测到系统 WebView2: {exe_path}")
                            os.environ['WEBVIEW2_BROWSER_EXECUTABLE_FOLDER'] = os.path.join(base_path, item)
                            return True
    except Exception:
        pass
    return False


def check_bundled_webview2():
    """检查内置的 WebView2 Runtime（webview2_runtime 目录）"""
    try:
        bundled_path = get_resource_path("webview2_runtime")
        exe_path = os.path.join(bundled_path, "msedgewebview2.exe")
        if os.path.exists(exe_path):
            logger.info(f"检测到内置 WebView2: {exe_path}")
            os.environ['WEBVIEW2_BROWSER_EXECUTABLE_FOLDER'] = bundled_path
            return True
    except Exception:
        pass
    return False


def download_webview2_runtime():
    """联网下载 WebView2 Runtime（带明确提示）"""
    import tkinter as tk
    from tkinter import messagebox

    download_url = "https://go.microsoft.com/fwlink/p/?LinkId=2124701"

    # 明确提示用户
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)

    result = messagebox.askyesno(
        "⚠️ WebView2 运行时未安装",
        "本应用需要 WebView2 运行时才能正常显示界面。\n\n"
        "系统未检测到 WebView2 Runtime，需要联网下载安装。\n\n"
        "📦 下载信息：\n"
        "  • 来源：微软官方服务器\n"
        "  • 大小：约 1.5MB（引导程序）\n"
        "  • 安装后将自动下载完整运行时\n\n"
        "是否立即下载并安装？\n\n"
        "（选择'否'将使用系统浏览器打开）",
        icon='warning'
    )
    root.destroy()

    if not result:
        logger.info("用户取消下载 WebView2 Runtime")
        return False

    # 显示下载进度提示
    progress_root = tk.Tk()
    progress_root.withdraw()
    progress_root.attributes('-topmost', True)
    messagebox.showinfo(
        "正在下载",
        "正在从微软官方服务器下载 WebView2 安装程序...\n\n"
        "请稍候，下载完成后将自动开始安装。\n\n"
        "（此过程可能需要 1-3 分钟，取决于网络速度）"
    )
    progress_root.destroy()

    try:
        import urllib.request
        import tempfile

        # 下载引导程序到临时目录
        temp_dir = tempfile.mkdtemp()
        bootstrapper_path = os.path.join(temp_dir, "MicrosoftEdgeWebview2Setup.exe")

        logger.info(f"正在下载 WebView2 引导程序: {download_url}")
        urllib.request.urlretrieve(download_url, bootstrapper_path)
        logger.info(f"下载完成: {bootstrapper_path}")

        # 显示安装提示
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        messagebox.showinfo(
            "开始安装",
            "WebView2 安装程序已下载完成。\n\n"
            "即将开始安装，请在弹出的安装窗口中等待完成。\n\n"
            "安装完成后应用将自动启动。"
        )
        root.destroy()

        # 运行安装程序
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE

        process = subprocess.Popen(
            [bootstrapper_path, "/silent", "/install"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            startupinfo=startupinfo,
        )

        logger.info("等待 WebView2 安装完成...")
        stdout, stderr = process.communicate(timeout=300)

        if process.returncode == 0:
            logger.info("WebView2 Runtime 安装成功")
            # 安装成功提示
            root = tk.Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            messagebox.showinfo(
                "✅ 安装成功",
                "WebView2 Runtime 已成功安装！\n\n"
                "应用即将启动，请稍候..."
            )
            root.destroy()
            return True
        else:
            logger.error(f"WebView2 安装失败，返回码: {process.returncode}")
            logger.error(f"stderr: {stderr.decode('utf-8', errors='ignore')}")
            # 安装失败提示
            root = tk.Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            messagebox.showerror(
                "❌ 安装失败",
                f"WebView2 Runtime 安装失败（错误码: {process.returncode}）。\n\n"
                "请尝试手动下载安装：\n"
                f"{download_url}\n\n"
                "或使用系统浏览器打开应用。"
            )
            root.destroy()
            return False

    except subprocess.TimeoutExpired:
        logger.error("WebView2 安装超时")
        process.kill()
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        messagebox.showerror(
            "❌ 安装超时",
            "WebView2 Runtime 安装超时。\n\n"
            "请检查网络连接后重试，或手动下载安装：\n"
            f"{download_url}"
        )
        root.destroy()
        return False
    except Exception as e:
        logger.error(f"下载或安装 WebView2 异常: {e}")
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        messagebox.showerror(
            "❌ 下载失败",
            f"下载或安装 WebView2 时发生错误：\n{str(e)}\n\n"
            "请手动下载安装：\n"
            f"{download_url}"
        )
        root.destroy()
        return False


def install_webview2():
    """使用内置引导程序安装 WebView2 Runtime（兼容旧接口）"""
    bootstrapper = get_resource_path("redist/MicrosoftEdgeWebview2Setup.exe")
    if not os.path.exists(bootstrapper):
        logger.error(f"WebView2 引导程序不存在: {bootstrapper}")
        return False
    
    logger.info(f"正在使用内置引导程序安装 WebView2 Runtime...")
    
    try:
        # 运行引导程序（静默安装）
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
        
        process = subprocess.Popen(
            [bootstrapper, "/silent", "/install"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            startupinfo=startupinfo,
        )
        
        # 等待安装完成（最多 5 分钟）
        logger.info("等待 WebView2 安装完成...")
        stdout, stderr = process.communicate(timeout=300)
        
        if process.returncode == 0:
            logger.info("WebView2 Runtime 安装成功")
            return True
        else:
            logger.error(f"WebView2 安装失败，返回码: {process.returncode}")
            logger.error(f"stderr: {stderr.decode('utf-8', errors='ignore')}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error("WebView2 安装超时")
        process.kill()
        return False
    except Exception as e:
        logger.error(f"WebView2 安装异常: {e}")
        return False


def start_streamlit():
    """Start Streamlit service in background"""
    mimo_app_path = get_resource_path("mimo_tts_app.py")
    
    if not os.path.exists(mimo_app_path):
        raise FileNotFoundError(f"找不到主程序文件: {mimo_app_path}")
    
    cmd = [
        sys.executable, "-m", "streamlit", "run", 
        mimo_app_path,
        "--server.headless", "true",
        "--server.port", str(STREAMLIT_PORT),
        "--server.address", STREAMLIT_HOST,
        "--browser.gatherUsageStats", "false",
    ]
    
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    # 设置环境变量标记，防止 PyInstaller 打包后的递归启动
    env["MIMO_TTS_LAUNCHER"] = "1"
    
    startupinfo = None
    if sys.platform == "win32":
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
    
    logger.info(f"启动 Streamlit: {' '.join(cmd)}")
    
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        cwd=get_resource_path("."),
        env=env,
        startupinfo=startupinfo,
        creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
    )
    
    return process


def wait_for_server(timeout=30):
    """Wait for Streamlit service to start"""
    import urllib.request
    url = f"http://{STREAMLIT_HOST}:{STREAMLIT_PORT}"
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            urllib.request.urlopen(url, timeout=1)
            logger.info(f"Streamlit 服务已启动: {url}")
            return True
        except:
            time.sleep(0.5)
    return False


def setup_webview():
    """配置 webview 环境（已由 check 函数处理，保留兼容）"""
    pass


def main():
    """Main function"""
    logger.info("=" * 50)
    logger.info("MiMo TTS 语音合成器 启动")
    logger.info(f"Python: {sys.version}")
    logger.info(f"平台: {sys.platform}")
    logger.info(f"架构: {getattr(sys, 'maxunicode', 'unknown')}")
    logger.info(f"打包模式: {IS_BUNDLED}")
    
    # PyInstaller + multiprocessing 递归防护
    # 如果是打包后的环境且环境变量已设置，说明这是 Streamlit 子进程
    if IS_BUNDLED and os.environ.get("MIMO_TTS_LAUNCHER"):
        logger.info("检测到子进程模式，直接启动 Streamlit...")
        try:
            # ★ 关键：环境变量必须在 import streamlit 之前设置
            os.environ["STREAMLIT_GLOBAL_DEVELOPMENT_MODE"] = "false"
            os.environ["STREAMLIT_SERVER_HEADLESS"] = "true"
            os.environ["STREAMLIT_BROWSER_GATHERUSAGESTATS"] = "false"
            os.environ["STREAMLIT_SERVER_ENABLE_CORS"] = "false"
            os.environ["STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION"] = "false"
            
            import streamlit.web.cli as stcli  # ← import 放在 env 设置之后
            mimo_app_path = get_resource_path("mimo_tts_app.py")
            sys.argv = [
                "streamlit", "run", mimo_app_path,
                "--server.headless", "true",
                "--server.port", str(STREAMLIT_PORT),
                "--server.address", STREAMLIT_HOST,
                "--browser.gatherUsageStats", "false",
            ]
            stcli.main()
        except Exception as e:
            logger.exception("子进程启动 Streamlit 失败")
            show_error_and_exit("启动失败", f"无法启动 Streamlit:\n{str(e)}")
        sys.exit(0)
    
    try:
        # 检查 .NET Framework (Windows)
        if sys.platform == "win32":
            if not check_dotnet_framework():
                show_error_and_exit(
                    "缺少依赖",
                    "未检测到 .NET Framework 4.7.2 或更高版本。\n"
                    "请从微软官网下载并安装最新版 .NET Framework。"
                )
        
        # 启动 Streamlit 服务（无论使用 WebView 还是浏览器都需要）
        logger.info("启动 Streamlit 服务...")
        try:
            streamlit_process = start_streamlit()
        except FileNotFoundError as e:
            show_error_and_exit("启动失败", str(e))
        except Exception as e:
            show_error_and_exit("启动失败", f"无法启动 Streamlit 服务:\n{str(e)}")
        
        # 等待服务启动
        logger.info("等待 Streamlit 服务就绪...")
        if not wait_for_server(timeout=30):
            streamlit_process.terminate()
            show_error_and_exit(
                "服务启动超时",
                "Streamlit 服务在 30 秒内未能启动。\n"
                "请检查:\n"
                "1. 端口 8501 是否被占用\n"
                "2. mimo_tts_app.py 是否存在且可运行\n"
                "3. 查看 desktop_app.log 获取详细信息"
            )
        
        # 检查 WebView2 Runtime
        logger.info("=" * 40)
        logger.info("检查 WebView2 Runtime...")
        
        # 第一步：检查系统内置 WebView2 Runtime
        logger.info("[1/3] 检查系统内置 WebView2 Runtime...")
        webview2_available = check_webview2_installed()
        if webview2_available:
            logger.info("✓ 使用系统内置 WebView2 Runtime")
        
        # 第二步：检查项目内置的 WebView2 Runtime
        if not webview2_available:
            logger.info("[2/3] 检查项目内置 WebView2 Runtime...")
            webview2_available = check_bundled_webview2()
            if webview2_available:
                logger.info("✓ 使用项目内置 WebView2 Runtime")
        
        # 第三步：尝试使用内置引导程序安装
        if not webview2_available:
            logger.info("[3/3] 尝试使用内置引导程序安装...")
            webview2_available = install_webview2()
            if webview2_available:
                logger.info("✓ 内置引导程序安装成功")
                webview2_available = check_webview2_installed()
        
        # 第四步：联网下载安装（带明确提示）
        if not webview2_available:
            logger.warning("本地 WebView2 不可用，尝试联网下载...")
            webview2_available = download_webview2_runtime()
            if webview2_available:
                logger.info("✓ 联网下载安装成功")
                webview2_available = check_webview2_installed()
        
        if not webview2_available:
            # WebView2 不可用，回退到浏览器模式
            logger.warning("WebView2 不可用，将使用浏览器模式")
            import webbrowser
            url = f"http://{STREAMLIT_HOST}:{STREAMLIT_PORT}"
            webbrowser.open(url)
            print(f"\n已在浏览器中打开: {url}")
            print("按 Ctrl+C 关闭服务...")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
            finally:
                streamlit_process.terminate()
            return
        else:
            logger.info("✓ WebView2 Runtime 已就绪")
        logger.info("=" * 40)
        
        # 导入 webview
        try:
            import webview
            logger.info(f"WebView 版本: {webview.__version__ if hasattr(webview, '__version__') else 'unknown'}")
        except ImportError as e:
            show_error_and_exit(
                "缺少依赖",
                f"无法导入 pywebview 模块。\n请运行: pip install pywebview\n错误: {e}"
            )
        except Exception as e:
            show_error_and_exit(
                "WebView 加载错误",
                f"加载 WebView 时发生错误:\n{str(e)}\n\n"
                f"可能原因:\n"
                f"1. WebView2 Runtime 未安装\n"
                f"2. 系统架构不兼容 (ARM64)\n"
                f"3. .NET Framework 损坏\n\n"
                f"请安装 WebView2 Runtime:\n"
                f"https://developer.microsoft.com/microsoft-edge/webview2/"
            )
        
        # 创建桌面窗口
        url = f"http://{STREAMLIT_HOST}:{STREAMLIT_PORT}"
        logger.info(f"创建窗口: {url}")
        
        try:
            # 检查 webview 版本是否支持 icon 参数
            import inspect
            create_window_params = inspect.signature(webview.create_window).parameters
            
            window_kwargs = {
                "title": APP_TITLE,
                "url": url,
                "width": APP_WIDTH,
                "height": APP_HEIGHT,
                "min_size": (1000, 700),
                "text_select": True,
                "confirm_close": True,
            }
            
            # 如果支持 icon 参数，尝试设置图标
            if "icon" in create_window_params:
                icon_path = get_resource_path("图标/app_icon.ico")
                if os.path.exists(icon_path):
                    window_kwargs["icon"] = icon_path
                else:
                    logger.warning("未找到应用图标")
            
            window = webview.create_window(**window_kwargs)
        except Exception as e:
            streamlit_process.terminate()
            show_error_and_exit(
                "创建窗口失败",
                f"无法创建 WebView 窗口:\n{str(e)}\n\n"
                f"可能原因:\n"
                f"1. WebView2 Runtime 未正确安装\n"
                f"2. 显卡驱动问题\n"
                f"3. 系统组件损坏"
            )
        
        # 定义清理函数
        def on_closing():
            logger.info("应用关闭，清理进程...")
            try:
                streamlit_process.terminate()
                streamlit_process.wait(timeout=5)
            except:
                try:
                    streamlit_process.kill()
                except:
                    pass
        
        window.events.closing += on_closing
        
        # 启动 WebView
        logger.info("启动 WebView...")
        
        # 检查 WebView2 是否可用（环境变量已由 check 函数设置）
        webview2_available = 'WEBVIEW2_BROWSER_EXECUTABLE_FOLDER' in os.environ
        
        if not webview2_available:
            logger.warning("未找到 WebView2 可执行文件，将使用 MSHTML 模式")
        
        gui = "edgechromium" if webview2_available else "mshtml"
        
        try:
            webview.start(
                debug=False,
                http_server=False,
                gui=gui
            )
        except Exception as e:
            logger.exception("WebView 启动失败")
            show_error_and_exit(
                "WebView 启动失败",
                f"无法启动 WebView:\n{str(e)}\n\n"
                f"请确保已安装 WebView2 Runtime:\n"
                f"https://developer.microsoft.com/microsoft-edge/webview2/"
            )
        
        logger.info("应用正常退出")
        
    except Exception as e:
        logger.exception("未处理的异常")
        show_error_and_exit(
            "运行时错误",
            f"发生未处理的异常:\n{str(e)}\n\n"
            f"详细错误信息已保存到 desktop_app.log"
        )


if __name__ == "__main__":
    main()

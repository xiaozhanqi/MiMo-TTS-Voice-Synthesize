@echo off
echo 启动 MiMo TTS 语音合成器...
echo.
echo 首次运行请先安装依赖:
echo   pip install -r requirements.txt
echo.
streamlit run src/mimo_tts_app.py
pause

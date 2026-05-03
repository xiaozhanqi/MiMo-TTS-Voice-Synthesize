import streamlit as st
import base64
import requests
from openai import OpenAI
from datetime import datetime

# ============================================================
# 页面配置
# ============================================================
st.set_page_config(
    page_title="MiMo TTS 语音合成器",
    page_icon="🔊",
    layout="centered"
)

# ============================================================
# 自定义样式
# ============================================================
st.markdown("""
<style>
@import url('
https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;700&display=swap
');

html, body, [class*="css"] {
    font-family: 'Noto Sans SC', -apple-system, sans-serif;
}
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

.app-header {
    text-align: center;
    padding: 0.5rem 0 1.5rem;
}
.app-header h1 {
    font-size: 1.8rem;
    font-weight: 700;
    background: linear-gradient(135deg, #FF6B00, #FF9040);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0;
    line-height: 1.3;
}
.app-header .sub {
    color: #aaa;
    font-size: 0.82rem;
    font-weight: 300;
    margin-top: 0.3rem;
}

.section-label {
    font-size: 0.88rem;
    font-weight: 600;
    color: #444;
    margin: 1.6rem 0 0.6rem;
    padding-left: 0.5rem;
    border-left: 3px solid #FF6B00;
    line-height: 1.4;
}
.section-label .hint {
    font-weight: 300;
    font-size: 0.75rem;
    color: #bbb;
    margin-left: 0.4rem;
}

.divider {
    height: 1px;
    background: #eee;
    margin: 1.3rem 0;
    border: none;
}

.tag-cat {
    font-size: 0.72rem;
    color: #999;
    font-weight: 500;
    margin-bottom: 0.2rem;
}

.app-footer {
    text-align: center;
    padding: 1.5rem 0 0.5rem;
    margin-top: 2rem;
    border-top: 1px solid #f0f0f0;
    color: #d0d0d0;
    font-size: 0.72rem;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# 会话状态初始化
# ============================================================
# ★ 关键：text_content 直接作为 text_area 的 key，不要另起名字
if "text_content" not in st.session_state:
    st.session_state.text_content = ""
if "active_tags" not in st.session_state:
    st.session_state.active_tags = set()
if "generated" not in st.session_state:
    st.session_state.generated = False
if "api_mode" not in st.session_state:
    st.session_state.api_mode = "mimoplan"
if "audio_data" not in st.session_state:
    st.session_state.audio_data = None
if "filename" not in st.session_state:
    st.session_state.filename = ""

# ============================================================
# 标签定义
# ============================================================
TAG_GROUPS = [
    ("😊 情感", {
        "开心": "(开心)", "悲伤": "(悲伤)", "温柔": "(温柔)",
        "慵懒": "(慵懒)", "愤怒": "(愤怒)", "惊讶": "(惊讶)",
    }),
    ("🗣️ 方言", {
        "东北话": "(东北话)", "粤语": "(粤语)", "四川话": "(四川话)",
    }),
    ("🎵 风格", {
        "唱歌": "(唱歌)", "耳语": "(耳语)",
    }),
    ("🔊 音效", {
        "笑": "[笑]", "叹气": "[叹气]", "吸气": "[吸气]",
    }),
]


# ---- 回调函数（on_click 在脚本重跑之前执行，所以改 session_state 是安全的）----
def toggle_tag(name, tag_text):
    """★ 必须用 on_click 回调，不能用 if st.button 后调用"""
    cur = st.session_state.text_content
    if name in st.session_state.active_tags:
        st.session_state.active_tags.discard(name)
        st.session_state.text_content = cur.replace(tag_text, "")
    else:
        st.session_state.active_tags.add(name)
        st.session_state.text_content = cur + tag_text


def clear_all():
    st.session_state.text_content = ""
    st.session_state.active_tags = set()
    st.session_state.generated = False
    st.session_state.audio_data = None
    st.session_state.filename = ""


def set_mode(mode):
    st.session_state.api_mode = mode


# ============================================================
# 侧边栏
# ============================================================
with st.sidebar:
    st.markdown("### ⚙️ API 接入方式")

    mc1, mc2 = st.columns(2)
    current = st.session_state.api_mode

    with mc1:
        plan_active = current == "mimoplan"
        plan_border = "#FF6B00" if plan_active else "#eee"
        plan_bg = "#FFF7F0" if plan_active else "#fff"
        st.markdown(f"""
        <div style="border:2px solid {plan_border};border-radius:10px;
             padding:0.7rem 0.5rem;text-align:center;background:{plan_bg};">
            <div style="font-size:1.4rem;">🪙</div>
            <div style="font-size:0.82rem;font-weight:600;color:#333;">MiMo Plan</div>
            <div style="font-size:0.65rem;color:#aaa;">按量计费</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button(
            "✓ 已选择" if plan_active else "切换到此",
            key="btn_plan", use_container_width=True,
            type="primary" if plan_active else "secondary",
            on_click=set_mode, args=("mimoplan",),
        ):
            pass

    with mc2:
        key_active = current == "apikey"
        key_border = "#FF6B00" if key_active else "#eee"
        key_bg = "#FFF7F0" if key_active else "#fff"
        st.markdown(f"""
        <div style="border:2px solid {key_border};border-radius:10px;
             padding:0.7rem 0.5rem;text-align:center;background:{key_bg};">
            <div style="font-size:1.4rem;">🔑</div>
            <div style="font-size:0.82rem;font-weight:600;color:#333;">API Key</div>
            <div style="font-size:0.65rem;color:#aaa;">自有密钥</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button(
            "✓ 已选择" if key_active else "切换到此",
            key="btn_key", use_container_width=True,
            type="primary" if key_active else "secondary",
            on_click=set_mode, args=("apikey",),
        ):
            pass

    st.markdown("---")

    if current == "mimoplan":
        st.markdown("##### 🪙 MiMo Plan 配置")
        mimoplan_token = st.text_input(
            "Plan Token", type="password", placeholder="mimo-plan-...",
            help="在 MiMo Plan 控制台获取的 Plan Token", key="mimoplan_token",
        )
        mimoplan_endpoint = st.text_input(
            "接口地址",
            value="https://token-plan-cn.xiaomimimo.com/v1",
            key="mimoplan_endpoint",
        )
        st.markdown("""
        <div style="background:#F0F7FF;border-radius:8px;padding:0.6rem 0.8rem;
             font-size:0.72rem;color:#556;line-height:1.5;margin-top:0.5rem;">
        <b>💡 MiMo Plan 说明</b><br>
        • 无需自备 API Key，按调用量计费<br>
        • 在控制台开通 Plan 并获取 Token<br>
        • 支持所有模型与音色
        </div>
        """, unsafe_allow_html=True)
        api_key_resolved = mimoplan_token
        base_url = mimoplan_endpoint
    else:
        st.markdown("##### 🔑 API Key 配置")
        api_key_input = st.text_input(
            "API Key", type="password", placeholder="sk-...",
            help="从 platform.xiaomimimo.com 获取", key="apikey_input",
        )
        api_endpoint = st.text_input(
            "接口地址", value="https://api.xiaomimimo.com/v1", key="api_endpoint",
        )
        st.markdown("""
        <div style="background:#FFF8F0;border-radius:8px;padding:0.6rem 0.8rem;
             font-size:0.72rem;color:#554;line-height:1.5;margin-top:0.5rem;">
        <b>💡 API Key 说明</b><br>
        • 使用自有 API Key 调用，独立计费<br>
        • 支持 OpenAI 兼容接口格式<br>
        • 可搭配自建代理地址使用
        </div>
        """, unsafe_allow_html=True)
        api_key_resolved = api_key_input
        base_url = api_endpoint

    st.markdown("---")
    st.markdown("### 📖 使用帮助")
    st.markdown("""
**风格标签**（直接写入文本）：

| 类型 | 标签 |
|---|---|
| 情感 | `(开心)` `(悲伤)` `(温柔)` `(慵懒)` |
| 方言 | `(东北话)` `(粤语)` `(四川话)` |
| 风格 | `(唱歌)` `(耳语)` |
| 音效 | `[笑]` `[叹气]` `[吸气]` |

**风格指令**：用自然语言描述说话风格。

**VoiceDesign**：选择该模型后，通过文字描述自定义音色。
    """)

# ============================================================
# 主区域 — 标题
# ============================================================
st.markdown("""
<div class="app-header">
    <h1>🔊 MiMo TTS 语音合成器</h1>
    <div class="sub">基于小米 MiMo-V2.5 · 语音合成</div>
</div>
""", unsafe_allow_html=True)

mode_label = "🪙 MiMo Plan" if st.session_state.api_mode == "mimoplan" else "🔑 API Key"
mode_color = "#E8F5E9" if st.session_state.api_mode == "mimoplan" else "#FFF3E0"
mode_border = "#81C784" if st.session_state.api_mode == "mimoplan" else "#FFB74D"
st.markdown(f"""
<div style="display:inline-block;background:{mode_color};border:1px solid {mode_border};
     border-radius:20px;padding:0.2rem 0.9rem;font-size:0.75rem;font-weight:500;color:#555;">
    当前接入方式：{mode_label}
</div>
""", unsafe_allow_html=True)

# ============================================================
# ① 模型配置
# ============================================================
st.markdown('<div class="section-label">模型配置</div>', unsafe_allow_html=True)

# ---- 模型选择 ----
model = st.selectbox(
    "选择模型",
    ["mimo-v2.5-tts", "mimo-v2.5-tts-voicedesign", "mimo-v2.5-tts-voiceclone"],
    format_func=lambda x: {
        "mimo-v2.5-tts": "🎙️ 预置音色",
        "mimo-v2.5-tts-voicedesign": "✨ 音色设计",
        "mimo-v2.5-tts-voiceclone": "🎭 音色克隆"
    }.get(x, x)
)

# ---- 根据模型显示不同的音色配置面板 ----
if model == "mimo-v2.5-tts":
    # 预置音色模型
    col_voice, col_fmt = st.columns([3, 1])
    with col_voice:
        voice = st.selectbox(
            "选择音色",
            ["冰糖", "茉莉", "苏打", "白桦", "Mia", "Chloe", "Milo", "Dean"],
            help="选择内置的精品音色"
        )
    with col_fmt:
        audio_format = st.selectbox("音频格式", ["wav", "mp3"])
    voice_desc = None
    voice_clone_base64 = None
    
elif model == "mimo-v2.5-tts-voicedesign":
    # 音色设计模型
    st.markdown("""
    <div style="background:#F0F7FF;border-radius:8px;padding:0.8rem 1rem;margin:0.5rem 0;">
        <div style="font-size:0.85rem;color:#333;font-weight:500;">✨ 通过文本描述定制音色</div>
        <div style="font-size:0.75rem;color:#666;margin-top:0.3rem;">
            描述越具体，生成的音色越贴近预期。建议包含：性别、年龄、音色质感、说话风格等
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col_desc, col_fmt = st.columns([3, 1])
    with col_desc:
        voice_desc = st.text_input(
            "音色描述",
            placeholder="例如：温柔的女声，像电台主持人一样，带有一点点磁性",
            key="voice_desc",
            help="描述你想要的音色特征"
        )
    with col_fmt:
        audio_format = st.selectbox("音频格式", ["wav", "mp3"])
    voice = None
    voice_clone_base64 = None
    
else:  # mimo-v2.5-tts-voiceclone
    # 音色克隆模型
    st.markdown("""
    <div style="background:#FFF3E0;border-radius:8px;padding:0.8rem 1rem;margin:0.5rem 0;">
        <div style="font-size:0.85rem;color:#333;font-weight:500;">🎭 上传音频样本复刻音色</div>
        <div style="font-size:0.75rem;color:#666;margin-top:0.3rem;">
            支持 wav 和 mp3 格式，音频文件大小不超过 10MB。样本质量越高，复刻效果越好。
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col_upload, col_fmt = st.columns([3, 1])
    with col_upload:
        voice_clone_file = st.file_uploader(
            "上传音频样本",
            type=["wav", "mp3"],
            help="上传音频样本以复刻音色"
        )
    with col_fmt:
        audio_format = st.selectbox("音频格式", ["wav", "mp3"])
    
    voice_clone_base64 = None
    voice_desc = None
    voice = None
    
    if voice_clone_file is not None:
        # 将上传的文件转换为 base64
        voice_bytes = voice_clone_file.read()
        voice_base64 = base64.b64encode(voice_bytes).decode("utf-8")
        mime_type = "audio/wav" if voice_clone_file.name.endswith(".wav") else "audio/mpeg"
        voice_clone_base64 = f"data:{mime_type};base64,{voice_base64}"
        st.success(f"✅ 已上传: {voice_clone_file.name} ({len(voice_bytes)/1024:.1f} KB)")

# ============================================================
# ② 合成文本
# ============================================================
st.markdown('<div class="section-label">合成文本</div>', unsafe_allow_html=True)

style_instruction = st.text_input(
    "风格指令（可选）",
    placeholder="例如：用温柔的语气说话、像新闻主播一样播报",
    help="给模型的自然语言风格指导，留空则不使用",
)

# ★★★ 核心修复：key="text_content"，不设 value，让 Streamlit 自动同步 ★★★
st.text_area(
    "文本内容",
    height=150,
    placeholder=(
        "在这里输入要合成的文本……\n\n"
        "示例：\n"
        "  (开心)你好呀，今天天气真好！\n"
        "  (东北话)哥们儿，整点啥？\n"
        "  [笑]哈哈哈，太好笑了！"
    ),
    key="text_content",          # ← 直接绑定 session_state.text_content
    label_visibility="collapsed",
)
# 不需要手动同步！key 绑定后，widget 的值自动写入 session_state

if st.session_state.text_content:
    st.caption(f"📝 {len(st.session_state.text_content)} 字")

# ============================================================
# ③ 快捷标签
# ============================================================
st.markdown(
    '<div class="section-label">快捷标签<span class="hint">点击插入到文本末尾，再次点击移除</span></div>',
    unsafe_allow_html=True,
)

for group_name, tags in TAG_GROUPS:
    st.markdown(f'<div class="tag-cat">{group_name}</div>', unsafe_allow_html=True)
    tag_cols = st.columns(len(tags))
    for idx, (name, tag_text) in enumerate(tags.items()):
        with tag_cols[idx]:
            active = name in st.session_state.active_tags
            # ★★★ 核心修复：用 on_click 回调，不用 if st.button() ★★★
            st.button(
                f"{'● ' if active else ''}{name}",
                key=f"tag_{name}",
                on_click=toggle_tag,              # ← 回调在 rerun 前执行
                args=(name, tag_text),             # ← 传参给回调
                use_container_width=True,
                type="primary" if active else "secondary",
            )

if st.session_state.active_tags:
    st.caption(f"✓ 已启用: {' · '.join(st.session_state.active_tags)}")

# ============================================================
# ④ 操作按钮
# ============================================================
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

col_gen, col_clr, _ = st.columns([2, 2, 4])
with col_gen:
    generate = st.button("🎵 开始合成", type="primary", use_container_width=True)
with col_clr:
    # ★ clear_all 也用 on_click，保证在 widget 渲染前清空
    st.button("🗑️ 清空全部", on_click=clear_all, use_container_width=True)

# ============================================================
# ⑤ 合成逻辑
# ============================================================
if generate:
    text = st.session_state.text_content.strip()

    if not api_key_resolved:
        mode_hint = "MiMo Plan Token" if st.session_state.api_mode == "mimoplan" else "API Key"
        st.error(f"请先在左侧侧边栏输入 {mode_hint}")
    elif not text:
        st.error("请输入要合成的文本")
    else:
        with st.spinner("🎙️ 正在合成语音，请稍候……"):
            try:
                # ---- VoiceClone 模型：需要上传音频样本 ----
                if model == "mimo-v2.5-tts-voiceclone":
                    if not voice_clone_base64:
                        st.error("请先上传音频样本（wav 或 mp3 格式）")
                        st.stop()
                    
                    messages = [
                        {"role": "user", "content": style_instruction.strip() if style_instruction else ""},
                        {"role": "assistant", "content": text},
                    ]
                    audio_payload = {
                        "format": audio_format,
                        "voice": voice_clone_base64,
                    }
                
                # ---- VoiceDesign 模型：音色描述放在 user 消息中 ----
                elif model == "mimo-v2.5-tts-voicedesign":
                    current_voice_desc = st.session_state.get("voice_desc", "")
                    # 音色描述 + 风格指令 合并到 user 消息
                    voice_design_prompt = current_voice_desc or "自然流畅的声音"
                    if style_instruction.strip():
                        voice_design_prompt += f"，{style_instruction.strip()}"
                    
                    messages = [
                        {"role": "user", "content": voice_design_prompt},
                        {"role": "assistant", "content": text},
                    ]
                    audio_payload = {"format": audio_format}
                
                # ---- 普通 TTS 模型：使用预置音色 ----
                else:
                    user_content = style_instruction.strip() if style_instruction else ""
                    messages = [
                        {"role": "user", "content": user_content},
                        {"role": "assistant", "content": text},
                    ]
                    audio_payload = {"voice": voice, "format": audio_format}

                # ---- 使用 requests 直接请求（所有模型）----
                payload = {
                    "model": model,
                    "messages": messages,
                    "audio": audio_payload,
                }

                resp = requests.post(
                    f"{base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key_resolved}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                    timeout=60,
                )
                resp.raise_for_status()
                result = resp.json()

                # ---- 解析音频 ----
                choices = result.get("choices", [])
                if choices and choices[0].get("message", {}).get("audio"):
                    audio_data = base64.b64decode(choices[0]["message"]["audio"]["data"])
                    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                    prefix = "voicedesign" if "voicedesign" in model else voice
                    filename = f"mimo_tts_{prefix}_{ts}.{audio_format}"

                    st.session_state.audio_data = audio_data
                    st.session_state.filename = filename
                    st.session_state.generated = True
                    st.rerun()
                else:
                    st.error("API 未返回音频数据，请检查文本或参数")

            except requests.HTTPError as e:
                st.error(f"请求失败 ({e.response.status_code}): {e.response.text}")
            except Exception as e:
                st.error(f"合成失败: {e}")

# ============================================================
# ⑥ 结果展示
# ============================================================
if st.session_state.get("generated") and st.session_state.audio_data:
    st.markdown('<div class="section-label">合成结果</div>', unsafe_allow_html=True)

    col_player, col_meta = st.columns([3, 1])
    with col_player:
        fmt = st.session_state.filename.split(".")[-1]
        st.audio(st.session_state.audio_data, format=f"audio/{fmt}")
    with col_meta:
        size_kb = len(st.session_state.audio_data) / 1024
        st.markdown(f"**`{st.session_state.filename}`**")
        st.caption(f"{size_kb:.1f} KB · {fmt.upper()}")
        st.download_button(
            "⬇️ 下载音频", data=st.session_state.audio_data,
            file_name=st.session_state.filename,
            mime=f"audio/{fmt}", use_container_width=True, type="primary",
        )

# ============================================================
# 底部
# ============================================================
st.markdown(
    '<div class="app-footer">Powered by 小米 MiMo-V2.5 · 非官方工具</div>',
    unsafe_allow_html=True,
)
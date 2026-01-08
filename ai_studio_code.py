import streamlit as st
import yt_dlp
import google.generativeai as genai
import os
import time
import random
import glob
from urllib.parse import urlparse # <-- هذا هو السطر الذي كان ينقصك وغالباً سبب المشكلة

# ---------------------------------------------------------
# 1. THE DARK HACKER UI STYLE
# ---------------------------------------------------------
st.set_page_config(
    page_title="GOD MODE Downloader",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'JetBrains Mono', monospace;
        background-color: #0d1117;
        color: #c9d1d9;
    }

    .stApp {
        background-image: radial-gradient(circle at 50% 50%, #161b22 0%, #0d1117 100%);
    }

    .terminal-box {
        background-color: #000;
        border: 1px solid #3fb950;
        padding: 20px;
        border-radius: 5px;
        box-shadow: 0 0 20px rgba(63, 185, 80, 0.2);
        font-family: 'Courier New', monospace;
    }
    
    .stButton>button {
        width: 100%;
        background: transparent;
        border: 2px solid #3fb950;
        color: #3fb950;
        font-weight: bold;
        text-transform: uppercase;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background: #3fb950;
        color: #000;
        box-shadow: 0 0 15px #3fb950;
    }

    .stTextInput>div>div>input {
        background-color: #0d1117;
        color: #58a6ff;
        border: 1px solid #30363d;
    }
    
    h1, h2, h3 { color: #f0f6fc !important; }
    </style>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. CONFIG & API
# ---------------------------------------------------------
api_key = "AIzaSyCb9L2p7XOp3B5AVoWZZjVoDGgN7PKDZiE"
genai.configure(api_key=api_key)

def get_best_model():
    """Auto-detect the strongest available AI model"""
    try:
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        for m in models:
            if 'gemini-1.5-pro' in m: return m
        for m in models:
            if 'flash' in m: return m
        return 'models/gemini-1.5-flash'
    except:
        return 'models/gemini-pro'

# ---------------------------------------------------------
# 3. THE GOD-MODE ENGINE (Back-end)
# ---------------------------------------------------------

def get_god_mode_options(referer=None, use_cookies=False):
    """
    Configuration updated to bypass 'strict-origin-when-cross-origin'
    """
    
    # قائمة هويات متصفحات حديثة
    agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15',
    ]
    
    # إعدادات الترويسات الأساسية
    headers = {
        'User-Agent': random.choice(agents),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Dest': 'document',
    }
    
    # ---------------------------------------------------------
    # تجاوز سياسة Cross-Origin
    # ---------------------------------------------------------
    if referer:
        # 1. نرسل الرابط الكامل في Referer
        headers['Referer'] = referer
        
        # 2. نستخرج الدومين الرئيسي فقط لنضعه في Origin
        try:
            parsed_uri = urlparse(referer)
            origin = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
            headers['Origin'] = origin
            # تحديث وضع الجلب ليناسب الطلب الخارجي
            headers['Sec-Fetch-Site'] = 'cross-site'
        except:
            pass # في حال كان الرابط غير صالح نتجاهل الخطأ

    opts = {
        # --- Stealth & Bypass ---
        'quiet': True,
        'no_warnings': True,
        'ignoreerrors': True,
        'nocheckcertificate': True,
        'geo_bypass': True,
        'http_headers': headers,
        
        # --- Network Resilience ---
        'socket_timeout': 30,
        'retries': float('inf'),
        'fragment_retries': float('inf'),
        
        # --- Output Config ---
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'restrictfilenames': True,
        
        # --- HLS Options ---
        'concurrent_fragment_downloads': 8,
        'hls_use_mpegts': True,
    }

    if use_cookies:
        opts['cookiesfrombrowser'] = ('chrome', 'edge')

    return opts

def execute_download(url, type='video', referer=None, use_cookies=False):
    """The Executor Function"""
    
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    
    opts = get_god_mode_options(referer, use_cookies)
    
    if type == 'audio':
        opts['format'] = 'bestaudio/best'
        opts['postprocessors'] = [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192'}]
    else:
        opts['format'] = 'bestvideo+bestaudio/best'
        opts['merge_output_format'] = 'mp4'

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            if type == 'audio':
                filename = os.path.splitext(filename)[0] + '.mp3'
            elif type == 'video' and opts.get('merge_output_format') == 'mp4':
                filename = os.path.splitext(filename)[0] + '.mp4'
                
            return filename, info.get('title', 'Unknown')
    except Exception as e:
        raise Exception(f"GOD MODE FAILED: {str(e)}")

def analyze_intelligence(file_path, model_name):
    audio_file = genai.upload_file(path=file_path)
    while audio_file.state.name == "PROCESSING":
        time.sleep(1)
        audio_file = genai.get_file(audio_file.name)
        
    model = genai.GenerativeModel(model_name)
    prompt = """
    SYSTEM OVERRIDE: Analyze this media stream.
    1. DECODE: Provide a comprehensive summary.
    2. EXTRACT: List key entities (people, dates, hidden details).
    3. TRANSCRIPT: Verbatim text log with timestamps [MM:SS].
    """
    response = model.generate_content([prompt, audio_file])
    return response.text

# ---------------------------------------------------------
# 4. THE COMMAND CENTER (Frontend)
# ---------------------------------------------------------

with st.sidebar:
    st.header("⚡ SYSTEM CONTROLS")
    
    st.markdown("### 🛡️ Bypass Protocols")
    use_cookies = st.checkbox("Inject Browser Cookies", help="Bypass Age-gating & Login walls")
    referer_spoof = st.text_input("Spoof Referer URL", placeholder="https://locked-site.com/watch")
    
    st.divider()
    model_status = get_best_model()
    st.caption(f"AI Core: {model_status}")

st.title("⚡ GOD MODE DOWNLOADER")
st.markdown("The Ultimate Tool for Extraction & Analysis. No Barriers.")

# Input Matrix
col_in1, col_in2 = st.columns([3, 1])
with col_in1:
    target_url = st.text_input("TARGET URL / M3U8 STREAM", placeholder="Paste any link here...", label_visibility="collapsed")
with col_in2:
    mode = st.selectbox("OPERATION MODE", ["Video Extraction", "Audio Extraction", "AI Analysis"], label_visibility="collapsed")

# Action Button
if st.button("🚀 INITIATE SEQUENCE"):
    if not target_url:
        st.error("NO TARGET DETECTED.")
    else:
        status_box = st.status("🚀 INITIALIZING GOD MODE...", expanded=True)
        try:
            # 1. DOWNLOAD PHASE
            status_box.write("Attacking Stream / Bypassing Headers...")
            file_type = 'audio' if mode == 'Audio Extraction' else 'video'
            
            if mode == 'AI Analysis': file_type = 'audio'
            
            file_path, title = execute_download(target_url, file_type, referer_spoof, use_cookies)
            status_box.write(f"✅ Payload Secured: {title}")
            
            # 2. OPERATION PHASE
            if mode == 'AI Analysis':
                status_box.write("Uploading to Neural Core...")
                report = analyze_intelligence(file_path, model_status)
                status_box.update(label="MISSION COMPLETE", state="complete", expanded=False)
                
                st.subheader("📝 INTELLIGENCE REPORT")
                st.markdown(f'<div class="terminal-box">{report}</div>', unsafe_allow_html=True)
                st.download_button("DOWNLOAD REPORT", report, file_name=f"{title}_REPORT.md")
                
            else:
                status_box.update(label="DOWNLOAD COMPLETE", state="complete", expanded=False)
                with open(file_path, "rb") as f:
                    mime = "audio/mpeg" if file_type == 'audio' else "video/mp4"
                    st.success(f"FILE READY: {os.path.basename(file_path)}")
                    st.download_button(f"💾 SAVE {mode.split()[0].upper()}", f, file_name=os.path.basename(file_path), mime=mime)
            
        except Exception as e:
            status_box.update(label="SYSTEM FAILURE", state="error")
            st.error(f"CRITICAL ERROR: {str(e)}")
            if "403" in str(e):
                st.info("💡 HINT: Server rejected the request. Try pasting the website link in 'Spoof Referer URL' sidebar.")
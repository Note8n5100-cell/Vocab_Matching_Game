# -*- coding: utf-8 -*-
r"""
國小一年級中英單字連連看小遊戲
------------------------------------------
功能：
1. 中英文單字連連看遊戲（點選左邊中文、右邊英文，配對正確會消除）
2. 可自訂單字（含圖案 emoji），並儲存在 D:\vocab_game\words.json
3. 具備英文單字發音（使用 gTTS 產生語音檔，快取在 D:\vocab_game\audio）
4. 點選英文單字後，該按鈕會持續變色閃爍，並反覆播放該單字發音，
   直到配對成功或重新選擇為止
5. 配對正確會有拍手鼓掌音效；配對錯誤畫面會震動一下

執行方式：
    1. 安裝套件： pip install -r requirements.txt
       （需要 streamlit >= 1.36，因為用到 st.container(key=...) 功能）
    2. 執行程式： streamlit run vocab_matching_game.py

注意：
    - 本程式預設把單字資料與語音檔存放在 D 槽（D:\vocab_game）。
      若電腦沒有 D 槽（例如 Mac / Linux，或 Windows 只有 C 槽），
      程式會自動改存到目前資料夾底下的 vocab_game 資料夾，並顯示提示訊息。
    - 語音使用 gTTS（Google 文字轉語音），產生語音檔時需要能連上網路，
      但同一個單字只需下載一次，之後會使用快取檔案，不用重複連網。
    - 拍手音效與畫面震動使用瀏覽器內建的 Web Audio / CSS 動畫技術產生，
      不需要額外下載任何音效檔。
"""

import streamlit as st
import streamlit.components.v1 as components
import json
import os
import random
import base64
import time
import glob

# ---------------------------------------------------------------------------
# 1. 資料夾與檔案路徑設定
# ---------------------------------------------------------------------------

def get_data_dir():
    """優先使用 D:\\vocab_game，若不可用則退回目前資料夾底下的 vocab_game。"""
    preferred = r"D:\vocab_game"
    try:
        os.makedirs(preferred, exist_ok=True)
        test_file = os.path.join(preferred, ".write_test")
        with open(test_file, "w") as f:
            f.write("ok")
        os.remove(test_file)
        return preferred, True
    except Exception:
        fallback = os.path.join(os.getcwd(), "vocab_game")
        os.makedirs(fallback, exist_ok=True)
        return fallback, False


DATA_DIR, USING_D_DRIVE = get_data_dir()
AUDIO_DIR = os.path.join(DATA_DIR, "audio")
os.makedirs(AUDIO_DIR, exist_ok=True)

DEFAULT_WORDS_FILENAME = "words.json"


def compute_words_file(data_dir: str, filename: str) -> str:
    return os.path.join(data_dir, filename)


def apply_words_filename(filename: str):
    """切換目前要使用的單字檔（例如 words1.json、words2.json...）。"""
    global WORDS_FILE
    filename = filename.strip()
    if not filename.lower().endswith(".json"):
        filename += ".json"
    st.session_state.words_filename = filename
    WORDS_FILE = compute_words_file(DATA_DIR, filename)


# 沿用使用者之前選擇的單字檔檔名
if "words_filename" not in st.session_state:
    st.session_state.words_filename = DEFAULT_WORDS_FILENAME
WORDS_FILE = compute_words_file(DATA_DIR, st.session_state.words_filename)

# ---------------------------------------------------------------------------
# 2. 預設單字（國小一年級常見詞彙，含圖案）
# ---------------------------------------------------------------------------

DEFAULT_WORDS = [
    {"en": "apple", "zh": "蘋果", "icon": "🍎"},
    {"en": "banana", "zh": "香蕉", "icon": "🍌"},
    {"en": "cat", "zh": "貓", "icon": "🐱"},
    {"en": "dog", "zh": "狗", "icon": "🐶"},
    {"en": "bird", "zh": "鳥", "icon": "🐦"},
    {"en": "fish", "zh": "魚", "icon": "🐟"},
    {"en": "egg", "zh": "蛋", "icon": "🥚"},
    {"en": "milk", "zh": "牛奶", "icon": "🥛"},
    {"en": "book", "zh": "書", "icon": "📖"},
    {"en": "pen", "zh": "筆", "icon": "🖊️"},
    {"en": "bag", "zh": "書包", "icon": "🎒"},
    {"en": "red", "zh": "紅色", "icon": "🟥"},
    {"en": "blue", "zh": "藍色", "icon": "🟦"},
    {"en": "yellow", "zh": "黃色", "icon": "🟨"},
    {"en": "one", "zh": "一", "icon": "1️⃣"},
    {"en": "two", "zh": "二", "icon": "2️⃣"},
]

# 常見單字的圖案猜測表（使用者新增單字時若不填圖案，會嘗試自動比對）
ICON_GUESS = {w["en"].lower(): w["icon"] for w in DEFAULT_WORDS}
ICON_GUESS.update({
    "three": "3️⃣", "four": "4️⃣", "five": "5️⃣",
    "green": "🟩", "black": "⬛", "white": "⬜",
    "water": "💧", "sun": "☀️", "moon": "🌙", "star": "⭐",
    "ball": "⚽", "car": "🚗", "house": "🏠", "tree": "🌳",
    "happy": "😀", "sad": "😢",
})
DEFAULT_ICON = "🔤"


def guess_icon(en_word: str) -> str:
    return ICON_GUESS.get(en_word.strip().lower(), DEFAULT_ICON)


def load_words():
    words = None
    if os.path.exists(WORDS_FILE):
        try:
            with open(WORDS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list) and len(data) > 0:
                words = data
        except Exception:
            pass
    if words is None:
        words = [dict(w) for w in DEFAULT_WORDS]
        save_words(words)
        return words

    # 相容舊資料：補上缺少的 icon 欄位
    changed = False
    for w in words:
        if "icon" not in w or not w["icon"]:
            w["icon"] = guess_icon(w.get("en", ""))
            changed = True
    if changed:
        save_words(words)
    return words


def save_words(words):
    with open(WORDS_FILE, "w", encoding="utf-8") as f:
        json.dump(words, f, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# 3. 語音與音效相關函式
# ---------------------------------------------------------------------------

def get_audio_path(english_word: str):
    """回傳該英文單字的 mp3 路徑，若不存在則用 gTTS 產生並快取。"""
    safe_name = "".join(c for c in english_word.lower() if c.isalnum()) or "word"
    path = os.path.join(AUDIO_DIR, f"{safe_name}.mp3")
    if not os.path.exists(path):
        try:
            from gtts import gTTS
            tts = gTTS(text=english_word, lang="en")
            tts.save(path)
        except Exception as e:
            st.warning(f"無法產生「{english_word}」的發音檔（需要網路連線）：{e}")
            return None
    return path


def audio_file_to_data_uri(path: str):
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    return f"data:audio/mp3;base64,{b64}"


def play_single_audio(english_word: str, loop: bool = False, comp_key: str = None):
    """播放單一單字發音；loop=True 時會不斷重複播放（用於選取中的英文按鈕）。"""
    path = get_audio_path(english_word)
    if not path:
        return
    uri = audio_file_to_data_uri(path)
    loop_attr = "loop" if loop else ""
    html = f"""
    <audio autoplay {loop_attr}>
        <source src="{uri}" type="audio/mp3">
    </audio>
    """
    components.html(html, height=0)


def play_sequence_audio(english_words):
    """依序連續播放多個單字的發音（清單/整回合的全部發音）。"""
    uris = []
    for w in english_words:
        path = get_audio_path(w)
        if path:
            uris.append(audio_file_to_data_uri(path))
    if not uris:
        return
    uris_js_array = ",".join(f'"{u}"' for u in uris)
    html = f"""
    <script>
        const sources = [{uris_js_array}];
        let idx = 0;
        const player = new Audio();
        function playNext() {{
            if (idx < sources.length) {{
                player.src = sources[idx];
                player.play();
                idx += 1;
            }}
        }}
        player.addEventListener('ended', playNext);
        playNext();
    </script>
    """
    components.html(html, height=0)


def play_applause_sound():
    """用 Web Audio API 合成拍手鼓掌聲，不需要外部音效檔。"""
    html = """
    <script>
    (function(){
        try {
            var Ctx = window.AudioContext || window.webkitAudioContext;
            var ctx = new Ctx();
            function clapBurst(startTime){
                var bufferSize = Math.floor(ctx.sampleRate * 0.15);
                var buffer = ctx.createBuffer(1, bufferSize, ctx.sampleRate);
                var data = buffer.getChannelData(0);
                for (var i = 0; i < bufferSize; i++){
                    data[i] = (Math.random() * 2 - 1) * Math.exp(-3 * i / bufferSize);
                }
                var noise = ctx.createBufferSource();
                noise.buffer = buffer;
                var filter = ctx.createBiquadFilter();
                filter.type = 'bandpass';
                filter.frequency.value = 1500;
                var gainNode = ctx.createGain();
                gainNode.gain.value = 0.9;
                noise.connect(filter);
                filter.connect(gainNode);
                gainNode.connect(ctx.destination);
                noise.start(startTime);
            }
            var now = ctx.currentTime;
            clapBurst(now);
            clapBurst(now + 0.12);
            clapBurst(now + 0.26);
            clapBurst(now + 0.42);
            clapBurst(now + 0.58);
        } catch (e) { console.log(e); }
    })();
    </script>
    """
    components.html(html, height=0)


def trigger_wrong_shake():
    """讓整個頁面震動一下，提示配對錯誤（透過操作父層 DOM 實作）。"""
    html = """
    <script>
    (function(){
        try {
            var doc = window.parent.document;
            if (!doc.getElementById('shake-style')) {
                var style = doc.createElement('style');
                style.id = 'shake-style';
                style.innerHTML =
                    '@keyframes shake-anim {' +
                    '0% { transform: translate(0,0); }' +
                    '20% { transform: translate(-10px,0); }' +
                    '40% { transform: translate(10px,0); }' +
                    '60% { transform: translate(-8px,0); }' +
                    '80% { transform: translate(8px,0); }' +
                    '100% { transform: translate(0,0); }' +
                    '}' +
                    '.shake-active { animation: shake-anim 0.4s; }';
                doc.head.appendChild(style);
            }
            var body = doc.body;
            body.classList.remove('shake-active');
            void body.offsetWidth;
            body.classList.add('shake-active');
            setTimeout(function(){ body.classList.remove('shake-active'); }, 450);
        } catch (e) { console.log(e); }
    })();
    </script>
    """
    components.html(html, height=0)


def render_flash_css(container_key: str):
    """讓指定 container(key=...) 內的按鈕持續變換顏色（彩虹閃爍動畫）。"""
    css = f"""
    <style>
    @keyframes rainbow-flash {{
        0%   {{ background-color: #ff6b6b; }}
        20%  {{ background-color: #ffb84d; }}
        40%  {{ background-color: #ffe14d; }}
        60%  {{ background-color: #6bdc6b; }}
        80%  {{ background-color: #6bb8ff; }}
        100% {{ background-color: #ff6b6b; }}
    }}
    .st-key-{container_key} button {{
        animation: rainbow-flash 1.2s linear infinite;
        color: #ffffff !important;
        font-weight: bold !important;
        border: none !important;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# 4. Streamlit 頁面設定
# ---------------------------------------------------------------------------

st.set_page_config(page_title="中英單字連連看", page_icon="🎮", layout="wide")

st.title("🎮 國小一年級中英單字連連看")
st.caption(f"單字與發音檔存放於：{DATA_DIR}")

# 初始化 session_state
if "words" not in st.session_state:
    st.session_state.words = load_words()

if "round_pairs" not in st.session_state:
    st.session_state.round_pairs = []
    st.session_state.left_order = []
    st.session_state.right_order = []
    st.session_state.matched = set()
    st.session_state.selected_left = None
    st.session_state.selected_right = None
    st.session_state.wrong_msg = ""
    st.session_state.score = 0
    st.session_state.attempts = 0


def start_new_round(num_pairs: int, sequential: bool = False,
                    start_no: int = 1, end_no: int = None):
    """sequential=False：隨機抽題，左欄（英文）順序也隨機。
    sequential=True：依單字清單順序，取第 start_no ~ end_no 個單字（從 1 算起，含頭尾），
    左欄（英文）照清單順序排列；右欄（中文）仍然打亂，才不會變成同一列直接對應。"""
    words = st.session_state.words
    if sequential:
        if end_no is None:
            end_no = start_no + num_pairs - 1
        chosen = list(words[max(start_no, 1) - 1:end_no])
        num_pairs = len(chosen)
    else:
        num_pairs = min(num_pairs, len(words))
        chosen = random.sample(words, num_pairs)
    st.session_state.round_pairs = chosen
    left_idx = list(range(num_pairs))
    right_idx = list(range(num_pairs))
    if not sequential:
        random.shuffle(left_idx)
    random.shuffle(right_idx)
    st.session_state.left_order = left_idx
    st.session_state.right_order = right_idx
    st.session_state.matched = set()
    st.session_state.selected_left = None
    st.session_state.selected_right = None
    st.session_state.wrong_msg = ""
    st.session_state.score = 0
    st.session_state.attempts = 0


# ---------------------------------------------------------------------------
# 5. 側邊欄：單字管理
# ---------------------------------------------------------------------------

def parse_words_json(raw_bytes: bytes):
    """解析並檢查匯入的 JSON。成功回傳 (單字清單, None)，失敗回傳 (None, 錯誤訊息)。"""
    try:
        data = json.loads(raw_bytes.decode("utf-8-sig"))
    except Exception as e:
        return None, f"不是有效的 JSON 檔案：{e}"
    if not isinstance(data, list) or len(data) == 0:
        return None, "JSON 內容必須是「不為空的單字清單」。"
    cleaned = []
    for i, item in enumerate(data, start=1):
        if not isinstance(item, dict):
            return None, f"第 {i} 筆不是物件（應為 {{\"en\":..., \"zh\":...}}）。"
        en = str(item.get("en", "")).strip()
        zh = str(item.get("zh", "")).strip()
        if not en or not zh:
            return None, f"第 {i} 筆缺少 en（英文）或 zh（中文）欄位。"
        icon = str(item.get("icon", "")).strip() or guess_icon(en)
        cleaned.append({"en": en, "zh": zh, "icon": icon})
    return cleaned, None


def make_import_filename(uploaded_name: str) -> str:
    """把上傳的檔名轉成安全的目標檔名；不是 words 開頭的會加上 words_ 前綴，
    這樣才會出現在「選擇要使用的單字檔」清單中。"""
    name = os.path.basename(uploaded_name.replace("\\", "/")).strip() or DEFAULT_WORDS_FILENAME
    if not name.lower().endswith(".json"):
        name += ".json"
    if not name.lower().startswith("words"):
        name = "words_" + name
    return name


def _do_import(name: str, words: list):
    """實際寫入檔案並切換到該單字檔（在 callback 中執行，可安全修改 selectbox 的狀態）。"""
    path = compute_words_file(DATA_DIR, name)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(words, f, ensure_ascii=False, indent=2)
    st.session_state.words_filename = name
    st.session_state.words_file_picker = name
    st.session_state.words = words
    st.session_state.pending_import = None
    st.session_state.import_uploader_n += 1  # 換一個 key，清空上傳欄位
    st.session_state.import_msg = f"✅ 已匯入 {len(words)} 個單字到 {name}"


def request_import(name: str, words: list):
    """按下「匯入」：若檔案已存在先要求確認，否則直接匯入。"""
    if os.path.exists(compute_words_file(DATA_DIR, name)):
        st.session_state.pending_import = {"name": name, "words": words}
    else:
        _do_import(name, words)


def confirm_import():
    p = st.session_state.pending_import
    if p:
        _do_import(p["name"], p["words"])


def cancel_import():
    st.session_state.pending_import = None
    st.session_state.import_msg = "已取消匯入，原檔案未被修改。"


if "pending_import" not in st.session_state:
    st.session_state.pending_import = None
if "import_uploader_n" not in st.session_state:
    st.session_state.import_uploader_n = 0

with st.sidebar:
    st.subheader("📚 選擇要使用的單字檔")
    existing_files = sorted(
        os.path.basename(p) for p in glob.glob(os.path.join(DATA_DIR, "words*.json"))
    )
    if not existing_files:
        existing_files = [DEFAULT_WORDS_FILENAME]
    current_file = st.session_state.words_filename
    if current_file not in existing_files:
        existing_files = sorted(existing_files + [current_file])

    picked_file = st.selectbox(
        "從資料夾中選擇（例如 words1.json、words2.json...）",
        options=existing_files,
        index=existing_files.index(current_file),
        key="words_file_picker",
    )
    if picked_file != current_file:
        apply_words_filename(picked_file)
        st.session_state.words = load_words()
        st.rerun()

    # ---- 匯出 / 匯入單字檔 ----
    st.markdown("**📤 匯出 / 📥 匯入單字檔**")

    st.download_button(
        f"📤 匯出目前單字（{st.session_state.words_filename}）",
        data=json.dumps(st.session_state.words, ensure_ascii=False, indent=2).encode("utf-8"),
        file_name=st.session_state.words_filename,
        mime="application/json",
        key="export_words_btn",
        use_container_width=True,
    )

    if st.session_state.get("import_msg"):
        st.info(st.session_state.pop("import_msg"))

    uploaded = st.file_uploader(
        "匯入 words.json（或其他 .json 單字檔）",
        type=["json"],
        key=f"import_uploader_{st.session_state.import_uploader_n}",
    )

    if uploaded is None:
        st.session_state.pending_import = None
    else:
        import_words, import_err = parse_words_json(uploaded.getvalue())
        target_name = make_import_filename(uploaded.name)
        if import_err:
            st.error(import_err)
        else:
            st.caption(f"檔案內有 {len(import_words)} 個單字，將匯入為：{target_name}")
            if st.session_state.pending_import is None:
                st.button(
                    "📥 匯入",
                    key="import_words_btn",
                    on_click=request_import,
                    args=(target_name, import_words),
                    use_container_width=True,
                )

    # 覆蓋確認：目標檔案已存在時，要再按一次「確定覆蓋」才會真的寫入
    pending = st.session_state.pending_import
    if pending is not None:
        st.warning(f"⚠️ {pending['name']} 已經存在，要覆蓋原本的 {pending['name']} 嗎？")
        ok_col, no_col = st.columns(2)
        with ok_col:
            st.button("✅ 確定覆蓋", key="confirm_import_btn", on_click=confirm_import)
        with no_col:
            st.button("❌ 取消", key="cancel_import_btn", on_click=cancel_import)

    st.divider()
    st.header("📝 單字管理")

    with st.form("add_word_form", clear_on_submit=True):
        st.write("新增單字")
        new_en = st.text_input("英文單字", key="new_en")
        new_zh = st.text_input("中文意思", key="new_zh")
        new_icon = st.text_input("圖案 emoji（可留空，會自動猜測）", key="new_icon")
        submitted = st.form_submit_button("➕ 加入單字")
        if submitted:
            if new_en.strip() and new_zh.strip():
                icon = new_icon.strip() or guess_icon(new_en)
                st.session_state.words.insert(
                    0, {"en": new_en.strip(), "zh": new_zh.strip(), "icon": icon}
                )
                save_words(st.session_state.words)
                st.success(f"已新增：{icon} {new_en.strip()} / {new_zh.strip()}")
            else:
                st.warning("請同時輸入英文單字與中文意思")

    st.divider()
    st.write(
        f"目前共有 {len(st.session_state.words)} 個單字"
        f"（來自 {st.session_state.words_filename}）："
    )

    if "pending_delete" not in st.session_state:
        st.session_state.pending_delete = None

    for i, w in enumerate(st.session_state.words):
        col1, col2 = st.columns([4, 1])
        with col1:
            st.write(f"{i + 1}. {w.get('icon', DEFAULT_ICON)} {w['en']} → {w['zh']}")
        with col2:
            if st.button("🗑️", key=f"del_{i}"):
                st.session_state.pending_delete = i
                st.rerun()

    # 刪除確認訊息：點垃圾桶後不會馬上刪除，要再按一次「確定刪除」才會真的刪掉
    pending_idx = st.session_state.pending_delete
    if pending_idx is not None and 0 <= pending_idx < len(st.session_state.words):
        w = st.session_state.words[pending_idx]
        st.warning(
            f"確定要刪除「{w.get('icon', DEFAULT_ICON)} {w['en']} / {w['zh']}」這個單字嗎？"
        )
        confirm_col, cancel_col = st.columns(2)
        with confirm_col:
            if st.button("✅ 確定刪除", key="confirm_delete_word"):
                st.session_state.words.pop(pending_idx)
                save_words(st.session_state.words)
                st.session_state.pending_delete = None
                st.rerun()
        with cancel_col:
            if st.button("❌ 取消", key="cancel_delete_word"):
                st.session_state.pending_delete = None
                st.rerun()

    st.divider()
    if st.button("🔊 播放全部單字發音（依清單順序）"):
        play_sequence_audio([w["en"] for w in st.session_state.words])

# ---------------------------------------------------------------------------
# 6. 遊戲設定與開始
# ---------------------------------------------------------------------------

ORDER_RANDOM = "🔀 亂數排序"
ORDER_SEQ = "🔢 順序排序"

total_words = len(st.session_state.words)
is_sequential = st.session_state.get("order_mode", ORDER_RANDOM) == ORDER_SEQ
seq_start, seq_end = 1, total_words
range_valid = True

if is_sequential:
    # 順序排序：指定要玩單字清單的第 m 個到第 m+n 個（編號見左側單字清單）
    rc1, rc2 = st.columns(2)
    with rc1:
        seq_start = st.number_input(
            "從第幾個單字開始（m）", min_value=1, max_value=total_words, value=1, step=1
        )
    with rc2:
        seq_end = st.number_input(
            "到第幾個單字結束（m+n）", min_value=1, max_value=total_words,
            value=min(8, total_words), step=1,
        )
    seq_start, seq_end = int(seq_start), int(seq_end)
    range_valid = seq_end >= seq_start
    if range_valid:
        num_pairs = seq_end - seq_start + 1
        st.caption(f"本回合範圍：單字清單第 {seq_start} ～ {seq_end} 個，共 {num_pairs} 組")
    else:
        num_pairs = 0
        st.warning("結束編號不能小於開始編號，請重新設定範圍。")
else:
    max_pairs = max(2, total_words)
    default_pairs = min(8, max_pairs)
    num_pairs = st.slider("本回合要玩幾組單字？", min_value=2, max_value=max_pairs, value=default_pairs)

show_english = st.checkbox(
    "👀 顯示英文單字文字（取消勾選會隱藏文字，只顯示🔊喇叭，考驗聽音辨義）",
    value=True,
    key="show_english",
)
show_chinese = st.checkbox(
    "🀄 顯示中文翻譯文字（取消勾選會隱藏中文，只顯示圖案）",
    value=True,
    key="show_chinese",
)

col_mode, col_a, col_b = st.columns([2, 1, 1], vertical_alignment="center")
with col_mode:
    order_mode = st.radio(
        "題目排序方式",
        options=[ORDER_RANDOM, ORDER_SEQ],
        horizontal=True,
        key="order_mode",
        label_visibility="collapsed",
    )
with col_a:
    if st.button("🔄 開始新回合", type="primary", disabled=not range_valid):
        start_new_round(
            num_pairs,
            sequential=(order_mode == ORDER_SEQ),
            start_no=seq_start,
            end_no=seq_end if order_mode == ORDER_SEQ else None,
        )
        st.rerun()
with col_b:
    if st.session_state.round_pairs and st.button("🔊 連續播放本回合單字發音"):
        play_sequence_audio([p["en"] for p in st.session_state.round_pairs])

# ---------------------------------------------------------------------------
# 7. 遊戲主畫面：連連看
# ---------------------------------------------------------------------------

pairs = st.session_state.round_pairs

# 按鈕字體/圖案放大樣式：英文（左欄）與中文＋圖案（右欄）都設為 3rem
# 除了 button 本身，也對 button 內部所有子元素（Streamlit 常把文字包在內部的 <p>／<div>
# 裡，且該子元素可能有自己的 font-size 設定覆蓋掉外層），全部一起強制設定字體大小，
# 確保不同版本的 Streamlit 都能正確套用。
BUTTON_SIZE_CSS = """
<style>
[class*="st-key-lc_"] button,
[class*="st-key-L_"] button,
[class*="st-key-lc_"] button *,
[class*="st-key-L_"] button * {
    font-size: 3rem !important;
    line-height: 1.2 !important;
    white-space: normal !important;
    overflow: visible !important;
    height: auto !important;
    min-height: 0 !important;
}
[class*="st-key-lc_"] button,
[class*="st-key-L_"] button {
    padding: 0.4rem 0.4rem !important;
}
[class*="st-key-rc_"] button,
[class*="st-key-R_"] button,
[class*="st-key-rc_"] button *,
[class*="st-key-R_"] button * {
    font-size: 3rem !important;
    line-height: 1.2 !important;
    white-space: normal !important;
    overflow: visible !important;
    height: auto !important;
    min-height: 0 !important;
}
[class*="st-key-rc_"] button,
[class*="st-key-R_"] button {
    padding: 0.4rem 0.4rem !important;
}
/* 每一題（每一列）上下的間距、內部間隔都設為 0.05rem */
.st-key-game_rows [data-testid="stHorizontalBlock"] {
    margin-bottom: 0.05rem !important;
    margin-top: 0.05rem !important;
    gap: 0.1rem !important;
}
.st-key-game_rows [data-testid="stVerticalBlockBorderWrapper"],
.st-key-game_rows [data-testid="stVerticalBlock"] {
    gap: 0.05rem !important;
}
.st-key-game_rows [data-testid="element-container"],
.st-key-game_rows .element-container {
    margin-bottom: 0.05rem !important;
    margin-top: 0.05rem !important;
}
/* 題號滑鼠移入顯示英文提示、移開自動隱藏 */
.qnum-wrapper {
    position: relative;
    cursor: default;
    display: inline-block;
    width: 100%;
}
.qnum-tooltip {
    display: none;
    position: absolute;
    top: 100%;
    left: 50%;
    transform: translateX(-50%);
    background: #333333;
    color: #ffffff;
    padding: 0.2rem 0.6rem;
    border-radius: 6px;
    font-size: 1.1rem;
    font-weight: 600;
    white-space: nowrap;
    z-index: 999;
    margin-top: 4px;
}
.qnum-wrapper:hover .qnum-tooltip {
    display: block;
}
</style>
"""
st.markdown(BUTTON_SIZE_CSS, unsafe_allow_html=True)

if not pairs:
    st.info("請先點選上方「開始新回合」來產生題目！")
else:
    total = len(pairs)
    matched = st.session_state.matched

    st.write(
        f"進度：{len(matched)} / {total} 組　｜　答對次數：{st.session_state.score}　"
        f"｜　嘗試次數：{st.session_state.attempts}"
    )

    if st.session_state.wrong_msg:
        st.markdown(
            f"""
            <div style="
                font-size: 3rem;
                font-weight: 900;
                text-align: center;
                color: #ffffff;
                background-color: #ff3b3b;
                border-radius: 16px;
                padding: 1rem;
                margin-bottom: 1rem;
            ">
                {st.session_state.wrong_msg}
            </div>
            """,
            unsafe_allow_html=True,
        )
        time.sleep(1.5)
        st.session_state.wrong_msg = ""
        st.rerun()

    left_col, mid_col, right_col = st.columns([5, 1, 5])
    with left_col:
        st.markdown("### 🔤 English")
    with right_col:
        st.markdown("### 🀄 中文")

    with st.container(key="game_rows"):
        for row in range(total):
            li = st.session_state.left_order[row]
            ri = st.session_state.right_order[row]

            col_l, col_mid, col_r = st.columns([5, 1, 5], gap="small", vertical_alignment="center")

            with col_l:
                w = pairs[li]
                is_matched = li in matched
                is_selected = (st.session_state.selected_left == li)
                prefix = "✅ " if is_matched else ("👉 " if is_selected else "")
                en_part = w["en"] if st.session_state.show_english else ""
                label = f"{prefix}🔊 {en_part}".rstrip()
                with st.container(key=f"lc_{li}"):
                    if st.button(label, key=f"L_{li}", disabled=is_matched, use_container_width=True):
                        st.session_state.selected_left = li
                        st.session_state.wrong_msg = ""

            with col_mid:
                hint_en = pairs[li]["en"]
                st.markdown(
                    f"""<div class="qnum-wrapper" style="text-align:center; font-size:1.4rem;
                    font-weight:800; color:#666;">第{row + 1}題
                    <div class="qnum-tooltip">{hint_en}</div>
                    </div>""",
                    unsafe_allow_html=True,
                )

            with col_r:
                w = pairs[ri]
                is_matched = ri in matched
                is_selected = (st.session_state.selected_right == ri)
                prefix = "✅ " if is_matched else ("👉 " if is_selected else "")
                zh_part = w["zh"] if st.session_state.show_chinese else ""
                label = f"{prefix}{w.get('icon', DEFAULT_ICON)} {zh_part}".rstrip()
                with st.container(key=f"rc_{ri}"):
                    if st.button(label, key=f"R_{ri}", disabled=is_matched, use_container_width=True):
                        st.session_state.selected_right = ri
                        st.session_state.wrong_msg = ""

    # 選取中的英文按鈕（現在在左欄）：持續變色 + 反覆播放發音
    sel_en = st.session_state.selected_left
    if sel_en is not None and sel_en not in matched:
        render_flash_css(f"lc_{sel_en}")
        play_single_audio(pairs[sel_en]["en"], loop=True)

    # 判斷是否兩邊都已選擇
    sl = st.session_state.selected_left
    sr = st.session_state.selected_right
    if sl is not None and sr is not None:
        st.session_state.attempts += 1
        if sl == sr:
            st.session_state.matched.add(sl)
            st.session_state.score += 1
            st.session_state.selected_left = None
            st.session_state.selected_right = None
            st.session_state.wrong_msg = ""
            play_applause_sound()
            play_single_audio(pairs[sl]["en"])
            st.balloons()
            time.sleep(1.5)
            st.rerun()
        else:
            st.session_state.wrong_msg = "❌ 答錯了，再試一次！"
            st.session_state.selected_left = None
            st.session_state.selected_right = None
            trigger_wrong_shake()
            st.rerun()

    if len(matched) == total:
        st.balloons()
        st.success("🎉 恭喜完成本回合！可以點選上方「開始新回合」再玩一次。")

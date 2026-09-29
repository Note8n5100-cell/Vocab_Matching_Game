# -*- coding: utf-8 -*-
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
  {
    "en": "Hey, Andy. What are you doing?",
    "zh": "嘿，Andy。你在做什麼？",
    "icon": "🔤"
  },
  {
    "en": "Hi, Molly. I’m doing a jigsaw puzzle.",
    "zh": "嗨，Molly。我正在拼拼圖。",
    "icon": "🔤"
  },
  {
    "en": "One, two, three, ... There are twenty-five pieces here.",
    "zh": "1、2、3、⋯ 這裡有二十五片拼圖。",
    "icon": "🔤"
  },
  {
    "en": "Would you like to help me finish the jigsaw puzzle?",
    "zh": "你想幫我一起完成拼圖嗎？",
    "icon": "🔤"
  },
  {
    "en": "Yes, I’d like to.",
    "zh": "是的，我想。",
    "icon": "🔤"
  },
  {
    "en": "Mom, there are thirteen tomatoes in the basket.",
    "zh": "媽媽，籃子裡有十三顆番茄。",
    "icon": "🔤"
  },
  {
    "en": "Mom, there are fourteen dishes here.",
    "zh": "媽媽，這裡有十四個盤子。",
    "icon": "🔤"
  },
  {
    "en": "OK. How many mugs do you count?",
    "zh": "好的。那你數了幾個馬克杯了呢？",
    "icon": "🔤"
  },
  {
    "en": "I count thirty.",
    "zh": "我數了三十個。",
    "icon": "🔤"
  },
  {
    "en": "I like this mug. This mug is my favorite.",
    "zh": "我喜歡這個馬克杯。這個馬克杯是我的最愛。",
    "icon": "🔤"
  },
  {
    "en": "I like it, too.",
    "zh": "我也喜歡。",
    "icon": "🔤"
  },
  {
    "en": "There are fifteen children in the picture. They all look happy.",
    "zh": "照片裡有十五位小孩。他們看起來都很開心。",
    "icon": "🔤"
  },
  {
    "en": "There are twenty-six mice under the tree. I like the white one because it is so cute.",
    "zh": "樹下有二十六隻老鼠。我喜歡白色的那隻因為它很可愛。",
    "icon": "🔤"
  },
  {
    "en": "There are thirty-nine knives on the table. Don’t touch them.",
    "zh": "桌上有三十九把刀子。別碰它們。",
    "icon": "🔤"
  },
  {
    "en": "Andy, how does the steak taste?",
    "zh": "Andy，牛排嘗起來如何？",
    "icon": "🔤"
  },
  {
    "en": "It tastes wonderful.",
    "zh": "它嘗起來好極了。",
    "icon": "🔤"
  },
  {
    "en": "It smells good, Dora. What is it?",
    "zh": "它聞起來好棒，Dora。它是什麼？",
    "icon": "🔤"
  },
  {
    "en": "It's my favorite soup.",
    "zh": "它是我最愛的湯。",
    "icon": "🔤"
  },
  {
    "en": "It tastes delicious.",
    "zh": "它嚐起來很美味。",
    "icon": "🔤"
  },
  {
    "en": "You look so happy.",
    "zh": "你看起來很快樂。",
    "icon": "🔤"
  },
  {
    "en": "Yes, I’m very happy.",
    "zh": "是的，我非常快樂。",
    "icon": "🔤"
  },
  {
    "en": "The cake tastes really sweet.",
    "zh": "這個蛋糕嚐起來真的很甜。",
    "icon": "🔤"
  },
  {
    "en": "I like it.",
    "zh": "我喜歡。",
    "icon": "🔤"
  },
  {
    "en": "I like it, too.",
    "zh": "我也喜歡。",
    "icon": "🔤"
  },
  {
    "en": "The coffee tastes really bitter.",
    "zh": "這個咖啡嚐起來真的很苦。",
    "icon": "🔤"
  },
  {
    "en": "I don’t like it.",
    "zh": "我不喜歡。",
    "icon": "🔤"
  },
  {
    "en": "I don’t like it, either.",
    "zh": "我也不喜歡。",
    "icon": "🔤"
  },
  {
    "en": "Andy likes the hamburger because it smells great. Ted likes it, too.",
    "zh": "Andy喜歡漢堡因為它聞起來很棒。Ted也喜歡。",
    "icon": "🔤"
  },
  {
    "en": "Lisa likes the bread because it tastes delicious. Buddy likes it, too.",
    "zh": "Lisa喜歡麵包因為它嚐起來很美味。Buddy也喜歡。",
    "icon": "🔤"
  },
  {
    "en": "Molly and Andy don’t like the French fries because they taste terrible. Buddy doesn’t like them, either.",
    "zh": "Molly和Andy不喜歡薯條因為它們嚐起來很糟糕。Buddy也不喜歡它們。",
    "icon": "🔤"
  },
  {
    "en": "I hope I can learn computer science well.",
    "zh": "我希望我能把電腦科學學好。",
    "icon": "🔤"
  },
  {
    "en": "Why?",
    "zh": "為什麼？",
    "icon": "🔤"
  },
  {
    "en": "I want to be an engineer.",
    "zh": "因為我想成為工程師。",
    "icon": "🔤"
  },
  {
    "en": "I hope I can play basketball well.",
    "zh": "我希望我能把籃球打好。",
    "icon": "🔤"
  },
  {
    "en": "Why?",
    "zh": "為什麼？",
    "icon": "🔤"
  },
  {
    "en": "I want to be a basketball player.",
    "zh": "因為我想成為籃球選手。",
    "icon": "🔤"
  },
  {
    "en": "Andy must feel dizzy.",
    "zh": "安迪一定覺得頭暈。",
    "icon": "🔤"
  },
  {
    "en": "I think he needs to take a rest.",
    "zh": "我覺得他需要休息一下。",
    "icon": "🔤"
  },
  {
    "en": "Who is crying?",
    "zh": "誰正在哭？",
    "icon": "🔤"
  },
  {
    "en": "My sister, Karen, is crying. I don’t think she likes the big dog.",
    "zh": "我的妹妹，Karen正在哭。我並不覺得她喜歡這隻大狗。",
    "icon": "🔤"
  },
  {
    "en": "Poor Karen. I think she wants to go.",
    "zh": "可憐的Karen。我覺得她想走了。",
    "icon": "🔤"
  },
  {
    "en": "I know Lisa likes dresses.",
    "zh": "我知道Lisa喜歡裙子。",
    "icon": "🔤"
  },
  {
    "en": "I know Ted likes sports.",
    "zh": "我知道Ted喜歡運動。",
    "icon": "🔤"
  },
  {
    "en": "I know Molly likes her family.",
    "zh": "我知道Molly喜歡她的家人。",
    "icon": "🔤"
  },
  {
    "en": "I know Buddy likes music.",
    "zh": "我知道Buddy喜歡音樂。",
    "icon": "🔤"
  },
  {
    "en": "I know Ms. Lee likes animals.",
    "zh": "我知道李女士喜歡動物。",
    "icon": "🔤"
  },
  {
    "en": "I know Mr. White likes his students.",
    "zh": "我知道白先生喜歡他的學生。",
    "icon": "🔤"
  },
  {
    "en": "I know everything.",
    "zh": "我知道任何事物。",
    "icon": "🔤"
  },
  {
    "en": "It’s warm outside now. Do you like spring?",
    "zh": "外面現在很暖和。你喜歡春天嗎？",
    "icon": "🔤"
  },
  {
    "en": "Yes, I do. Everybody feels great in spring. Do you like summer?",
    "zh": "是的，我喜歡。每個人在春天都感覺很好。那你喜歡夏天嗎？",
    "icon": "🔤"
  },
  {
    "en": "Yes. In summer, I usually go camping with my family. What do you do in summer?",
    "zh": "是的。在夏天，我常常和我的家人去露營。你在夏天的時候做什麼呢？",
    "icon": "🔤"
  },
  {
    "en": "I go to the beach with my family in summer. We build sandcastles there. It’s fun!",
    "zh": "我和家人在夏天的時候會去海邊。我們會在那邊堆沙堡。很有趣！",
    "icon": "🔤"
  },
  {
    "en": "What's your favorite season?",
    "zh": "你最喜歡的季節是什麼？",
    "icon": "🔤"
  },
  {
    "en": "Fall is my favorite season because I can go hiking with my family.",
    "zh": "秋天是我最喜歡的季節因為我可以跟我的家人去健行。",
    "icon": "🔤"
  },
  {
    "en": "I like fall, too. How about you, Buddy?",
    "zh": "我也喜歡秋天。那你呢，Buddy？",
    "icon": "🔤"
  },
  {
    "en": "My favorite season is winter because I can go skiing with my friends.",
    "zh": "我最喜歡的季節是冬天因為我可以跟我的朋友們去滑雪。",
    "icon": "🔤"
  },
  {
    "en": "I like winter, too.",
    "zh": "我也喜歡冬天。",
    "icon": "🔤"
  },
  {
    "en": "There are four seasons in a year: spring, summer, fall and winter.",
    "zh": "一年有四個季節：春天、夏天、秋天和冬天。",
    "icon": "🔤"
  },
  {
    "en": "In spring, the weather becomes warm and I like to go jogging.",
    "zh": "春天時，天氣變暖和，我喜歡去慢跑。",
    "icon": "🔤"
  },
  {
    "en": "In summer, it’s hot and we like to go swimming.",
    "zh": "夏天很熱，我們喜歡去游泳。",
    "icon": "🔤"
  },
  {
    "en": "In fall, the weather becomes cool and I like to go roller-skating in the park.",
    "zh": "秋天，天氣變涼爽，我喜歡去公園溜直排輪。",
    "icon": "🔤"
  },
  {
    "en": "In winter, it is cold and we like to build a snowman.",
    "zh": "冬天很冷，我們喜歡堆雪人。",
    "icon": "🔤"
  },
  {
    "en": "OK, everybody.",
    "zh": "好的，大家。",
    "icon": "🔤"
  },
  {
    "en": "What season comes after spring?",
    "zh": "春天過後是什麼季節？",
    "icon": "🔤"
  },
  {
    "en": "It’s summer. Summer comes after spring.",
    "zh": "是夏天。夏天在春天之後來。",
    "icon": "🔤"
  },
  {
    "en": "Great! What can you see in summer?",
    "zh": "太棒了！夏天你可以看到什麼？",
    "icon": "🔤"
  },
  {
    "en": "We can see a lot of people wearing shorts and sandals.",
    "zh": "我們可以看到很多人穿著短褲和涼鞋。",
    "icon": "🔤"
  },
  {
    "en": "We can see some people drinking soda.",
    "zh": "我們可以看到有人在喝汽水。",
    "icon": "🔤"
  },
  {
    "en": "What season comes before winter?",
    "zh": "冬天之前是什麼季節？",
    "icon": "🔤"
  },
  {
    "en": "It’s fall. We can see a lot of children jumping in the leaves.",
    "zh": "是秋天。我們可以看到很多小朋友在落葉堆裡跳來跳去。",
    "icon": "🔤"
  },
  {
    "en": "Why is spring your favorite season?",
    "zh": "為什麼春天是你最喜歡的季節？",
    "icon": "🔤"
  },
  {
    "en": "In spring, we can see butterflies flying and hear birds singing.",
    "zh": "春天裡，我們可以看到蝴蝶飛舞，聽到鳥兒歌唱。",
    "icon": "🔤"
  },
  {
    "en": "We can also see people playing and laughing in the playground.",
    "zh": "我們還可以看到人們在操場上玩耍和笑聲不斷。",
    "icon": "🔤"
  },
  {
    "en": "You’re right. I want to go to the bookstore after school. Do you want to come with me?",
    "zh": "你說得對。放學後我想去書店，你想跟我一起去嗎？",
    "icon": "🔤"
  },
  {
    "en": "Sure, but I need to go home before dinner.",
    "zh": "當然可以，但我需要在晚餐前回家。",
    "icon": "🔤"
  },
  {
    "en": "Andy always has breakfast before school.",
    "zh": "Andy總是在上學前吃早餐。",
    "icon": "🔤"
  },
  {
    "en": "He usually reads at his desk after lunch.",
    "zh": "他通常在午餐後在書桌前看書。",
    "icon": "🔤"
  },
  {
    "en": "He always does his homework after school.",
    "zh": "他總是在放學後寫作業。",
    "icon": "🔤"
  },
  {
    "en": "He sometimes takes Rocky to the park before dinner.",
    "zh": "他有時會在晚餐前帶Rocky去公園。",
    "icon": "🔤"
  },
  {
    "en": "He likes to see Rocky running there.",
    "zh": "他喜歡看Rocky在那裡跑來跑去。",
    "icon": "🔤"
  },
  {
    "en": "Andy’s mom is always busy before dinner.",
    "zh": "Andy的媽媽在晚餐前總是很忙。",
    "icon": "🔤"
  },
  {
    "en": "Andy’s dad usually feels tired after work.",
    "zh": "Andy的爸爸下班後通常覺得很累。",
    "icon": "🔤"
  },
  {
    "en": "Andy and his family always have dinner together.",
    "zh": "Andy和他的家人總是一起吃晚餐。",
    "icon": "🔤"
  },
  {
    "en": "They talk, laugh, and enjoy the meal together.",
    "zh": "他們一起聊天、笑著，享受這頓飯。",
    "icon": "🔤"
  },
  {
    "en": "Look! There is a scooter over there. It looks cool.",
    "zh": "看！那邊有一台機車，看起來很酷。",
    "icon": "🔤"
  },
  {
    "en": "My dad goes to work by scooter. It’s a little dangerous.",
    "zh": "我爸爸騎機車去上班。有一點危險。",
    "icon": "🔤"
  },
  {
    "en": "How do you go to school every day?",
    "zh": "你每天怎麼去上學？",
    "icon": "🔤"
  },
  {
    "en": "I usually go to school by bus. How about you?",
    "zh": "我通常坐公車去上學。那你呢？",
    "icon": "🔤"
  },
  {
    "en": "I go to school by bicycle.",
    "zh": "我騎腳踏車去上學。",
    "icon": "🔤"
  },
  {
    "en": "That's nice! I sometimes go to school by bicycle, too.",
    "zh": "那很好！我有時候也會騎腳踏車去上學。",
    "icon": "🔤"
  },
  {
    "en": "Look! There is a scooter over there. It looks cool.",
    "zh": "看！那邊有一台機車，看起來很酷。",
    "icon": "🔤"
  },
  {
    "en": "My dad goes to work by scooter.",
    "zh": "我爸爸騎機車去上班。",
    "icon": "🔤"
  },
  {
    "en": "It's a little dangerous.",
    "zh": "有一點危險。",
    "icon": "🔤"
  },
  {
    "en": "How can we get to ABC Restaurant?",
    "zh": "我們怎麼去ABC餐廳？",
    "icon": "🔤"
  },
  {
    "en": "We can get there by subway. It’s safe and comfortable.",
    "zh": "我們可以搭地鐵去那裡，又安全又舒服。",
    "icon": "🔤"
  },
  {
    "en": "Can we get there on foot?",
    "zh": "我們可以走路去嗎？",
    "icon": "🔤"
  },
  {
    "en": "Of course. Wow! There’s an airplane in the sky.",
    "zh": "當然可以。哇！天上有一架飛機。",
    "icon": "🔤"
  },
  {
    "en": "Now, we can get to a lot of places by airplane.",
    "zh": "現在，我們可以搭飛機去很多地方。",
    "icon": "🔤"
  },
  {
    "en": "There is a big department store in the city.",
    "zh": "市區裡有一家大型百貨公司。",
    "icon": "🔤"
  },
  {
    "en": "John likes to ride his bicycle or motorcycle to get there.",
    "zh": "John喜歡騎自行車或機車去那裡。",
    "icon": "🔤"
  },
  {
    "en": "Ms. Blake wants to drive her car or take a taxi to get there.",
    "zh": "Blake女士想開車或搭計程車去那裡。",
    "icon": "🔤"
  },
  {
    "en": "Sarah likes to take the bus or subway to get there.",
    "zh": "Sarah喜歡搭公車或地鐵去那裡。",
    "icon": "🔤"
  },
  {
    "en": "Mrs. Smith wants to get there on foot.",
    "zh": "Smith太太想走路去那裡。",
    "icon": "🔤"
  },
  {
    "en": "People can get to the department store in a lot of ways.",
    "zh": "人們可以用很多種方式去那家百貨公司。",
    "icon": "🔤"
  }
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


def start_new_round(num_pairs: int):
    words = st.session_state.words
    num_pairs = min(num_pairs, len(words))
    chosen = random.sample(words, num_pairs)
    st.session_state.round_pairs = chosen
    left_idx = list(range(num_pairs))
    right_idx = list(range(num_pairs))
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
            st.write(f"{w.get('icon', DEFAULT_ICON)} {w['en']} → {w['zh']}")
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

max_pairs = max(2, len(st.session_state.words))
default_pairs = min(8, max_pairs)
num_pairs = st.slider("本回合要玩幾組單字？", min_value=2, max_value=max_pairs, value=default_pairs)
show_english = st.checkbox(
    "👀 顯示英文單字文字（取消勾選會隱藏文字，只顯示🔊喇叭，考驗聽音辨義）",
    value=True,
    key="show_english",
)

col_a, col_b = st.columns([1, 1])
with col_a:
    if st.button("🔄 開始新回合", type="primary"):
        start_new_round(num_pairs)
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
                label = f"{prefix}{w.get('icon', DEFAULT_ICON)} {w['zh']}"
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

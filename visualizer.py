# visualizer.py (V32.1 - Dynamic Adaptation Edition)

import mido, time, sys, math, random, cv2, os, json, threading, collections
import numpy as np
# 在导入 pygame 之前设置环境变量，避免在后台线程初始化显示模块导致崩溃
os.environ['SDL_VIDEODRIVER'] = 'dummy'
try:
    from moviepy.editor import VideoFileClip, AudioFileClip
except ImportError:
    from moviepy import VideoFileClip, AudioFileClip
import customtkinter as ctk
from tkinter import filedialog
import pygame
import librosa

# --- 默认参数定义 ---
DEFAULT_WIDTH, DEFAULT_HEIGHT = 1920, 1080; DEFAULT_BPM, DEFAULT_MEASURES = None, 2
DEFAULT_VIBRATION_MAX_INTENSITY = 4.0; DEFAULT_VIBRATION_ATTACK = 0.02; DEFAULT_VIBRATION_DECAY = 0.2
DEFAULT_VIBRATION_SUSTAIN = 0.3; DEFAULT_VIBRATION_RELEASE = 0.1
DEFAULT_FADE_IN, DEFAULT_FADE_OUT = 0.0, 0.5; DEFAULT_SOLO_MODE, DEFAULT_PIANOTILES_MODE = False, False
DEFAULT_NOTE_HEIGHT = 3.0; DEFAULT_VERTICAL_COMPRESSION = 0.9
DEFAULT_SS_DOWNSAMPLE = 4; DEFAULT_SS_GAIN = 1.2
# 【新增功能】为新功能添加默认值
DEFAULT_DYNAMIC_RANGE_MODE = True 
# 在打包后的应用中，presets 目录在资源路径中
def get_presets_dir():
    try:
        # 尝试使用 PyInstaller 的资源路径
        if hasattr(sys, '_MEIPASS'):
            base_path = sys._MEIPASS
            presets_path = os.path.join(base_path, "presets")
            if os.path.exists(presets_path):
                return presets_path
    except:
        pass
    # 回退到当前目录
    return "presets"
PRESETS_DIR = get_presets_dir()
GOLDEN_RATIO = 1.61803398875

# --- 颜文字库 ---
KAOMOJI_LIST = ["(๑•̀ㅂ•́)و✧", "ദ്ദി ˉ͈̀꒳ˉ͈́ )✧", "ヾ(≧▽≦*)o", "(ง •_•)ง", "٩(ˊᗜˋ*)و", "♪(^∇^*)", "( •̀ ω •́ )y"]

# --- 语言库 (【新增功能】添加新功能的翻译) ---
LANGUAGES = {
    "zh": {
        "window_title": "MidiArt Pro", "main_title": "MidiArt Pro", "subtitle": "by Aclameta & Your AI Partner", 
        "preset_library": "预设库:", "load_preset": "加载预设...", "save_button": "保存", "console_title": "控制台", 
        "select_midi_button": "选择 MIDI", "select_audio_button": "选择音频", "select_output_dir_button": "选择输出目录", "output_dir_label": "输出目录:", "not_selected": "未选择", 
        "color_theme_label": "颜色主题:", "notes_black": "音符为黑色", "notes_white": "音符为白色", 
        "resolution_label": "分辨率:", "width_placeholder": "W: {width}", "height_placeholder": "H: {height}", 
        "playback_settings_label": "播放设置:", "bpm_placeholder": "BPM (MIDI默认)", "measures_placeholder": "每页小节数 (默认: {measures})", 
        "note_appearance_title": "音符外观", "note_thickness_label": "音符粗细:", "vertical_compression_label": "垂直压缩:", 
        "fade_in_time_label": "缓入时间:", "fade_out_time_label": "缓出时间:", "adsr_title": "振动ADSR包络", 
        "max_amplitude_label": "最大幅度:", "max_amplitude_placeholder": "像素 (默认: {vib_max})", 
        "attack_label": "A:", "decay_label": "D:", "sustain_label": "S:", "release_label": "R:", 
        "render_mode_title": "渲染模式:", "pianotiles_mode_switch": "钢琴块模式", "solo_mode_switch": "独奏模式 (聚焦)",
        "dynamic_range_switch": "动态音域自适应", # 新增
        "text_info_title": "文本信息:", "song_name_label": "作品名:", "song_name_placeholder": "显示在右上方", 
        "author_name_label": "作者名:", "author_name_placeholder": "显示在作品名下方", "render_button_text": "创世 (GENESIS)", 
        "status_ready": "一切就绪，等待你的指令，制作人。", "save_preset_dialog_title": "保存预设", 
        "save_preset_dialog_text": "输入预设名称:", "preset_saved_status": "预设 '{name}' 已保存！", 
        "no_presets_available": "无可用预设", "error_file_not_selected": "错误: 请先选择MIDI和音频文件！", 
        "status_parsing_midi": "正在解析MIDI...", "error_midi_parse_failed": "MIDI解析失败或无音符", 
        "status_rendering": "正在渲染: {progress:.1%}", "status_merging_audio": "正在合并音轨...", 
        "status_genesis_complete": "创世完成！杰作已保存为 {filename}", "error_generic": "错误: {error}", 
        "language_menu": "语言", "soundscape_title": "声场可视化 (实验性):", "soundscape_switch": "开启", 
        "ss_density_label": "线条密度:", "ss_gain_label": "动态范围:"
    },
    "en": {
        "window_title": "MidiArt Pro", "main_title": "MidiArt Pro", "subtitle": "by Aclameta & Your AI Partner", 
        "preset_library": "Preset Library:", "load_preset": "Load Preset...", "save_button": "Save", "console_title": "Control Panel", 
        "select_midi_button": "Select MIDI", "select_audio_button": "Select Audio", "select_output_dir_button": "Select Output Directory", "output_dir_label": "Output Directory:", "not_selected": "Not selected", 
        "color_theme_label": "Color Theme:", "notes_black": "Notes as Black", "notes_white": "Notes as White", 
        "resolution_label": "Resolution:", "width_placeholder": "W: {width}", "height_placeholder": "H: {height}", 
        "playback_settings_label": "Playback:", "bpm_placeholder": "BPM (MIDI Default)", "measures_placeholder": "Measures/Page (Default: {measures})", 
        "note_appearance_title": "Note Appearance", "note_thickness_label": "Note Thickness:", "vertical_compression_label": "V-Compression:", 
        "fade_in_time_label": "Fade-In Time:", "fade_out_time_label": "Fade-Out Time:", "adsr_title": "Vibration ADSR Envelope", 
        "max_amplitude_label": "Max Amplitude:", "max_amplitude_placeholder": "Pixels (Default: {vib_max})", 
        "attack_label": "A:", "decay_label": "D:", "sustain_label": "S:", "release_label": "R:", 
        "render_mode_title": "Render Mode:", "pianotiles_mode_switch": "Piano Tiles Mode", "solo_mode_switch": "Solo Mode (Focus)", 
        "dynamic_range_switch": "Dynamic Pitch Adaptation", # 新增
        "text_info_title": "Text Info:", "song_name_label": "Title:", "song_name_placeholder": "Displayed at the top right", 
        "author_name_label": "Artist:", "author_name_placeholder": "Displayed below the title", "render_button_text": "GENESIS", 
        "status_ready": "Ready for your command, Producer.", "save_preset_dialog_title": "Save Preset", 
        "save_preset_dialog_text": "Enter preset name:", "preset_saved_status": "Preset '{name}' has been saved!", 
        "no_presets_available": "No presets available", "error_file_not_selected": "Error: Please select MIDI and Audio files first!", 
        "status_parsing_midi": "Parsing MIDI...", "error_midi_parse_failed": "MIDI parsing failed or no notes found", 
        "status_rendering": "Rendering: {progress:.1%}", "status_merging_audio": "Merging audio track...", 
        "status_genesis_complete": "Genesis complete! Masterpiece saved as {filename}", "error_generic": "Error: {error}", 
        "language_menu": "Language", "soundscape_title": "Soundscape (Experimental):", "soundscape_switch": "Enable", 
        "ss_density_label": "Line Density:", "ss_gain_label": "Dynamic Range:"
    },
    "ja": {
        "window_title": "MidiArt Pro", "main_title": "MidiArt Pro", "subtitle": "by Aclameta & Your AI Partner", 
        "preset_library": "プリセット:", "load_preset": "プリセットを読込...", "save_button": "保存", "console_title": "コントロールパネル", 
        "select_midi_button": "MIDIを選択", "select_audio_button": "オーディオを選択", "select_output_dir_button": "出力ディレクトリを選択", "output_dir_label": "出力ディレクトリ:", "not_selected": "未選択", 
        "color_theme_label": "カラーテーマ:", "notes_black": "ノートは黒", "notes_white": "ノートは白", 
        "resolution_label": "解像度:", "width_placeholder": "幅: {width}", "height_placeholder": "高さ: {height}", 
        "playback_settings_label": "再生設定:", "bpm_placeholder": "BPM (MIDIデフォルト)", "measures_placeholder": "ページ毎の小節数 (規定値: {measures})", 
        "note_appearance_title": "ノートの外観", "note_thickness_label": "ノートの太さ:", "vertical_compression_label": "垂直圧縮:", 
        "fade_in_time_label": "フェードイン:", "fade_out_time_label": "フェードアウト:", "adsr_title": "振動ADSRエンベロープ", 
        "max_amplitude_label": "最大振幅:", "max_amplitude_placeholder": "ピクセル (規定値: {vib_max})", 
        "attack_label": "A:", "decay_label": "D:", "sustain_label": "S:", "release_label": "R:", 
        "render_mode_title": "レンダーモード:", "pianotiles_mode_switch": "ピアノタイルモード", "solo_mode_switch": "ソロモード (フォーカス)", 
        "dynamic_range_switch": "ダイナミック音域適応", # 新增
        "text_info_title": "テキスト情報:", "song_name_label": "曲名:", "song_name_placeholder": "右上に表示", 
        "author_name_label": "作曲者名:", "author_name_placeholder": "曲名の下に表示", "render_button_text": "創世 (GENESIS)", 
        "status_ready": "準備完了。プロデューサー、あなたの指示を待っています。", "save_preset_dialog_title": "プリセットを保存", 
        "save_preset_dialog_text": "プリセット名を入力してください:", "preset_saved_status": "プリセット '{name}' を保存しました！", 
        "no_presets_available": "利用可能なプリセットがありません", "error_file_not_selected": "エラー: 先にMIDIとオーディオファイルを選択してください！", 
        "status_parsing_midi": "MIDIを解析中...", "error_midi_parse_failed": "MIDIの解析に失敗したか、ノートがありません", 
        "status_rendering": "レンダリング中: {progress:.1%}", "status_merging_audio": "オーディオトラックを結合中...", 
        "status_genesis_complete": "創世完了！傑作は {filename} として保存されました", "error_generic": "エラー: {error}", 
        "language_menu": "言語", "soundscape_title": "サウンドスケープ (試験的):", "soundscape_switch": "有効化", 
        "ss_density_label": "ライン密度:", "ss_gain_label": "ダイナミックレンジ:"
    },
    "zh_tw": {
        "window_title": "MidiArt Pro", "main_title": "MidiArt Pro", "subtitle": "by Aclameta & Your AI Partner", 
        "preset_library": "預設集:", "load_preset": "載入預設...", "save_button": "儲存", "console_title": "控制台", 
        "select_midi_button": "選取 MIDI", "select_audio_button": "選取音訊", "select_output_dir_button": "選取輸出目錄", "output_dir_label": "輸出目錄:", "not_selected": "尚未選取", 
        "color_theme_label": "顏色主題:", "notes_black": "音符為黑色", "notes_white": "音符為白色", 
        "resolution_label": "解析度:", "width_placeholder": "寬: {width}", "height_placeholder": "高: {height}", 
        "playback_settings_label": "播放設定:", "bpm_placeholder": "BPM (MIDI預設)", "measures_placeholder": "每頁小節數 (預設: {measures})", 
        "note_appearance_title": "音符外觀", "note_thickness_label": "音符粗細:", "vertical_compression_label": "垂直壓縮:", 
        "fade_in_time_label": "淡入時間:", "fade_out_time_label": "淡出時間:", "adsr_title": "顫動ADSR包絡", 
        "max_amplitude_label": "最大振幅:", "max_amplitude_placeholder": "像素 (預設: {vib_max})", 
        "attack_label": "A:", "decay_label": "D:", "sustain_label": "S:", "release_label": "R:", 
        "render_mode_title": "渲染模式:", "pianotiles_mode_switch": "鋼琴塊模式", "solo_mode_switch": "獨奏模式 (聚焦)", 
        "dynamic_range_switch": "動態音域適應", # 新增
        "text_info_title": "文字資訊:", "song_name_label": "作品名稱:", "song_name_placeholder": "顯示於右上方", 
        "author_name_label": "作者名稱:", "author_name_placeholder": "顯示於作品名稱下方", "render_button_text": "創世 (GENESIS)", 
        "status_ready": "一切就緒，等待您的指令，製作人。", "save_preset_dialog_title": "儲存預設", 
        "save_preset_dialog_text": "輸入預設名稱:", "preset_saved_status": "預設 '{name}' 已儲存！", 
        "no_presets_available": "無可用預設", "error_file_not_selected": "錯誤: 請先選取MIDI和音訊檔案！", 
        "status_parsing_midi": "正在解析MIDI...", "error_midi_parse_failed": "MIDI解析失敗或無音符", 
        "status_rendering": "正在渲染: {progress:.1%}", "status_merging_audio": "正在合併音軌...", 
        "status_genesis_complete": "創世完成！傑作已儲存為 {filename}", "error_generic": "錯誤: {error}", 
        "language_menu": "語言", "soundscape_title": "聲場視覺化 (實驗性):", "soundscape_switch": "啟用", 
        "ss_density_label": "線條密度:", "ss_gain_label": "動態範圍:"
    }
}

def resource_path(relative_path):
    try: base_path = sys._MEIPASS
    except Exception: base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def sanitize_filename(filename):
    """清理文件名，移除或替换不安全的字符"""
    import re
    # 移除或替换不安全的字符：&, *, ?, |, <, >, :, ", /, \, 空格, 以及控制字符
    # 将所有不安全的字符替换为下划线
    filename = re.sub(r'[<>:"/\\|?*&\s\x00-\x1f]', '_', filename)
    # 移除连续的下划线
    filename = re.sub(r'_+', '_', filename)
    # 移除开头和结尾的下划线
    filename = filename.strip('_')
    # 确保文件名不为空
    if not filename:
        filename = "output"
    # 限制文件名长度（避免路径过长）
    if len(filename) > 200:
        filename = filename[:200]
    return filename

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.current_lang = "zh"; self.texts = LANGUAGES[self.current_lang]
        self.title(self.texts["window_title"]); self.geometry("600x850")
        ctk.set_appearance_mode("Light"); ctk.set_default_color_theme("blue")
        self.midi_path, self.audio_path = "", ""; self.grid_columnconfigure(0, weight=1);
        
        # 设置默认输出目录：使用用户的视频目录（~/Movies）
        default_output_dir = os.path.join(os.path.expanduser("~"), "Movies")
        # 如果视频目录不存在，创建它
        if not os.path.exists(default_output_dir):
            try:
                os.makedirs(default_output_dir, exist_ok=True)
            except:
                # 如果创建失败，使用用户主目录
                default_output_dir = os.path.expanduser("~")
        self.output_dir = default_output_dir
        
        # 设置 MoviePy 临时目录，确保临时文件在可访问的位置
        import tempfile
        self.moviepy_temp_dir = tempfile.gettempdir()
        # 设置环境变量，让 MoviePy 使用指定的临时目录
        os.environ['MOVIEPY_TEMP_DIR'] = self.moviepy_temp_dir
        
        # pygame 初始化延迟到需要时进行，避免在主线程初始化导致 GIL 问题
        
        try:
            self.font_path_regular = resource_path("SourceHanSansSC-Regular.otf")
            self.font_path_bold = resource_path("SourceHanSansSC-Bold.otf")
            self.ui_title_font = ctk.CTkFont(family=self.font_path_bold, size=28)
            self.ui_subtitle_font = ctk.CTkFont(family=self.font_path_regular, size=16)
            self.ui_label_font = ctk.CTkFont(family=self.font_path_regular, size=14)
            self.ui_button_font = ctk.CTkFont(family=self.font_path_bold, size=14)
            self.ui_big_button_font = ctk.CTkFont(family=self.font_path_bold, size=20)
            self.ui_header_font = ctk.CTkFont(family=self.font_path_bold, size=14)
        except Exception as e:
            print(f"字体加载失败: {e}. 将使用默认字体。")
            self.ui_title_font = ctk.CTkFont(size=28, weight="bold"); self.ui_subtitle_font = ctk.CTkFont(size=16); self.ui_label_font = ctk.CTkFont(size=14)
            self.ui_button_font = ctk.CTkFont(size=14, weight="bold"); self.ui_big_button_font = ctk.CTkFont(size=20, weight="bold"); self.ui_header_font = ctk.CTkFont(weight="bold")

        self.setup_ui(); self.load_presets()

    def setup_ui(self):
        self.grid_rowconfigure(3, weight=1)
        top_frame = ctk.CTkFrame(self, fg_color="transparent"); top_frame.grid(row=0, column=0, padx=20, pady=(20, 5), sticky="ew"); top_frame.grid_columnconfigure(1, weight=1)
        self.main_title_label = ctk.CTkLabel(top_frame, text=self.texts["main_title"], font=self.ui_title_font); self.main_title_label.grid(row=0, column=0, sticky="w")
        self.kaomoji_label = ctk.CTkLabel(top_frame, text=random.choice(KAOMOJI_LIST), font=self.ui_subtitle_font); self.kaomoji_label.grid(row=0, column=1, sticky="ew")
        self.language_menu = ctk.CTkOptionMenu(top_frame, values=["🇨🇳 简体中文", "🇹🇼 正體中文", "🇺🇸 English", "🇯🇵 日本語"], command=self.change_language, font=self.ui_button_font, width=150); self.language_menu.set("🇨🇳 简体中文"); self.language_menu.grid(row=0, column=2, sticky="e")
        self.subtitle_label = ctk.CTkLabel(self, text=self.texts["subtitle"], font=self.ui_subtitle_font, anchor="w"); self.subtitle_label.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="ew")
        preset_frame = ctk.CTkFrame(self); preset_frame.grid(row=2, column=0, padx=20, pady=5, sticky="ew"); preset_frame.grid_columnconfigure(1, weight=1)
        self.preset_library_label = ctk.CTkLabel(preset_frame, text=self.texts["preset_library"], font=self.ui_button_font); self.preset_library_label.grid(row=0, column=0, padx=10, pady=10)
        self.preset_menu = ctk.CTkOptionMenu(preset_frame, values=[self.texts["load_preset"]], command=self.apply_preset, font=self.ui_label_font); self.preset_menu.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.save_preset_button = ctk.CTkButton(preset_frame, text=self.texts["save_button"], command=self.save_preset, font=self.ui_button_font, width=80); self.save_preset_button.grid(row=0, column=2, padx=10, pady=10)
        self.scrollable_frame = ctk.CTkScrollableFrame(self, label_text=self.texts["console_title"], label_font=self.ui_header_font); self.scrollable_frame.grid(row=3, column=0, padx=20, pady=5, sticky="nsew"); self.scrollable_frame.grid_columnconfigure(0, weight=1)
        
        file_frame = ctk.CTkFrame(self.scrollable_frame); file_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew"); file_frame.grid_columnconfigure(1, weight=1)
        self.select_midi_button = ctk.CTkButton(file_frame, text=self.texts["select_midi_button"], command=self.select_midi, font=self.ui_button_font); self.select_midi_button.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.midi_label = ctk.CTkLabel(file_frame, text=self.texts["not_selected"], anchor="w", font=self.ui_label_font); self.midi_label.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.select_audio_button = ctk.CTkButton(file_frame, text=self.texts["select_audio_button"], command=self.select_audio, font=self.ui_button_font); self.select_audio_button.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.audio_label = ctk.CTkLabel(file_frame, text=self.texts["not_selected"], anchor="w", font=self.ui_label_font); self.audio_label.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        self.select_output_dir_button = ctk.CTkButton(file_frame, text=self.texts["select_output_dir_button"], command=self.select_output_dir, font=self.ui_button_font); self.select_output_dir_button.grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.output_dir_label = ctk.CTkLabel(file_frame, text=self.output_dir, anchor="w", font=self.ui_label_font); self.output_dir_label.grid(row=2, column=1, padx=10, pady=10, sticky="ew")
        settings_frame = ctk.CTkFrame(self.scrollable_frame); settings_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10); settings_frame.grid_columnconfigure(1, weight=1)
        color_theme_frame = ctk.CTkFrame(settings_frame, fg_color=("gray90", "gray19")); color_theme_frame.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="ew"); color_theme_frame.grid_columnconfigure(1, weight=1)
        self.color_theme_label = ctk.CTkLabel(color_theme_frame, text=self.texts["color_theme_label"], font=self.ui_label_font); self.color_theme_label.grid(row=0, column=0, padx=(10,5), pady=5)
        self.color_mode_var = ctk.StringVar(value=self.texts["notes_black"]); self.color_mode_switch = ctk.CTkSegmentedButton(color_theme_frame, values=[self.texts["notes_black"], self.texts["notes_white"]], variable=self.color_mode_var, font=self.ui_label_font); self.color_mode_switch.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        res_frame = ctk.CTkFrame(settings_frame); res_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        self.resolution_label = ctk.CTkLabel(res_frame, text=self.texts["resolution_label"], font=self.ui_label_font); self.resolution_label.pack(side="left", padx=(5,10))
        self.width_entry = ctk.CTkEntry(res_frame, placeholder_text=self.texts["width_placeholder"].format(width=DEFAULT_WIDTH), font=self.ui_label_font); self.width_entry.pack(side="left", padx=5, expand=True, fill="x")
        self.height_entry = ctk.CTkEntry(res_frame, placeholder_text=self.texts["height_placeholder"].format(height=DEFAULT_HEIGHT), font=self.ui_label_font); self.height_entry.pack(side="left", padx=5, expand=True, fill="x")
        play_frame = ctk.CTkFrame(settings_frame); play_frame.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        self.playback_settings_label = ctk.CTkLabel(play_frame, text=self.texts["playback_settings_label"], font=self.ui_label_font); self.playback_settings_label.pack(side="left", padx=(5,10))
        self.bpm_entry = ctk.CTkEntry(play_frame, placeholder_text=self.texts["bpm_placeholder"], font=self.ui_label_font); self.bpm_entry.pack(side="left", padx=5, expand=True, fill="x")
        self.measures_entry = ctk.CTkEntry(play_frame, placeholder_text=self.texts["measures_placeholder"].format(measures=DEFAULT_MEASURES), font=self.ui_label_font); self.measures_entry.pack(side="left", padx=5, expand=True, fill="x")
        appearance_frame = ctk.CTkFrame(settings_frame, fg_color=("gray90", "gray19")); appearance_frame.grid(row=3, column=0, columnspan=2, padx=5, pady=10, sticky="ew"); appearance_frame.grid_columnconfigure(1, weight=1)
        self.note_appearance_title_label = ctk.CTkLabel(appearance_frame, text=self.texts["note_appearance_title"], font=self.ui_header_font); self.note_appearance_title_label.grid(row=0, column=0, columnspan=3, pady=(5,10))
        self.note_thickness_label = ctk.CTkLabel(appearance_frame, text=self.texts["note_thickness_label"], font=self.ui_label_font); self.note_thickness_label.grid(row=1, column=0, padx=(10,5), pady=5, sticky="w")
        self.note_height_slider = ctk.CTkSlider(appearance_frame, from_=1, to=10, command=lambda v: self.note_height_label.configure(text=f"{v:.1f} px")); self.note_height_slider.set(DEFAULT_NOTE_HEIGHT); self.note_height_slider.grid(row=1, column=1, padx=5, pady=5, sticky="ew"); self.note_height_label = ctk.CTkLabel(appearance_frame, text=f"{DEFAULT_NOTE_HEIGHT:.1f} px", width=60, font=self.ui_label_font); self.note_height_label.grid(row=1, column=2, padx=(5,10))
        self.vertical_compression_label = ctk.CTkLabel(appearance_frame, text=self.texts["vertical_compression_label"], font=self.ui_label_font); self.vertical_compression_label.grid(row=2, column=0, padx=(10,5), pady=5, sticky="w")
        self.v_compress_slider = ctk.CTkSlider(appearance_frame, from_=0.1, to=1.0, command=lambda v: self.v_compress_label.configure(text=f"{v*100:.0f}%")); self.v_compress_slider.set(DEFAULT_VERTICAL_COMPRESSION); self.v_compress_slider.grid(row=2, column=1, padx=5, pady=5, sticky="ew"); self.v_compress_label = ctk.CTkLabel(appearance_frame, text=f"{DEFAULT_VERTICAL_COMPRESSION*100:.0f}%", width=60, font=self.ui_label_font); self.v_compress_label.grid(row=2, column=2, padx=(5,10))
        fade_frame = ctk.CTkFrame(settings_frame); fade_frame.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky="ew"); fade_frame.grid_columnconfigure(1, weight=1)
        self.fade_in_time_label = ctk.CTkLabel(fade_frame, text=self.texts["fade_in_time_label"], font=self.ui_label_font); self.fade_in_time_label.grid(row=0, column=0, padx=(5,10), pady=5)
        self.fade_in_slider = ctk.CTkSlider(fade_frame, from_=0.0, to=1.0, command=lambda v: self.fade_in_label.configure(text=f"{v:.2f} s")); self.fade_in_slider.set(DEFAULT_FADE_IN); self.fade_in_slider.grid(row=0, column=1, padx=5, pady=5, sticky="ew"); self.fade_in_label = ctk.CTkLabel(fade_frame, text=f"{DEFAULT_FADE_IN:.2f} s", width=50, font=self.ui_label_font); self.fade_in_label.grid(row=0, column=2, padx=(5,10))
        self.fade_out_time_label = ctk.CTkLabel(fade_frame, text=self.texts["fade_out_time_label"], font=self.ui_label_font); self.fade_out_time_label.grid(row=1, column=0, padx=(5,10), pady=5)
        self.fade_out_slider = ctk.CTkSlider(fade_frame, from_=0.0, to=1.0, command=lambda v: self.fade_out_label.configure(text=f"{v:.2f} s")); self.fade_out_slider.set(DEFAULT_FADE_OUT); self.fade_out_slider.grid(row=1, column=1, padx=5, pady=5, sticky="ew"); self.fade_out_label = ctk.CTkLabel(fade_frame, text=f"{DEFAULT_FADE_OUT:.2f} s", width=50, font=self.ui_label_font); self.fade_out_label.grid(row=1, column=2, padx=(5,10))
        adsr_frame = ctk.CTkFrame(settings_frame, fg_color=("gray90", "gray19")); adsr_frame.grid(row=5, column=0, columnspan=2, padx=5, pady=10, sticky="ew"); adsr_frame.grid_columnconfigure(1, weight=1)
        self.adsr_title_label = ctk.CTkLabel(adsr_frame, text=self.texts["adsr_title"], font=self.ui_header_font); self.adsr_title_label.grid(row=0, column=0, columnspan=3, pady=(5,10))
        self.max_amplitude_label = ctk.CTkLabel(adsr_frame, text=self.texts["max_amplitude_label"], font=self.ui_label_font); self.max_amplitude_label.grid(row=1, column=0, padx=(10,5), pady=5, sticky="w")
        self.vib_max_entry = ctk.CTkEntry(adsr_frame, placeholder_text=self.texts["max_amplitude_placeholder"].format(vib_max=DEFAULT_VIBRATION_MAX_INTENSITY), font=self.ui_label_font); self.vib_max_entry.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky="ew")
        self.attack_label = ctk.CTkLabel(adsr_frame, text=self.texts["attack_label"], font=self.ui_label_font); self.attack_label.grid(row=2, column=0, padx=(10,5), pady=5, sticky="w")
        self.vib_a_slider = ctk.CTkSlider(adsr_frame, from_=0.0, to=0.5, command=lambda v: self.vib_a_label.configure(text=f"{v:.3f}s")); self.vib_a_slider.set(DEFAULT_VIBRATION_ATTACK); self.vib_a_slider.grid(row=2, column=1, padx=5, pady=5, sticky="ew"); self.vib_a_label = ctk.CTkLabel(adsr_frame, text=f"{DEFAULT_VIBRATION_ATTACK:.3f}s", width=50, font=self.ui_label_font); self.vib_a_label.grid(row=2, column=2, padx=(5,10))
        self.decay_label = ctk.CTkLabel(adsr_frame, text=self.texts["decay_label"], font=self.ui_label_font); self.decay_label.grid(row=3, column=0, padx=(10,5), pady=5, sticky="w")
        self.vib_d_slider = ctk.CTkSlider(adsr_frame, from_=0.0, to=1.0, command=lambda v: self.vib_d_label.configure(text=f"{v:.3f}s")); self.vib_d_slider.set(DEFAULT_VIBRATION_DECAY); self.vib_d_slider.grid(row=3, column=1, padx=5, pady=5, sticky="ew"); self.vib_d_label = ctk.CTkLabel(adsr_frame, text=f"{DEFAULT_VIBRATION_DECAY:.3f}s", width=50, font=self.ui_label_font); self.vib_d_label.grid(row=3, column=2, padx=(5,10))
        self.sustain_label = ctk.CTkLabel(adsr_frame, text=self.texts["sustain_label"], font=self.ui_label_font); self.sustain_label.grid(row=4, column=0, padx=(10,5), pady=5, sticky="w")
        self.vib_s_slider = ctk.CTkSlider(adsr_frame, from_=0.0, to=1.0, command=lambda v: self.vib_s_label.configure(text=f"{v*100:.0f}%")); self.vib_s_slider.set(DEFAULT_VIBRATION_SUSTAIN); self.vib_s_slider.grid(row=4, column=1, padx=5, pady=5, sticky="ew"); self.vib_s_label = ctk.CTkLabel(adsr_frame, text=f"{DEFAULT_VIBRATION_SUSTAIN*100:.0f}%", width=50, font=self.ui_label_font); self.vib_s_label.grid(row=4, column=2, padx=(5,10))
        self.release_label = ctk.CTkLabel(adsr_frame, text=self.texts["release_label"], font=self.ui_label_font); self.release_label.grid(row=5, column=0, padx=(10,5), pady=5, sticky="w")
        self.vib_r_slider = ctk.CTkSlider(adsr_frame, from_=0.0, to=1.0, command=lambda v: self.vib_r_label.configure(text=f"{v:.3f}s")); self.vib_r_slider.set(DEFAULT_VIBRATION_RELEASE); self.vib_r_slider.grid(row=5, column=1, padx=5, pady=5, sticky="ew"); self.vib_r_label = ctk.CTkLabel(adsr_frame, text=f"{DEFAULT_VIBRATION_RELEASE:.3f}s", width=50, font=self.ui_label_font); self.vib_r_label.grid(row=5, column=2, padx=(5,10))
        
        mode_frame = ctk.CTkFrame(self.scrollable_frame); mode_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        self.render_mode_title_label = ctk.CTkLabel(mode_frame, text=self.texts["render_mode_title"], font=self.ui_header_font); self.render_mode_title_label.pack(side="top", anchor="w", padx=10, pady=(5,0))
        self.mode_switch = ctk.CTkSwitch(mode_frame, text=self.texts["solo_mode_switch"], font=self.ui_label_font, onvalue=True, offvalue=False, command=self.toggle_solo_options); self.mode_switch.pack(side="top", anchor="w", padx=10, pady=5)
        
        # --- 【新增功能】创建钢琴块模式的专属容器 ---
        self.pianotiles_master_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        self.pianotiles_master_frame.grid(row=3, column=0, sticky="ew", padx=0, pady=0)
        
        self.pianotiles_switch = ctk.CTkSwitch(self.pianotiles_master_frame, text=self.texts["pianotiles_mode_switch"], font=self.ui_label_font, onvalue=True, offvalue=False, command=self.toggle_pianotiles_options)
        self.pianotiles_switch.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        # --- 【新增功能】创建新开关，并放入一个子框架中，方便一起显示/隐藏 ---
        self.pianotiles_options_frame = ctk.CTkFrame(self.pianotiles_master_frame, fg_color="transparent")
        self.pianotiles_options_frame.grid(row=1, column=0, sticky="ew", padx=0, pady=0)
        
        self.dynamic_range_switch = ctk.CTkSwitch(self.pianotiles_options_frame, text=self.texts["dynamic_range_switch"], font=self.ui_label_font, onvalue=True, offvalue=False)
        self.dynamic_range_switch.grid(row=0, column=0, sticky='w', padx=20, pady=5)
        self.dynamic_range_switch.select() # 默认开启

        self.text_input_frame = ctk.CTkFrame(self.pianotiles_options_frame, fg_color=("gray90", "gray19"))
        self.text_input_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        self.text_input_frame.grid_columnconfigure(1, weight=1)
        self.text_info_title_label = ctk.CTkLabel(self.text_input_frame, text=self.texts["text_info_title"], font=self.ui_header_font); self.text_info_title_label.grid(row=0, column=0, columnspan=2, padx=10, pady=(5,0))
        self.song_name_label = ctk.CTkLabel(self.text_input_frame, text=self.texts["song_name_label"], font=self.ui_label_font); self.song_name_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.song_name_entry = ctk.CTkEntry(self.text_input_frame, placeholder_text=self.texts["song_name_placeholder"], font=self.ui_label_font); self.song_name_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        self.author_name_label = ctk.CTkLabel(self.text_input_frame, text=self.texts["author_name_label"], font=self.ui_label_font); self.author_name_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.author_name_entry = ctk.CTkEntry(self.text_input_frame, placeholder_text=self.texts["author_name_placeholder"], font=self.ui_label_font); self.author_name_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
        
        self.soundscape_frame = ctk.CTkFrame(self.pianotiles_options_frame, fg_color=("gray90", "gray19"))
        self.soundscape_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(10,0))
        self.soundscape_frame.grid_columnconfigure(1, weight=1)
        self.soundscape_title_label = ctk.CTkLabel(self.soundscape_frame, text=self.texts["soundscape_title"], font=self.ui_header_font); self.soundscape_title_label.grid(row=0, column=0, padx=10, pady=(5,0), sticky="w")
        self.soundscape_switch = ctk.CTkSwitch(self.soundscape_frame, text=self.texts["soundscape_switch"], font=self.ui_label_font, onvalue=True, offvalue=False); self.soundscape_switch.grid(row=0, column=1, padx=10, pady=(5,0))
        self.ss_density_label = ctk.CTkLabel(self.soundscape_frame, text=self.texts["ss_density_label"], font=self.ui_label_font); self.ss_density_label.grid(row=1, column=0, padx=(10,5), pady=5, sticky="w")
        self.ss_density_slider = ctk.CTkSlider(self.soundscape_frame, from_=1, to=10, number_of_steps=9, command=lambda v: self.ss_density_value_label.configure(text=f"1/{int(v)}")); self.ss_density_slider.set(DEFAULT_SS_DOWNSAMPLE); self.ss_density_slider.grid(row=1, column=1, padx=5, pady=5, sticky="ew"); self.ss_density_value_label = ctk.CTkLabel(self.soundscape_frame, text=f"1/{DEFAULT_SS_DOWNSAMPLE}", width=50, font=self.ui_label_font); self.ss_density_value_label.grid(row=1, column=2, padx=(5,10))
        self.ss_gain_label = ctk.CTkLabel(self.soundscape_frame, text=self.texts["ss_gain_label"], font=self.ui_label_font); self.ss_gain_label.grid(row=2, column=0, padx=(10,5), pady=5, sticky="w")
        self.ss_gain_slider = ctk.CTkSlider(self.soundscape_frame, from_=0.5, to=3.0, command=lambda v: self.ss_gain_value_label.configure(text=f"{v:.1f}x")); self.ss_gain_slider.set(DEFAULT_SS_GAIN); self.ss_gain_slider.grid(row=2, column=1, padx=5, pady=5, sticky="ew"); self.ss_gain_value_label = ctk.CTkLabel(self.soundscape_frame, text=f"{DEFAULT_SS_GAIN:.1f}x", width=50, font=self.ui_label_font); self.ss_gain_value_label.grid(row=2, column=2, padx=(5,10))

        self.pianotiles_options_frame.grid_remove() # 默认隐藏子选项
        
        # 初始时，钢琴块模式和独奏模式不能共存
        self.toggle_pianotiles_options()

        bottom_frame = ctk.CTkFrame(self, fg_color="transparent"); bottom_frame.grid(row=4, column=0, sticky="ew", padx=20, pady=(5, 10)); bottom_frame.grid_columnconfigure(0, weight=1)
        self.render_button = ctk.CTkButton(bottom_frame, text=self.texts["render_button_text"], command=self.start_render, font=self.ui_big_button_font, height=40); self.render_button.grid(row=0, column=0, pady=10, sticky="ew")
        self.progress_bar = ctk.CTkProgressBar(bottom_frame, orientation="horizontal"); self.progress_bar.set(0); self.progress_bar.grid(row=1, column=0, pady=5, sticky="ew")
        self.progress_label = ctk.CTkLabel(bottom_frame, text=self.texts["status_ready"], font=self.ui_label_font); self.progress_label.grid(row=2, column=0, pady=5)
        self.update_ui_text()

    def change_language(self, language_choice):
        lang_code_map = {"🇨🇳 简体中文": "zh", "🇹🇼 正體中文": "zh_tw", "🇺🇸 English": "en", "🇯🇵 日本語": "ja"}; self.current_lang = lang_code_map[language_choice]; self.texts = LANGUAGES[self.current_lang]; self.update_ui_text()

    def update_ui_text(self):
        self.title(self.texts["window_title"]); self.main_title_label.configure(font=self.ui_title_font); self.subtitle_label.configure(font=self.ui_subtitle_font)
        self.language_menu.configure(font=self.ui_button_font); self.preset_library_label.configure(text=self.texts["preset_library"], font=self.ui_button_font)
        self.preset_menu.configure(font=self.ui_label_font)
        current_preset_val = self.preset_menu.get()
        is_placeholder = any(current_preset_val == LANGUAGES[lang_code][key] for lang_code in LANGUAGES for key in ["load_preset", "no_presets_available"])
        if is_placeholder:
             if not os.path.exists(PRESETS_DIR) or not any(f.endswith('.json') for f in os.listdir(PRESETS_DIR)):
                self.preset_menu.configure(values=[self.texts["no_presets_available"]]); self.preset_menu.set(self.texts["no_presets_available"])
             else: self.preset_menu.configure(values=[f.replace('.json', '') for f in os.listdir(PRESETS_DIR) if f.endswith('.json')]); self.preset_menu.set(self.texts["load_preset"])
        self.save_preset_button.configure(text=self.texts["save_button"], font=self.ui_button_font); self.scrollable_frame.configure(label_text=self.texts["console_title"], label_font=self.ui_header_font); self.select_midi_button.configure(text=self.texts["select_midi_button"], font=self.ui_button_font)
        if any(self.midi_label.cget("text") == LANGUAGES[lang]["not_selected"] for lang in LANGUAGES): self.midi_label.configure(text=self.texts["not_selected"])
        self.midi_label.configure(font=self.ui_label_font); self.select_audio_button.configure(text=self.texts["select_audio_button"], font=self.ui_button_font)
        if any(self.audio_label.cget("text") == LANGUAGES[lang]["not_selected"] for lang in LANGUAGES): self.audio_label.configure(text=self.texts["not_selected"])
        self.audio_label.configure(font=self.ui_label_font); self.select_output_dir_button.configure(text=self.texts["select_output_dir_button"], font=self.ui_button_font)
        self.output_dir_label.configure(text=self.output_dir, font=self.ui_label_font); self.color_theme_label.configure(text=self.texts["color_theme_label"], font=self.ui_label_font); self.color_mode_switch.configure(values=[self.texts["notes_black"], self.texts["notes_white"]], font=self.ui_label_font); self.resolution_label.configure(text=self.texts["resolution_label"], font=self.ui_label_font)
        self.width_entry.configure(placeholder_text=self.texts["width_placeholder"].format(width=DEFAULT_WIDTH), font=self.ui_label_font); self.height_entry.configure(placeholder_text=self.texts["height_placeholder"].format(height=DEFAULT_HEIGHT), font=self.ui_label_font); self.playback_settings_label.configure(text=self.texts["playback_settings_label"], font=self.ui_label_font)
        self.bpm_entry.configure(placeholder_text=self.texts["bpm_placeholder"], font=self.ui_label_font); self.measures_entry.configure(placeholder_text=self.texts["measures_placeholder"].format(measures=DEFAULT_MEASURES), font=self.ui_label_font); self.note_appearance_title_label.configure(text=self.texts["note_appearance_title"], font=self.ui_header_font)
        self.note_thickness_label.configure(text=self.texts["note_thickness_label"], font=self.ui_label_font); self.note_height_label.configure(font=self.ui_label_font); self.vertical_compression_label.configure(text=self.texts["vertical_compression_label"], font=self.ui_label_font); self.v_compress_label.configure(font=self.ui_label_font); self.fade_in_time_label.configure(text=self.texts["fade_in_time_label"], font=self.ui_label_font); self.fade_in_label.configure(font=self.ui_label_font)
        self.fade_out_time_label.configure(text=self.texts["fade_out_time_label"], font=self.ui_label_font); self.fade_out_label.configure(font=self.ui_label_font); self.adsr_title_label.configure(text=self.texts["adsr_title"], font=self.ui_header_font); self.max_amplitude_label.configure(text=self.texts["max_amplitude_label"], font=self.ui_label_font)
        self.vib_max_entry.configure(placeholder_text=self.texts["max_amplitude_placeholder"].format(vib_max=DEFAULT_VIBRATION_MAX_INTENSITY), font=self.ui_label_font); self.attack_label.configure(text=self.texts["attack_label"], font=self.ui_label_font); self.vib_a_label.configure(font=self.ui_label_font); self.decay_label.configure(text=self.texts["decay_label"], font=self.ui_label_font); self.vib_d_label.configure(font=self.ui_label_font); self.sustain_label.configure(text=self.texts["sustain_label"], font=self.ui_label_font); self.vib_s_label.configure(font=self.ui_label_font); self.release_label.configure(text=self.texts["release_label"], font=self.ui_label_font); self.vib_r_label.configure(font=self.ui_label_font)
        self.render_mode_title_label.configure(text=self.texts["render_mode_title"], font=self.ui_header_font)
        self.pianotiles_switch.configure(text=self.texts["pianotiles_mode_switch"], font=self.ui_label_font)
        self.mode_switch.configure(text=self.texts["solo_mode_switch"], font=self.ui_label_font)
        # 【新增功能】更新新开关的文本和字体
        self.dynamic_range_switch.configure(text=self.texts["dynamic_range_switch"], font=self.ui_label_font)
        self.text_info_title_label.configure(text=self.texts["text_info_title"], font=self.ui_header_font); self.song_name_label.configure(text=self.texts["song_name_label"], font=self.ui_label_font)
        self.song_name_entry.configure(placeholder_text=self.texts["song_name_placeholder"], font=self.ui_label_font); self.author_name_label.configure(text=self.texts["author_name_label"], font=self.ui_label_font); self.author_name_entry.configure(placeholder_text=self.texts["author_name_placeholder"], font=self.ui_label_font)
        self.soundscape_title_label.configure(text=self.texts["soundscape_title"], font=self.ui_header_font); self.soundscape_switch.configure(text=self.texts["soundscape_switch"], font=self.ui_label_font); self.ss_density_label.configure(text=self.texts["ss_density_label"], font=self.ui_label_font); self.ss_gain_label.configure(text=self.texts["ss_gain_label"], font=self.ui_label_font)
        self.render_button.configure(text=self.texts["render_button_text"], font=self.ui_big_button_font); self.progress_label.configure(text=self.texts["status_ready"], font=self.ui_label_font)
    
    def toggle_solo_options(self):
        if self.mode_switch.get():
            self.pianotiles_switch.deselect()
            self.pianotiles_options_frame.grid_remove()
            self.pianotiles_master_frame.configure(fg_color="transparent")
        
    def toggle_pianotiles_options(self):
        if self.pianotiles_switch.get(): 
            self.mode_switch.deselect() # 钢琴块模式和独奏模式互斥
            self.pianotiles_options_frame.grid()
            self.pianotiles_master_frame.configure(fg_color=("gray90", "gray19"))
        else: 
            self.pianotiles_options_frame.grid_remove()
            self.pianotiles_master_frame.configure(fg_color="transparent")
    
    def save_preset(self):
        dialog = ctk.CTkInputDialog(text=self.texts["save_preset_dialog_text"], title=self.texts["save_preset_dialog_title"]); preset_name = dialog.get_input()
        if not preset_name: return
        color_mode_en_val = "Notes as White" if self.color_mode_var.get() in [LANGUAGES[lang]["notes_white"] for lang in LANGUAGES] else "Notes as Black"
        preset_data = {'note_height': self.note_height_slider.get(), 'v_compress': self.v_compress_slider.get(),'fade_in': self.fade_in_slider.get(), 'fade_out': self.fade_out_slider.get(),'vib_max': self.vib_max_entry.get() or str(DEFAULT_VIBRATION_MAX_INTENSITY),'vib_a': self.vib_a_slider.get(), 'vib_d': self.vib_d_slider.get(),'vib_s': self.vib_s_slider.get(), 'vib_r': self.vib_r_slider.get(), 'color_mode_en': color_mode_en_val}
        if not os.path.exists(PRESETS_DIR): os.makedirs(PRESETS_DIR)
        with open(os.path.join(PRESETS_DIR, f"{preset_name}.json"), 'w') as f: json.dump(preset_data, f, indent=4)
        self.load_presets(); self.progress_label.configure(text=self.texts["preset_saved_status"].format(name=preset_name))

    def load_presets(self):
        if not os.path.exists(PRESETS_DIR) or not any(f.endswith('.json') for f in os.listdir(PRESETS_DIR)):
            self.preset_menu.configure(values=[self.texts["no_presets_available"]]); self.preset_menu.set(self.texts["no_presets_available"]); return
        presets = [f.replace('.json', '') for f in os.listdir(PRESETS_DIR) if f.endswith('.json')]
        self.preset_menu.configure(values=[self.texts["load_preset"]] + presets); self.preset_menu.set(self.texts["load_preset"])

    def apply_preset(self, preset_name):
        if any(preset_name == val for lang in LANGUAGES.values() for val in [lang["no_presets_available"], lang["load_preset"]]): return
        with open(os.path.join(PRESETS_DIR, f"{preset_name}.json"), 'r') as f: preset_data = json.load(f)
        self.note_height_slider.set(preset_data.get('note_height', DEFAULT_NOTE_HEIGHT)); self.v_compress_slider.set(preset_data.get('v_compress', DEFAULT_VERTICAL_COMPRESSION)); self.fade_in_slider.set(preset_data.get('fade_in', DEFAULT_FADE_IN)); self.fade_out_slider.set(preset_data.get('fade_out', DEFAULT_FADE_OUT)); self.vib_max_entry.delete(0, 'end'); self.vib_max_entry.insert(0, preset_data.get('vib_max', str(DEFAULT_VIBRATION_MAX_INTENSITY))); self.vib_a_slider.set(preset_data.get('vib_a', DEFAULT_VIBRATION_ATTACK)); self.vib_d_slider.set(preset_data.get('vib_d', DEFAULT_VIBRATION_DECAY)); self.vib_s_slider.set(preset_data.get('vib_s', DEFAULT_VIBRATION_SUSTAIN)); self.vib_r_slider.set(preset_data.get('vib_r', DEFAULT_VIBRATION_RELEASE));
        color_mode_en_val = preset_data.get('color_mode_en', "Notes as Black")
        if color_mode_en_val == "Notes as White": self.color_mode_var.set(self.texts["notes_white"]);
        else: self.color_mode_var.set(self.texts["notes_black"])
        for widget, value in [(self.note_height_label, f"{self.note_height_slider.get():.1f} px"), (self.v_compress_label, f"{self.v_compress_slider.get()*100:.0f}%"), (self.fade_in_label, f"{self.fade_in_slider.get():.2f} s"), (self.fade_out_label, f"{self.fade_out_slider.get():.2f} s"), (self.vib_a_label, f"{self.vib_a_slider.get():.3f}s"), (self.vib_d_label, f"{self.vib_d_slider.get():.3f}s"), (self.vib_s_label, f"{self.vib_s_slider.get()*100:.0f}%"), (self.vib_r_label, f"{self.vib_r_slider.get():.3f}s")]: widget.configure(text=value)

    def select_midi(self): self.midi_path = filedialog.askopenfilename(title="Select MIDI", filetypes=(("MIDI", "*.mid *.midi"),)); self.midi_label.configure(text=os.path.basename(self.midi_path) or self.texts["not_selected"])
    def select_audio(self): self.audio_path = filedialog.askopenfilename(title="Select Audio", filetypes=(("Audio", "*.mp3 *.wav"),)); self.audio_label.configure(text=os.path.basename(self.audio_path) or self.texts["not_selected"])
    def select_output_dir(self): 
        selected_dir = filedialog.askdirectory(title="Select Output Directory", initialdir=self.output_dir)
        if selected_dir:
            self.output_dir = selected_dir
            self.output_dir_label.configure(text=self.output_dir)
    
    def start_render(self):
        if not self.midi_path or not self.audio_path: self.progress_label.configure(text=self.texts["error_file_not_selected"]); return
        self.render_button.configure(state="disabled"); render_thread = threading.Thread(target=self.render_backend); render_thread.start()
    
    def update_progress(self, value, text): self.progress_bar.set(value); self.progress_label.configure(text=text)
    
    def render_backend(self):
        try:
            color_mode_en = "Notes as White" if self.color_mode_var.get() in [LANGUAGES[lang]["notes_white"] for lang in LANGUAGES] else "Notes as Black"
            params = {
                'width': int(self.width_entry.get() or DEFAULT_WIDTH), 'height': int(self.height_entry.get() or DEFAULT_HEIGHT),
                'user_bpm': float(self.bpm_entry.get()) if self.bpm_entry.get() else DEFAULT_BPM,
                'measures_per_page': int(self.measures_entry.get() or DEFAULT_MEASURES),
                'note_height': self.note_height_slider.get(),'v_compress': self.v_compress_slider.get(),
                'fade_in': self.fade_in_slider.get(), 'fade_out': self.fade_out_slider.get(),
                'solo_mode': self.mode_switch.get(), 'pianotiles_mode': self.pianotiles_switch.get(),
                'enable_soundscape': self.soundscape_switch.get(), 'color_mode_en': color_mode_en, 
                'song_name': self.song_name_entry.get(), 'author_name': self.author_name_entry.get(), 
                'vib_max': float(self.vib_max_entry.get() or DEFAULT_VIBRATION_MAX_INTENSITY),
                'vib_a': self.vib_a_slider.get(), 'vib_d': self.vib_d_slider.get(),
                'vib_s': self.vib_s_slider.get(), 'vib_r': self.vib_r_slider.get(), 
                'ss_downsample': int(self.ss_density_slider.get()), 'ss_gain': self.ss_gain_slider.get(),
                'final_video_name': os.path.join(self.output_dir, f"{sanitize_filename(os.path.splitext(os.path.basename(self.midi_path))[0])}_Visualized.mp4"),
                # 【新增功能】将新开关的状态传递给后端
                'dynamic_range_mode': self.dynamic_range_switch.get()
            }
            
            self.update_progress(0, self.texts["status_parsing_midi"])
            notes, default_bpm, time_sig, song_duration = parse_midi(self.midi_path)
            if not notes: raise Exception(self.texts["error_midi_parse_failed"])
            # 确保 time_sig 是元组格式
            if not isinstance(time_sig, tuple) or len(time_sig) < 2:
                time_sig = (4, 4)  # 默认 4/4 拍
            params['time_sig_info'] = (time_sig, (60.0 / (params['user_bpm'] or default_bpm)) * time_sig[0])
            if params['user_bpm'] is None: params['user_bpm'] = default_bpm
            if params['user_bpm'] != default_bpm:
                ratio = default_bpm / params['user_bpm'];
                for note in notes: note['start'] *= ratio; note['duration'] *= ratio
                song_duration *= ratio

            total_frames = math.ceil(song_duration * 60)
            # 在后台线程初始化 pygame（使用 dummy driver 避免显示问题）
            # pygame.get_init() 在新版本中返回布尔值，不是元组
            init_result = pygame.get_init()
            if isinstance(init_result, tuple):
                is_init = init_result[0]
            else:
                is_init = bool(init_result)
            if not is_init:
                pygame.init()
            if not pygame.font.get_init():
                pygame.font.init()

            y, sr = None, None
            if params['enable_soundscape'] and params['pianotiles_mode']:
                self.update_progress(0.01, "加载音频波形..."); y, sr = librosa.load(self.audio_path, sr=44100, mono=False)
                if y.ndim == 1: y = np.vstack([y, np.roll(y, int(sr*0.005))])
            
            if params['color_mode_en'] == 'Notes as White': PRIMARY_COLOR, SECONDARY_COLOR = (255, 255, 255), (0, 0, 0)
            else: PRIMARY_COLOR, SECONDARY_COLOR = (0, 0, 0), (255, 255, 255)
            C_NOTE, C_MAIN_BG, C_PIANO_BLOCK_BG, C_TEXT = PRIMARY_COLOR, PRIMARY_COLOR, SECONDARY_COLOR, SECONDARY_COLOR
            C_INACTIVE_PAGE_NOTE, C_NON_PIANO_BG = (200,200,200), (230, 230, 230)
            # 使用绝对路径保存临时视频文件
            silent_output_path = os.path.join(self.output_dir, "silent_output.mp4")
            screen = pygame.Surface((params['width'], params['height'])); video_writer = cv2.VideoWriter(silent_output_path, cv2.VideoWriter_fourcc(*'mp4v'), 60, (params['width'], params['height']))
            
            fade_surface = None
            if params['pianotiles_mode']:
                render_area_height = params['height'] * 0.75; piano_rect_width = params['width'] * 0.5; piano_rect_height = piano_rect_width / GOLDEN_RATIO; left_margin = params['width'] / 8; piano_rect_y = (render_area_height - piano_rect_height) / 2
                piano_rect = pygame.Rect(left_margin, piano_rect_y, piano_rect_width, piano_rect_height)
                if params['enable_soundscape']:
                    ss_margin_top = piano_rect.height * 0.1; ss_margin_bottom = params['height'] * 0.1; ss_top = piano_rect.bottom + ss_margin_top; ss_height = params['height'] - ss_top - ss_margin_bottom
                    ss_width = piano_rect.width * 0.8; ss_left = piano_rect.left + (piano_rect.width - ss_width) / 2
                    soundscape_rect = pygame.Rect(ss_left, ss_top, ss_width, ss_height)
                    fade_surface = pygame.Surface(screen.get_size()); fade_surface.set_alpha(35); fade_surface.fill(C_MAIN_BG)
                
                try:
                    font_regular = resource_path('SourceHanSansSC-Regular.otf'); font_bold = resource_path('SourceHanSansSC-Bold.otf')
                    font_song = pygame.font.Font(font_regular, int(params['height'] * 0.04)); font_author = pygame.font.Font(font_bold, int(params['height'] * 0.08))
                except Exception as e:
                    print(f"渲染字体加载失败: {e}. 使用后备字体."); font_song = pygame.font.SysFont("sans", int(params['height'] * 0.04)); font_author = pygame.font.SysFont("sans", int(params['height'] * 0.08), bold=True)
                song_surf = font_song.render(params['song_name'], True, C_TEXT) if params['song_name'] else None; author_surf = font_author.render(params['author_name'], True, C_TEXT) if params['author_name'] else None

            # 【新增功能】如果不是动态模式，则在渲染前计算好全局音域
            global_min_p, global_max_p = None, None
            if params['pianotiles_mode'] and not params['dynamic_range_mode']:
                all_pitches = [n['pitch'] for n in notes]
                if all_pitches: global_min_p, global_max_p = min(all_pitches), max(all_pitches)

            for frame_index in range(total_frames):
                progress = (frame_index + 1) / total_frames; self.update_progress(progress, self.texts["status_rendering"].format(progress=progress)); current_song_time = frame_index / 60.0

                if params['enable_soundscape'] and fade_surface is not None: screen.blit(fade_surface, (0,0))
                else: screen.fill(C_MAIN_BG)

                if params['pianotiles_mode']:
                    pygame.draw.rect(screen, C_PIANO_BLOCK_BG, piano_rect)
                    space_between = (params['width'] - piano_rect.right) * (1.0 - 0.42) * 0.5; text_column_center_x = piano_rect.right + space_between
                    if author_surf:
                        author_y_center = piano_rect.bottom - (piano_rect.height / GOLDEN_RATIO); author_rect = author_surf.get_rect(centerx=text_column_center_x, centery=author_y_center); screen.blit(author_surf, author_rect)
                        if song_surf: song_rect = song_surf.get_rect(centerx=text_column_center_x); song_rect.top = piano_rect.top; screen.blit(song_surf, song_rect)

                    # --- 【核心修改】在这里实现动态音域逻辑 ---
                    if isinstance(params.get('time_sig_info'), tuple) and len(params['time_sig_info']) >= 2:
                        page_duration = params['time_sig_info'][1]
                    else:
                        # 如果 time_sig_info 无效，使用默认值
                        bpm = params.get('user_bpm', 120)
                        page_duration = (60.0 / bpm) * 4  # 默认 4/4 拍
                    current_page_index = math.floor(current_song_time / page_duration)
                    page_start_time = current_page_index * page_duration
                    page_end_time = page_start_time + page_duration

                    min_p, max_p = None, None
                    if params['dynamic_range_mode']:
                        # 动态模式: 只看当前小节的音符
                        notes_in_measure = [n['pitch'] for n in notes if n['start'] < page_end_time and n['start'] + n['duration'] > page_start_time]
                        if notes_in_measure:
                            min_p, max_p = min(notes_in_measure), max(notes_in_measure)
                    else:
                        # 静态模式: 使用全局音域
                        min_p, max_p = global_min_p, global_max_p

                    active_notes = [n for n in notes if n['start'] - params['fade_in'] <= current_song_time < n['start'] + n['duration'] + params['fade_out']]
                    if active_notes and min_p is not None:
                        pitch_range = max(max_p - min_p + 1, 5) 
                        v_spacing = (piano_rect.height * params['v_compress']) / pitch_range
                        y_offset = (piano_rect.height - ((pitch_range - 1) * v_spacing)) / 2
                        for note in active_notes:
                            color, _ = get_note_attrs(current_song_time, note, params, C_NOTE, C_PIANO_BLOCK_BG)
                            if color: 
                                y_pos = piano_rect.top + y_offset + (max_p - note['pitch']) * v_spacing
                                note_bar = pygame.Rect(piano_rect.left, y_pos - params['note_height'] / 2, piano_rect.width, params['note_height'])
                                pygame.draw.rect(screen, color, note_bar)
                    
                    if params['enable_soundscape'] and y is not None:
                        start_sample = int(current_song_time * sr); samples_per_frame = int(sr / 60); end_sample = start_sample + samples_per_frame
                        if end_sample <= y.shape[1]:
                            gain = params['ss_gain']; downsample = params['ss_downsample']
                            samples_l = y[0, start_sample:end_sample:downsample] * gain; samples_r = y[1, start_sample:end_sample:downsample] * gain
                            points = np.column_stack(((samples_l - samples_r), (samples_l + samples_r))) / math.sqrt(2)
                            points_transformed = np.column_stack((soundscape_rect.centerx + points[:,0] * soundscape_rect.width/2, soundscape_rect.centery - points[:,1] * soundscape_rect.height/2))
                            if points_transformed.shape[0] > 1:
                                final_color = (255,255,255) if C_MAIN_BG == (0,0,0) else (0,0,0)
                                pygame.draw.aalines(screen, final_color, False, points_transformed.tolist())
                else:
                    screen.fill(C_NON_PIANO_BG)
                    if params['solo_mode']:
                        active_notes = [n for n in notes if n['start'] - params['fade_in'] <= current_song_time < n['start'] + n['duration'] + params['fade_out']]
                        if active_notes:
                            min_p = min(n['pitch'] for n in active_notes); max_p = max(n['pitch'] for n in active_notes); pitch_range = max_p - min_p + 1
                            canvas_dim = min(params['width'], params['height']) * 0.8; canvas_rect = pygame.Rect((params['width'] - canvas_dim) / 2, (params['height'] - canvas_dim) / 2, canvas_dim, canvas_dim)
                            display_height = canvas_rect.height * params['v_compress']; v_spacing = display_height / pitch_range if pitch_range > 1 else 0
                            y_offset = (canvas_rect.height - ((pitch_range - 1) * v_spacing)) / 2
                            for note in active_notes:
                                x = canvas_rect.left + canvas_rect.width * 0.1; width = note['duration'] * (canvas_rect.width / 4); y_pos = canvas_rect.top + y_offset + (max_p - note['pitch']) * v_spacing
                                color, vib_intensity = get_note_attrs(current_song_time, note, params, C_NOTE, C_INACTIVE_PAGE_NOTE)
                                if color: pygame.draw.rect(screen, color, (x, y_pos + random.uniform(-vib_intensity, vib_intensity), width, params['note_height']))
                    else:
                        if isinstance(params.get('time_sig_info'), tuple) and len(params['time_sig_info']) >= 2:
                            page_duration = params['time_sig_info'][1]
                        else:
                            # 如果 time_sig_info 无效，使用默认值
                            bpm = params.get('user_bpm', 120)
                            page_duration = (60.0 / bpm) * 4  # 默认 4/4 拍
                        current_page = math.floor(current_song_time / page_duration)
                        time_on_page = current_song_time % page_duration
                        page_start_time = current_page * page_duration
                        notes_on_page = [n for n in notes if n['start'] < page_start_time + page_duration and n['start'] + n['duration'] > page_start_time]
                        if notes_on_page:
                            page_min_p = min(n['pitch'] for n in notes_on_page); page_max_p = max(n['pitch'] for n in notes_on_page); page_pitch_range = page_max_p - page_min_p + 1
                            canvas_dim = min(params['width'], params['height']) * 0.8; canvas_rect = pygame.Rect((params['width'] - canvas_dim) / 2, (params['height'] - canvas_dim) / 2, canvas_dim, canvas_dim)
                            display_height = canvas_rect.height * params['v_compress']; vertical_spacing = display_height / page_pitch_range if page_pitch_range > 1 else 0
                            y_offset = (canvas_rect.height - ((page_pitch_range - 1) * vertical_spacing)) / 2
                            for note in notes_on_page:
                                playhead_relative_time = time_on_page - (note['start'] - page_start_time)
                                color, vib_intensity = get_note_attrs(playhead_relative_time, note, params, C_NOTE, C_INACTIVE_PAGE_NOTE, is_page_mode=True)
                                if color:
                                    x_on_canvas = ((note['start'] - page_start_time) / page_duration) * canvas_rect.width; width_on_canvas = (note['duration'] / page_duration) * canvas_rect.width; y_on_canvas = (page_max_p - note['pitch']) * vertical_spacing
                                    final_x = canvas_rect.left + x_on_canvas; final_y = canvas_rect.top + y_offset + y_on_canvas + random.uniform(-vib_intensity, vib_intensity)
                                    pygame.draw.rect(screen, color, (final_x, final_y, width_on_canvas, params['note_height']))

                frame = pygame.surfarray.array3d(screen); frame = frame.transpose([1, 0, 2]); frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR); video_writer.write(frame)
            
            video_writer.release(); pygame.quit()
            self.update_progress(1, self.texts["status_merging_audio"])
            # 使用绝对路径读取临时视频文件
            silent_output_path = os.path.join(self.output_dir, "silent_output.mp4")
            if not os.path.exists(silent_output_path):
                raise FileNotFoundError(f"临时视频文件未找到: {silent_output_path}")
            video_clip = VideoFileClip(silent_output_path); audio_clip = AudioFileClip(self.audio_path)
            # 新版本 moviepy 使用 subclipped 而不是 subclip，使用 with_audio 而不是 set_audio
            max_duration = min(video_clip.duration, audio_clip.duration)
            try:
                # 尝试使用新版本的 subclipped
                final_audio = audio_clip.subclipped(0, max_duration)
            except (AttributeError, TypeError):
                # 如果 subclipped 不存在或参数不对，尝试使用切片语法
                final_audio = audio_clip[:max_duration]
            # 新版本 moviepy 使用 with_audio 而不是 set_audio
            try:
                final_clip = video_clip.with_audio(final_audio)
            except AttributeError:
                # 如果 with_audio 不存在，尝试使用旧版本的 set_audio
                final_clip = video_clip.set_audio(final_audio)
            # 确保输出文件名是安全的
            output_path = params['final_video_name']
            # 如果路径包含特殊字符，再次清理
            output_dir = os.path.dirname(output_path)
            output_filename = sanitize_filename(os.path.basename(output_path))
            output_path = os.path.join(output_dir, output_filename)
            
            # 使用临时目录写入，避免 moviepy 的临时文件问题
            import tempfile
            import shutil
            temp_dir = self.moviepy_temp_dir
            # 生成安全的临时文件名
            temp_basename = sanitize_filename(os.path.splitext(os.path.basename(output_path))[0])
            temp_output = os.path.join(temp_dir, f"midiart_temp_{temp_basename}.mp4")
            temp_audio = os.path.join(temp_dir, f"midiart_temp_{temp_basename}_audio.m4a")
            
            try:
                # 先写入到临时目录，明确指定临时音频文件位置
                final_clip.write_videofile(
                    temp_output, 
                    codec='libx264', 
                    audio_codec='aac', 
                    logger=None,
                    temp_audiofile=temp_audio
                )
                # 写入成功后移动到最终位置
                if os.path.exists(temp_output):
                    if os.path.exists(output_path):
                        os.remove(output_path)
                    # 使用 shutil.move 确保跨文件系统也能工作
                    shutil.move(temp_output, output_path)
                    output_path = output_path  # 更新为最终路径
            except Exception as write_error:
                # 如果临时目录写入失败，尝试直接写入最终位置
                # 清理临时文件
                for temp_file in [temp_output, temp_audio]:
                    if os.path.exists(temp_file):
                        try:
                            os.remove(temp_file)
                        except:
                            pass
                # 直接写入最终文件，使用临时音频文件
                try:
                    final_clip.write_videofile(
                        output_path, 
                        codec='libx264', 
                        audio_codec='aac', 
                        logger=None,
                        temp_audiofile=temp_audio
                    )
                except:
                    # 如果指定 temp_audiofile 失败，尝试不指定
                    final_clip.write_videofile(output_path, codec='libx264', audio_codec='aac', logger=None)
            
            # 清理临时音频文件
            if os.path.exists(temp_audio):
                try:
                    os.remove(temp_audio)
                except:
                    pass
            
            self.update_progress(1, self.texts["status_genesis_complete"].format(filename=output_path))
        except Exception as e:
            self.update_progress(0, self.texts["error_generic"].format(error=e)); import traceback; traceback.print_exc()
        finally:
            self.render_button.configure(state="normal");
            # 清理临时文件（使用绝对路径）
            silent_output_path = os.path.join(self.output_dir, "silent_output.mp4")
            if os.path.exists(silent_output_path): os.remove(silent_output_path)

def parse_midi(midi_file):
    mid = mido.MidiFile(midi_file); notes = []; ticks_per_beat = mid.ticks_per_beat or 480; tempo = 500000; time_signature = (4, 4)
    for msg in mid:
        if msg.type == 'set_tempo': tempo = msg.tempo; break
    for msg in mid:
        if msg.type == 'time_signature': 
            # 确保 time_signature 是元组格式
            if hasattr(msg, 'numerator') and hasattr(msg, 'denominator'):
                time_signature = (msg.numerator, msg.denominator)
            break
    # 确保 time_signature 始终是元组
    if not isinstance(time_signature, tuple) or len(time_signature) < 2:
        time_signature = (4, 4)
    bpm = mido.tempo2bpm(tempo); seconds_per_tick = tempo / (1000000.0 * ticks_per_beat); has_notes = False
    for track in mid.tracks:
        current_ticks = 0; open_notes = {}
        for msg in track:
            current_ticks += msg.time; time_sec = current_ticks * seconds_per_tick
            if msg.type == 'note_on' and msg.velocity > 0: has_notes = True; open_notes[(msg.channel, msg.note)] = {'start': time_sec}
            elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                key = (msg.channel, msg.note);
                if key in open_notes:
                    start_info = open_notes.pop(key); notes.append({'pitch': msg.note, 'start': start_info['start'], 'duration': time_sec - start_info['start'], 'id': (start_info['start'], msg.note)})
    if not has_notes: return None, None, None, None
    song_duration = max(n['start'] + n['duration'] for n in notes) if notes else 0
    return notes, bpm, time_signature, song_duration

def get_note_attrs(current_time, note, params, active_color, inactive_color, is_page_mode=False):
    note_start_time = note['start'] if not is_page_mode else 0; note_duration = note['duration']
    time_since_start = current_time - note_start_time; time_from_end = current_time - (note_start_time + note_duration)
    vib_intensity = 0
    if not params['pianotiles_mode']:
        sustain_level = params['vib_max'] * params['vib_s']
        if 0 <= time_since_start < params['vib_a'] and params['vib_a'] > 0: vib_intensity = params['vib_max'] * (time_since_start / params['vib_a'])
        elif params['vib_a'] <= time_since_start < params['vib_a'] + params['vib_d'] and params['vib_d'] > 0: vib_intensity = params['vib_max'] - (params['vib_max'] - sustain_level) * ((time_since_start - params['vib_a']) / params['vib_d'])
        elif params['vib_a'] + params['vib_d'] <= time_since_start <= note_duration: vib_intensity = sustain_level
        elif 0 < time_from_end < params['vib_r'] and params['vib_r'] > 0: vib_intensity = sustain_level * (1 - (time_from_end / params['vib_r']))
    color = None; time_to_start = note_start_time - current_time if is_page_mode else note['start'] - current_time
    is_active = time_to_start <= 0 and time_from_end < 0
    if params['fade_in'] > 0 and -params['fade_in'] < time_to_start <= 0: color = lerp_color(inactive_color, active_color, 1.0 - (-time_to_start / params['fade_in']))
    elif is_active: color = active_color
    elif params['fade_out'] > 0 and 0 <= time_from_end < params['fade_out']: color = lerp_color(inactive_color, active_color, 1.0 - (time_from_end / params['fade_out']))
    elif not params['solo_mode'] and is_page_mode and not params.get('pianotiles_mode'): color = inactive_color
    return color, vib_intensity

def lerp_color(c1, c2, factor): return tuple(int(c1[i] + (c2[i] - c1[i]) * factor) for i in range(3))

if __name__ == "__main__":
    try:
        if sys.platform == "darwin": ctk.set_appearance_mode("System")
        app = App()
        app.mainloop()
    except Exception as e:
        # 在打包后的应用中，将错误写入日志文件
        import traceback
        error_msg = f"应用启动失败: {e}\n{traceback.format_exc()}"
        print(error_msg)
        # 尝试写入日志文件
        try:
            log_path = os.path.join(os.path.expanduser("~"), "MidiArt_Pro_error.log")
            with open(log_path, "w", encoding="utf-8") as f:
                f.write(error_msg)
            print(f"错误日志已保存到: {log_path}")
        except:
            pass
        # 如果是打包后的应用，显示错误对话框
        try:
            import tkinter.messagebox as msgbox
            root = ctk.CTk()
            root.withdraw()
            msgbox.showerror("MidiArt Pro 错误", f"应用启动失败:\n{str(e)}\n\n详细信息请查看控制台或日志文件。")
        except:
            pass
        raise
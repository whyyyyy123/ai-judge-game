# 🔥 火眼金睛 AI辨伪大挑战

南开大学人工智能学院权益部 · AI游园会 2026.4.9

## 玩法

考验你分辨 AI 生成内容的能力！图片、音频、文字三种题型，看谁火眼金睛。

## 运行方法

```bash
git clone https://github.com/whyyyyy123/ai-judge-game.git
cd ai-judge-game
python3 server.py
```

然后用浏览器打开终端显示的地址（局域网内所有设备均可访问）。

## 目录结构

```
├── index.html          # 前端游戏页面
├── server.py           # 局域网 HTTP 服务器
├── bgm.mp3             # 背景音乐
├── scores.json         # 排行榜数据（自动生成）
└── media/
    ├── ai/             # AI 生成图片题
    ├── notai/          # 真人图片题
    ├── audio_ai/       # AI 生成音频题
    └── audio_human/    # 真人音频题
```

## 环境要求

- Python 3.6+
- 现代浏览器（Chrome / Firefox / Edge）

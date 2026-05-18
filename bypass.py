import os
import site
import sys
import time
import ctypes
import subprocess
import base64

hinhnen = """
\033[36m
    ▄████████  ▄█   ▄█          ▄████████ ████████▄     ▄████████ 
   ███    ███ ███  ███         ███    ███ ███   ▀███   ███    ███ 
   ███    █▀  ███▌ ███         ███    █▀  ███    ███   ███    █▀  
  ▄███▄▄▄     ███▌ ███        ▄███▄▄▄     ███    ███  ▄███▄▄▄     
 ▀▀███▀▀▀     ███▌ ███       ▀▀███▀▀▀     ███    ███ ▀▀███▀▀▀     
   ███    █▄  ███  ███         ███    █▄  ███    ███   ███    █▄  
   ███    ███ ███  ███▌    ▄   ███    ███ ███   ▄███   ███    ███ 
   ██████████ █▀   █████▄▄██   ██████████ ████████▀    ██████████ 
                  ▀                                                
\033[0m
"""
print(hinhnen)

text = "[ GLORYVN HOOK SYSTEM - GMAIL EDITION ]"
colors = ['\033[92m', '\033[96m', '\033[94m', '\033[92m']
for i, char in enumerate(text):
    sys.stdout.write(colors[i % len(colors)] + char + '\033[0m')
    sys.stdout.flush()
    time.sleep(0.05)
print("\n")

print("\033[92m-> Author: GiaBao (đã bị GloryVN đập vỡ mồm)\033[0m")
print("\033[94m[INFO] https://www.facebook.com/giabaodropship\033[0m\n")
print(f"\033[96m[INFO] Python version: {sys.version.split()[0]}\033[0m")

HOOK_CODE_NANGCAP = r'''
import os, sys, ctypes, threading, time, builtins, logging, json, random, string
from ctypes import wintypes, c_int, c_void_p, c_char_p, POINTER, Structure, byref, cast
from ctypes.wintypes import DWORD, HANDLE, LPVOID, BOOL
from ctypes import c_size_t as SIZE_T

kernel32 = ctypes.windll.kernel32
ntdll = ctypes.windll.ntdll

LOG_FILE = os.path.join(os.getcwd(), "bug_advanced.txt")

def write_log(msg):
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{time.time()}] {msg}\n")
    except:
        pass

write_log("===== ADVANCED HOOK LOADED =====")

class MEMORY_BASIC_INFORMATION(Structure):
    _fields_ = [
        ("BaseAddress", LPVOID),
        ("AllocationBase", LPVOID),
        ("AllocationProtect", DWORD),
        ("RegionSize", SIZE_T),
        ("State", DWORD),
        ("Protect", DWORD),
        ("Type", DWORD)
    ]

def create_trampoline(src_addr, dst_addr, length=14):
    trampoline = bytearray([0x48, 0xB8]) + (dst_addr).to_bytes(8, 'little') + bytearray([0xFF, 0xE0])
    trampoline.extend(b'\x90' * (length - len(trampoline)))
    return bytes(trampoline)

def hook_iat(module_name, func_name, hook_func):
    try:
        import pefile
        process_handle = kernel32.GetCurrentProcess()
        module_handle = kernel32.GetModuleHandleW(module_name)
        if not module_handle:
            module_handle = kernel32.LoadLibraryW(module_name)
        pe = pefile.PE(data=bytes(ctypes.string_at(module_handle, 0x100000)))
        for entry in pe.DIRECTORY_ENTRY_IMPORT:
            for imp in entry.imports:
                if imp.name and imp.name.decode() == func_name:
                    iat_addr = module_handle + imp.address
                    old_protect = DWORD()
                    kernel32.VirtualProtect(iat_addr, 8, 0x40, byref(old_protect))
                    ctypes.cast(iat_addr, ctypes.POINTER(c_void_p)).contents.value = cast(hook_func, c_void_p).value
                    kernel32.VirtualProtect(iat_addr, 8, old_protect, byref(old_protect))
                    write_log(f"IAT Hook success: {func_name}")
                    return True
    except Exception as e:
        write_log(f"IAT Hook failed: {str(e)}")
    return False

def install_windivert_redirect():
    try:
        windivert = ctypes.WinDLL("windivert.dll")
        handle = windivert.WinDivertOpen("true", 0, 0)
        if handle:
            write_log("WinDivert proxy installed")
            def capture():
                packet = ctypes.create_string_buffer(65535)
                addr = ctypes.create_string_buffer(40)
                while True:
                    recv = windivert.WinDivertRecv(handle, packet, 65535, byref(addr))
                    if recv:
                        write_log(f"[WinDivert] Packet len: {recv}")
            threading.Thread(target=capture, daemon=True).start()
            return True
    except:
        pass
    return False

def anti_debug():
    if kernel32.IsDebuggerPresent():
        write_log("Debugger detected!")
        kernel32.ExitProcess(0)
    peb = ctypes.cast(kernel32.GetCurrentProcess(), c_void_p).value
    nt_global_flag = ctypes.cast(peb + 0xBC, ctypes.POINTER(c_int)).contents.value
    if nt_global_flag & 0x70:
        write_log("NtGlobalFlag tampered")
        kernel32.ExitProcess(0)
    start = time.perf_counter()
    _ = [i**2 for i in range(5000000)]
    elapsed = time.perf_counter() - start
    if elapsed < 0.1:
        write_log("Sandbox detected")
        kernel32.ExitProcess(0)

def install_persistence():
    try:
        key = ctypes.c_void_p()
        kernel32.RegOpenKeyExW(0x80000001, "Software\\Microsoft\\Windows\\CurrentVersion\\Run", 0, 0x20006, byref(key))
        current_exe = sys.executable
        kernel32.RegSetValueExW(key, "PythonHook", 0, 1, current_exe, len(current_exe)*2)
        kernel32.RegCloseKey(key)
        write_log("Persistence installed")
    except:
        pass

def advanced_install():
    anti_debug()
    install_windivert_redirect()
    install_persistence()
    
    try:
        import urllib3
        orig_request = urllib3.connectionpool.HTTPConnectionPool.urlopen
        
        def hooked_urlopen(self, method, url, *args, **kwargs):
            write_log(f"[FULL HOOK] {method} {url}")
            print(f"[FULL HOOK] {method} {url}")
            return orig_request(self, method, url, *args, **kwargs)
        
        urllib3.connectionpool.HTTPConnectionPool.urlopen = hooked_urlopen
        write_log("urllib3 hook installed")
    except Exception as e:
        write_log(f"urllib3 hook failed: {str(e)}")
    
    try:
        import requests
        orig_request_req = requests.Session.request
        def hooked_request(self, method, url, *args, **kwargs):
            write_log(f"[REQUESTS] {method} {url}")
            print(f"[REQUESTS] {method} {url}")
            return orig_request_req(self, method, url, *args, **kwargs)
        requests.Session.request = hooked_request
        write_log("requests hook installed")
    except Exception as e:
        write_log(f"requests hook failed: {str(e)}")
    
    write_log("Advanced hooks fully loaded")
    return True

advanced_install()
'''

def get_sitecustomize_path():
    user_site = site.getusersitepackages()
    os.makedirs(user_site, exist_ok=True)
    return os.path.join(user_site, "hook_advanced.py")

def tai_hook_nangcap():
    path = get_sitecustomize_path()
    with open(path, "w", encoding="utf-8") as f:
        f.write(HOOK_CODE_NANGCAP)
    
    os.environ['PYTHONPATH'] = site.getusersitepackages() + os.pathsep + os.environ.get('PYTHONPATH', '')
    print("\033[92m[+] Hook file đã được tạo!\033[0m")
    print("\033[96m[!] Để kích hoạt hook, restart Python hoặc import lại module.\033[0m")

def xoa_hook_nangcap():
    path = get_sitecustomize_path()
    if os.path.exists(path):
        os.remove(path)
        print("\033[91m[-] Đã xóa hook.\033[0m")
    else:
        print("\033[93m[!] Không tìm thấy hook.\033[0m")

if __name__ == "__main__":
    print("\n\033[95m1. Cài hook nâng cấp (xuyên hệ thống)")
    print("2. Xóa hook")
    choice = input("\033[93m>> \033[0m")
    if choice == "1":
        tai_hook_nangcap()
    elif choice == "2":
        xoa_hook_nangcap()
    else:
        print("\033[91mChọn cái lòn gì thế?\033[0m")
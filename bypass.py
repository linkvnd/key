import os
import site
import sys

hinhnen = """
 | |/ / |  ____| \ \   / /
 | ' /  | |__     \ \_/ / 
 |  <   |  __|     \   /  
 | . \  | |____     | |   
 |_|\_\ |______|    |_|   

"""
print(hinhnen)
print("\n-> Author: GiaBao")
print("[INFO] https://www.facebook.com/giabaodropship\n")
print(f"[INFO] Python version: {sys.version.split()[0]}")
if sys.version_info < (3, 7):
    print("[!] Python quá cũ, nên dùng 3.8+ trở lên.")
print()

HOOK_CODE = r'''
import os, datetime, sys, builtins, threading

LOG_FILE = os.path.join(os.getcwd(), "bug.txt")
_HOOKS_INSTALLED = False
_INSTALL_LOCK = threading.Lock()

def write_log(t):
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(t + "\n")
    except:
        pass

write_log("\n===== Bypass Anti-Hooking =====\n" + str(datetime.datetime.now()))

def install_requests_hook():
    try:
        if 'requests' in sys.modules:
            requests = sys.modules['requests']

            if hasattr(requests, 'sessions'):
                import requests.sessions

                if not hasattr(requests.sessions.Session.request, '_hooked'):
                    _old_req = requests.sessions.Session.request
                    
                    def new_req(self, method, url, *args, **kwargs):
                        msg = f"[Url] {method} {url}"
                        print(msg)
                        write_log(msg)
                        return _old_req(self, method, url, *args, **kwargs)
                    new_req._hooked = True
                    requests.sessions.Session.request = new_req
                    write_log("✓ Requests hook installed")
                    return True
    except Exception as e:
        write_log(f"✗ Requests hook failed: {str(e)}")
    return False

def install_urllib3_hook():
    try:
        if 'urllib3' in sys.modules:
            import urllib3.connectionpool
            
            if not hasattr(urllib3.connectionpool.HTTPConnectionPool.urlopen, '_hooked'):
                _old_urlopen = urllib3.connectionpool.HTTPConnectionPool.urlopen
                
                def new_urlopen(self, method, url, *args, **kwargs):
                    scheme = "https" if hasattr(self, 'scheme') and self.scheme == "https" else "http"
                    host = getattr(self, 'host', 'unknown')
                    full_url = f"{scheme}://{host}{url}"
                    msg = f"[Urllib3] {method} {full_url}"
                    print(msg)
                    write_log(msg)
                    return _old_urlopen(self, method, url, *args, **kwargs)
                
                new_urlopen._hooked = True
                urllib3.connectionpool.HTTPConnectionPool.urlopen = new_urlopen
                write_log("✓ Urllib3 hook installed")
                return True
    except Exception as e:
        write_log(f"✗ Urllib3 hook failed: {str(e)}")
    return False

def install_hooks(force=False):
    global _HOOKS_INSTALLED
    
    with _INSTALL_LOCK:
        if _HOOKS_INSTALLED and not force:
            return True
        
        requests_ok = install_requests_hook()
        urllib3_ok = install_urllib3_hook()
        
        if requests_ok or urllib3_ok:
            _HOOKS_INSTALLED = True
            
        return _HOOKS_INSTALLED

original_import = builtins.__import__
_IMPORTED_MODULES = set()

def hooked_import(name, *args, **kwargs):
    module = original_import(name, *args, **kwargs)

    if name in ['requests', 'urllib3'] and name not in _IMPORTED_MODULES:
        _IMPORTED_MODULES.add(name)
        write_log(f"Module {name} loaded, checking hooks...")

        def delayed_install():
            import time
            time.sleep(0.1)
            install_hooks()
        
        threading.Thread(target=delayed_install, daemon=True).start()
    
    return module

builtins.__import__ = hooked_import

for mod_name in ['requests', 'urllib3']:
    if mod_name in sys.modules:
        _IMPORTED_MODULES.add(mod_name)
        install_hooks()

class ImportHook:
    def find_module(self, fullname, path=None):
        if fullname in ['requests', 'urllib3'] and fullname not in _IMPORTED_MODULES:
            _IMPORTED_MODULES.add(fullname)
            write_log(f"ImportHook: {fullname} is being imported")
        return None

sys.meta_path.insert(0, ImportHook())

write_log("="*50)
write_log(f"HOOK READY - Already imported: {[m for m in ['requests','urllib3'] if m in sys.modules]}")
write_log("="*50)
'''

HOOK_CODE1 = r'''import hook'''

def get_sitecustomize_path():
    user_site = site.getusersitepackages()
    os.makedirs(user_site, exist_ok=True)
    return os.path.join(user_site, "hook.py")

def get_sitecustomize_path1():
    user_site = site.getusersitepackages()
    os.makedirs(user_site, exist_ok=True)
    return os.path.join(user_site, "inject.pth")

def tai_hook():
    path1 = get_sitecustomize_path()
    path2 = get_sitecustomize_path1()
#    path = path1 + path2
    with open(path1, "w", encoding="utf-8") as f:
        f.write(HOOK_CODE)
    with open(path2, "w", encoding="utf-8") as f:
        f.write(HOOK_CODE1)
    print("Success Hook!")
#    print(f"[+] Hook installed at: {path1}")
#    print(f"[+] Hook installed at: {path2}")

def xoa_hook():
    path1 = get_sitecustomize_path()
    path2 = get_sitecustomize_path1()

    removed = False

    if os.path.exists(path1):
        os.remove(path1)
#        print(f"[+] xoá: {path1}")
        removed = True

    if os.path.exists(path2):
        os.remove(path2)
#        print(f"[+] xoá: {path2}")
        removed = True

    if removed:
        print("[+] Success Hook Removed!")
    else:
        print("[!] No hook found.")

if __name__ == "__main__":
    print("1. Install key")
    print("2. Remove key")
    choice = input(">> ")

    if choice == "1":
        tai_hook()
    elif choice == "2":
        xoa_hook()
    else:
        print("Chọn sai rồi nhóc!")

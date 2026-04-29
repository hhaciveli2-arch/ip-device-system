# collectors/wmic_collector.py
import os
import subprocess
import json
import requests

BACKEND_URL = os.environ.get("BACKEND_URL", "http://127.0.0.1:5000")
API_KEY = os.environ.get("WMIC_API_KEY", "")

def run_wmic(command):
    """WMIC komutunu çalıştır ve çıktıyı döndür"""
    try:
        result = subprocess.check_output(
            ["wmic"] + command.split(),
            stderr=subprocess.STDOUT,
            text=True
        )
        return result.strip()
    except subprocess.CalledProcessError as e:
        print(f"WMIC error: {e.output}")
        return ""

def collect_device_info():
    """WMIC üzerinden cihaz bilgilerini topla"""
    device = {
        "pgm_no": "-",  
        "mudurluk": "-",
        "amirlik": "-",
        "sube": "-",
        "ip_no": run_wmic("nicconfig get IPAddress | findstr /R [0-9]"),
        "mac_adresi": run_wmic("nic get MACAddress"),
        "isletim_sistemi": run_wmic("os get Caption"),
        "pc_markasi": run_wmic("csproduct get Vendor"),
        "pc_modeli": run_wmic("csproduct get Name"),
        "islemci": run_wmic("cpu get Name"),
        "hard_disk": run_wmic("diskdrive get Size"),
        "ram_boyutu": run_wmic("memorychip get Capacity"),
        "bit_tipi": run_wmic("os get OSArchitecture"),
        "ekran_karti": run_wmic("path win32_VideoController get Name"),
        "ses_karti": run_wmic("path win32_SoundDevice get Name"),
        "network_karti": run_wmic("nic get Name"),
        "ana_kart": run_wmic("baseboard get Product"),
        "ekran": "-",
        "yazici": run_wmic("printer get Name"),
        "aciklama": run_wmic("computersystem get Name"),
    }
    return device

def send_to_backend(device):
    """Backend'e POST et"""
    try:
        url = f"{BACKEND_URL}/wmic/upsert"
        headers = {"Content-Type": "application/json"}
        if API_KEY:
            headers["X-API-Key"] = API_KEY
        resp = requests.post(url, json=device, headers=headers)
        print("Gönderim sonucu:", resp.status_code, resp.text)
    except Exception as e:
        print("Backend'e gönderim hatası:", e)

if __name__ == "__main__":
    info = collect_device_info()
    print(json.dumps(info, indent=2, ensure_ascii=False))  # Terminalde gör
    send_to_backend(info)

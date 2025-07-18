import time
import pyotp
from config import Config
import json
from selenium.webdriver.common.by import By

def build_brightdata_proxy() -> dict:
    user = f"{Config.BRIGHTDATA_USER_NAME}-zone-{Config.BRIGHTDATA_ZONE}-country-{Config.PROXY_COUNTRY}-city-{Config.PROXY_CITY}"
    if Config.PROXY_SESSION:
        user += f"-session-{Config.PROXY_SESSION}"
    
    return {
        "mode": "https",
        "host": "brd.superproxy.io",
        "port": 33335,
        "username": user,
        "password": Config.BRIGHTDATA_PASSWORD
    }


def get_ip_proxy(driver) -> str:
    driver.get("https://ipinfo.io/json")
    time.sleep(3)
    resp = driver.find_element(By.TAG_NAME, "pre").text
    data = json.loads(resp)
    proxy_ip = data["ip"]
    print("🧠 Proxy Detected:", data)
    return proxy_ip



def getTOTP(secret_key:str) -> str:
        """Generate a TOTP (One-Time Password) using the secret key"""

        try:
            totp = pyotp.TOTP(secret_key)
            return totp.now()
        except Exception as e:
            raise Exception(
                f"TOTP generation failed", details=e)
        

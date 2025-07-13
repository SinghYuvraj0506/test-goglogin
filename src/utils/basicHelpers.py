import time
import pyotp
from config import Config
import json
from selenium.webdriver.common.by import By


def build_brightdata_proxy(country: str, ip: str = None) -> dict:
    user = f"{Config.BRIGHTDATA_USER_NAME}-zone-{Config.BRIGHTDATA_ZONE}-country-{country}"
    if ip:
        user += f"-ip-{ip}"
    
    # print("proxy user is", user)
    user= "brd-customer-hl_a70b254f-zone-residential_proxy1-country-in-city-delhi-session-mycheck2134"
    
    return {
        "mode": "https",
        "host": "brd.superproxy.io",
        "port": 33335,
        "username": user,
        # "password": Config.BRIGHTDATA_PASSWORD
        "password": "1slwg7840okd"
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
        

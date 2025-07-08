import os
import time

def get_config():
    """
    Gets all the required environment variables and returns them as a dictionary.
    """
    config = {
        "profile_id": os.getenv('GL_PROFILE_ID'),
        "insta_secret_key": os.getenv('INSTA_SECRET_CODE'),
        "insta_username": os.getenv('INSTA_USERNAME'),
        "insta_password": os.getenv('INSTA_PASSWORD'),
        "username": os.getenv('BRIGHTDATA_USER_NAME'),
        "brightdata-zone": os.getenv('BRIGHTDATA_ZONE'),
        "insta_password": os.getenv('INSTA_PASSWORD'),
    }
    
    return config


def build_brightdata_proxy(country: str, ip: str = None) -> dict:
    username = os.getenv('BRIGHTDATA_USER_NAME')

    user = f"{os.getenv('BRIGHTDATA_USER_NAME')}-zone-{os.getenv('BRIGHTDATA_ZONE')}-country-{country}"
    if ip:
        user += f"-ip-{ip}"

    return {
        "mode": "http",
        "host": "brd.superproxy.io",
        "port": 33335,
        "username": user,
        "password": os.getenv('BRIGHTDATA_PASSWORD')
    }


def get_ip_proxy(driver) -> str:
    driver.get("http://lumtest.com/myip.json")
    time.sleep(3)
    resp = driver.find_element(By.TAG_NAME, "pre").text
    data = json.loads(resp)
    proxy_ip = data["ip"]
    print("🧠 Proxy IP Detected:", proxy_ip)
    return proxy_ip
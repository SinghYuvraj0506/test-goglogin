from dotenv import load_dotenv
load_dotenv(override=True, dotenv_path=".env")
import sys
from gologinHandlers import GologinHandler
from config import Config
from selenium.webdriver.common.by import By
from utils.scrapping.HumanMouseBehavior import HumanMouseBehavior
from utils.scrapping.HumanTypingBehavior import HumanTypingBehavior
from utils.scrapping.ScreenObserver import ScreenObserver, callbackEventHandler
import time

def main():
    try:
        profile_id = Config.PROFILE_ID
        gologin = GologinHandler(profile_id=profile_id, proxy_country=Config.PROXY_COUNTRY, proxy_ip=Config.PROXY_IP)
        gologin.connect_gologin_session()
        driver = gologin.driver

        observer = ScreenObserver(driver, callback_function=callbackEventHandler)
        observer.start_monitoring()

        # Navigate to Instagram
        driver.get("https://www.instagram.com")
        
        # Let it run for a while
        time.sleep(30)
    
    finally:
        if(observer):
            observer.stop_monitoring()


    # gologin.stop_gologin_session()

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f'❌ {e}, details: {e.details}')
        sys.exit(1)
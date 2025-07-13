from dotenv import load_dotenv
load_dotenv(override=True, dotenv_path=".env")
import sys
from gologinHandlers import GologinHandler
from config import Config
from utils.scrapping.ScreenObserver import ScreenObserver, callbackEventHandler
import time
from scripts.login import insta_login
from scripts.exploreReel import explore_reels_randomly
from scripts.goToMessages import search_and_message_users
from selenium.webdriver.common.by import By
from utils.scrapping.HumanMouseBehavior import HumanMouseBehavior
from utils.scrapping.HumanTypingBehavior import HumanTypingBehavior
from utils.basicHelpers import get_ip_proxy

def main():
    try:
        profile_id = Config.PROFILE_ID
        gologin = GologinHandler(profile_id=profile_id, proxy_country=Config.PROXY_COUNTRY, proxy_ip=Config.PROXY_IP)
        gologin.connect_gologin_session()
        driver = gologin.driver

        # test proxy validity
        get_ip_proxy(driver)
        
        human_mouse = HumanMouseBehavior(driver)
        human_typing = HumanTypingBehavior(driver)

        observer = ScreenObserver(driver, callback_function=callbackEventHandler)
        observer.start_monitoring()

        driver.get("https://www.instagram.com")
        time.sleep(5)
        # insta_login(driver)
        
        # gologin.download_cookies()
        explore_reels_randomly(driver)
        # search_and_message_users(driver, usernames_list=["ssinghyuvraj02","jatin_jayant_"],message_text="Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining")
        time.sleep(50)
    
    finally:
        if(observer):
            observer.stop_monitoring()
        if(gologin):
            gologin.stop_gologin_session()



if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f'❌ {e}, details: {e.details}')
        sys.exit(1)
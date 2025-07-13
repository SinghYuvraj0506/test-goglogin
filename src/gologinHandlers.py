from gologin import GoLogin
from typing import Optional, Dict, Any
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from config import Config
from utils.basicHelpers import build_brightdata_proxy

class BaseGologinError(Exception):
    """Base exception for gologin related error"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}



class GologinHandler:
    def __init__(self, proxy_country: str, profile_id: str = None, proxy_ip: str = None):
        token = Config.GL_API_TOKEN
        if not token:
            raise BaseGologinError("Gologin Token not found")

        self.gologin = GoLogin({
            'token': token,
            # "executablePath": "/orbita/orbita-browser/chrome"
            # 'extra_params': ['--headless=new', '--no-sandbox']
        })

        self.profile_id = profile_id
        self.proxy_country = proxy_country
        self.proxy_ip = proxy_ip
        self.driver = None

        if profile_id is None:
            self.create_gologin_profile()

        self.gologin.setProfileId(self.profile_id)
        proxyConfig = build_brightdata_proxy(self.proxy_country, self.proxy_ip)
        self.change_gologin_proxy(proxyConfig)


    def connect_gologin_session(self):
        try:
            print('📡 Starting GoLogin session...')
            debugger_address = self.gologin.start()
            # Setup Chrome driver
            service = Service(ChromeDriverManager(
                driver_version=self.gologin.get_chromium_version()).install())

            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_experimental_option(
                "debuggerAddress", debugger_address)

            print('🌐 Connecting to browser...')
            self.driver = webdriver.Chrome(
                service=service, options=chrome_options)

        except Exception as e:
            raise BaseGologinError("Gologin Connection Error", e)


    def stop_gologin_session(self):
        try:
            self.gologin.stop()
            print('✅ GoLogin session stopped successfully')
        except Exception as e:
            raise BaseGologinError("GologinStop Connection Error", e)


    def create_gologin_profile(self):
        try:
            self.profile_id = self.gologin.createProfileWithCustomParams({
                # "os": "lin",
                # "name": "testing",
                # "autoLang": False,
                # "navigator": {
                #     "userAgent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
                #     "resolution": "1920x1080",
                #     "language": "en-US",
                #     "platform": "Linux x86_64"
                # }
                "os": "mac",
                "name": "testing-local2",
                "autoLang": False,
                "navigator": {
                    "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.7151.56 Safari/537.36",
                    "resolution": "1440x900",
                    "language": "en-US",
                    "platform": "MacIntel"
                },
                "webRTC": {
                    "enable": True,
                    "isEmptyIceList": False,
                    "mode": "alerted"
                },
                "webGL": {
                    "mode": "noise",
                    "getClientRectsNoise": 1,
                    "noise": 1
                },
                "timezone": {
                    "enabled": True,
                    "fillBasedOnIp": True,
                }, 
                "geolocation": {
                    "mode": "allow",
                    "enabled": True,
                    "fillBasedOnIp":True
                }
            })

            print('✅ GoLogin profile created successfully')


        except Exception as e:
            raise BaseGologinError("GologinProfileCreation Error", e)
        

    def change_gologin_proxy(self, proxyConfig):
        try:
            self.gologin.changeProfileProxy(self.profile_id, proxyConfig)
            print('✅ GoLogin proxy Alloted successfully')
        except Exception as e:
            raise BaseGologinError("GologinProxyAllot Error", e)


    def download_cookies(self):
        cookies = self.gologin.downloadCookies()
        print("cookies", cookies)
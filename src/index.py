from config import Config
print(Config.PROFILE_ID, Config.GL_API_TOKEN)
import sys

def init():
    from main import MainExecutor
    executor = MainExecutor(
        profile_id=Config.PROFILE_ID, proxy_country=Config.PROXY_COUNTRY, proxy_ip=Config.PROXY_IP
    )
    
    success = executor.execute()
    
    if success:
        print("✅ Execution completed successfully")
    else:
        print("❌ Execution failed")

if __name__ == '__main__':
    try:
        init()
    except Exception as e:
        print(f'❌ {e}, details: {e.details}')
        sys.exit(1)
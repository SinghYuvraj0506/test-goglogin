from dotenv import load_dotenv
load_dotenv()
from config import Config
import sys
# from pyvirtualdisplay.smartdisplay import SmartDisplay


def init():
    # with SmartDisplay() as disp:
    from main import MainExecutor
    executor = MainExecutor(profile_id=Config.PROFILE_ID)
    
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
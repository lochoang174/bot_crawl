import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def wait_for_page_load(driver, timeout=30):
    """
    Waits for the page to fully load by checking the document.readyState.
    
    :param driver: The Selenium WebDriver instance.
    :param timeout: Maximum time to wait for the page to load (in seconds).
    """
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        time.sleep(1)  
        print("✅ Page has fully loaded.")
    except Exception:
        print("❌ Timeout while waiting for the page to load.")
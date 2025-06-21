import time
import random
class HumanBehaviorSimulator:
    """Mô phỏng hành vi người dùng thật"""
    
    @staticmethod
    def human_type(element, text: str):
        """Mô phỏng hành vi gõ phím của người thật"""
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.05, 0.2))
    
    @staticmethod
    def random_delay(min_seconds: float = 1, max_seconds: float = 3):
        """Tạo delay ngẫu nhiên với human behavior"""
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
    
    @staticmethod
    def human_scroll(driver):
        """Scroll một cách tự nhiên như người thật"""
        scroll_pause_time = random.uniform(0.5, 1.5)
        scroll_distance = random.randint(300, 800)
        driver.execute_script(f"window.scrollBy(0, {scroll_distance});")
        time.sleep(scroll_pause_time)
    
    @staticmethod
    def scroll_to_bottom(driver):
        """Scroll xuống cuối trang nhiều lần để trigger lazy loading"""
        last_height = driver.execute_script("return document.body.scrollHeight")
        for i in range(5):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            HumanBehaviorSimulator.random_delay(2, 3)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
    @staticmethod
    def random_typing_delay():
        time.sleep(random.uniform(0.1, 0.3))

    @staticmethod
    def random_wait_after_action():
        
        time.sleep(random.uniform(1.0, 2.0))
    
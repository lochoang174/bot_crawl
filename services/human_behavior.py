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
    def scroll_main_to_bottom(driver):
        """Scroll xuống cuối thẻ #workspace nhiều lần để trigger lazy loading"""
        try:
            # Locate the element with ID 'workspace'
            main_element = driver.find_element("id", "workspace")
            last_height = driver.execute_script("return arguments[0].scrollHeight", main_element)
            print(f"Initial scrollHeight of #workspace: {last_height}")

            for _ in range(5):
                driver.execute_script("arguments[0].scrollTo(0, arguments[0].scrollHeight);", main_element)
                HumanBehaviorSimulator.random_delay(2, 3)
                new_height = driver.execute_script("return arguments[0].scrollHeight", main_element)
                print(f"New scrollHeight of #workspace: {new_height}")
                if new_height == last_height:
                    print("No more content to load in #workspace.")
                    break
                last_height = new_height
        except Exception as e:
            print(f"❌ Lỗi khi scroll thẻ #workspace: {e}")
       
     
            
    @staticmethod
    def scroll_to_bottom_modal_show_all(driver, modal_element):
        """Scroll xuống cuối modal để hiển thị tất cả kết quả trong LinkedIn giống như cuộn bằng chuột giữa"""
        last_height = driver.execute_script("return arguments[0].scrollHeight", modal_element)
        print(f"Initial scrollHeight: {last_height}")

        for i in range(10):  # Limit the number of scroll attempts
            # Scroll by small increments to simulate middle mouse scrolling
            for _ in range(random.randint(5, 10)):  # Randomize the number of small scrolls per iteration
                scroll_distance = random.randint(100,200)  # Small scroll increments
                driver.execute_script(f"arguments[0].scrollBy(0, {scroll_distance});", modal_element)
                HumanBehaviorSimulator.random_delay(0.1, 0.3)  # Short delay between small scrolls
            
            # Add a slightly longer pause to simulate a human reviewing the content
            HumanBehaviorSimulator.random_delay(0.5, 1.5)
            
            # Check the new scroll height
            new_height = driver.execute_script("return arguments[0].scrollHeight", modal_element)
            print(f"New scrollHeight after scroll {i+1}: {new_height}")
            
            # If no new content is loaded, stop scrolling
            if new_height == last_height:
                print("No more content to load.")
                break
            
            last_height = new_height

        # Add a final pause to simulate a human reviewing the content
        HumanBehaviorSimulator.random_delay(2, 3)
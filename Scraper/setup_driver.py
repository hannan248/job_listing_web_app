from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def setup_chrome_driver():
    """Automatically download and setup ChromeDriver"""
    try:
        service = Service(ChromeDriverManager().install())
        
        # Test the driver
        driver = webdriver.Chrome(service=service)
        driver.get("https://www.google.com")
        print("ChromeDriver setup successful!")
        driver.quit()
        return True
        
    except Exception as e:
        print(f"Error setting up ChromeDriver: {str(e)}")
        print("Please install ChromeDriver manually:")
        print("1. Download from: https://chromedriver.chromium.org/")
        print("2. Add to PATH or place in project directory")
        return False

if __name__ == "__main__":
    setup_chrome_driver()
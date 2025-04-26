import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.robotparser import RobotFileParser
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import NoSuchElementException
from urllib.parse import urlparse
import re
import time
import random
import sys  # Added import for sys



# 生成符合当前Chrome版本的User-Agent
CHROME_VERSION = "135.0.7049.115"
USER_AGENT = f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{CHROME_VERSION} Safari/537.36"

# 完整的请求头模板
HEADERS_TEMPLATE = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": USER_AGENT ## 设置用户代理
}

# ===========================
# Configuration and Utilities
# ===========================

def configure_chrome_options():
    """
    Configures Chrome options for Selenium WebDriver.
    Returns:
        ChromeOptions: Configured Chrome options.
    """
    chrome_options = webdriver.ChromeOptions()
    # 基础反检测设置
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument('--ignore-certificate-errors')

    # 添加实验性参数
    chrome_options.add_experimental_option("useAutomationExtension", False)

    # 语言偏好设置
    chrome_options.add_argument("--lang=zh-CN")
    
    # 禁用自动化特征
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")

    return chrome_options


# ===========================
# Human-like delay function
# ===========================
def human_like_delay(min_delay=1, max_delay=3):
    """
    Introduces a human-like delay to mimic real user behavior.
    Args:
        min_delay (int): Minimum delay in seconds.
        max_delay (int): Maximum delay in seconds.
    """
    time.sleep(random.uniform(min_delay, max_delay))

# ===========================
# Human-like Behavior Simulation
# ===========================
def human_like_scroll(driver):
    """
    Scrolls the page to simulate human-like behavior.
    Args:
        driver (WebDriver): The Selenium WebDriver instance.
    """
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    while True:
        # Scroll down to the bottom of the page
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
        # Wait for new content to load
        human_like_delay(min_delay=1, max_delay=3)
        
        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


# ===========================
# Injecting Headers and Fingerprint
# ===========================
def inject_headers(driver):
    """通过CDP协议注入完整请求头"""
    driver.execute_cdp_cmd("Network.enable", {})
    
    # 设置基础头
    for header, value in HEADERS_TEMPLATE.items():
        driver.execute_cdp_cmd("Network.setExtraHTTPHeaders", {
            "headers": HEADERS_TEMPLATE
        })
    
    # 动态生成随机指纹
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
        // 移除 navigator.webdriver 属性
        Object.defineProperty(navigator, 'webdriver', { get: () => undefined });

        // const original = navigator.webdriver;
        // delete navigator.webdriver;
        // Object.defineProperty(navigator, 'webdriver', {
        //     get: () => undefined
        // });
        
        // 模拟 window.chrome 对象
        window.chrome = {
            runtime: {}
            // 添加其他必要属性
        };
        
        // 简化 User-Agent 修改，避免递归
        const originalUserAgent = navigator.userAgent;
        Object.defineProperty(navigator, 'userAgent', {
            get: () => originalUserAgent.replace(/Chrome\\/([\\d.]+)/, (match, version) => {
                return `Chrome/${version}.${Math.floor(Math.random() * 1000)}`;
            })
        });
        """
    })


# ===========================
# Creating Realistic Browser Instance
# ===========================
def get_realistic_driver(options):
    """创建拟真浏览器实例"""  
    try:
        service = Service(executable_path="D:\IdeaWorkSpaces\RogerLYJ\chromedriver.exe", service_creationflags=0)
        driver = webdriver.Chrome(service=service, options=options)
    except WebDriverException as e:
        print(f"WebDriver 初始化失败: {e}")
        print("请检查以下内容：")
        print("1. 是否安装了正确版本的 Chrome 浏览器。")
        print("2. 是否安装了与 Chrome 版本匹配的 chromedriver。")
        print("3. 是否将 chromedriver 添加到系统 PATH 环境变量中。")
        raise

    # 注入请求头和反检测脚本
    inject_headers(driver)
    
    # 设置初始窗口大小（模拟真实用户）
    driver.set_window_size(
        width=random.randint(1200, 1920),
        height=random.randint(800, 1080)
    )
    
    return driver


# ===========================
# Test the URL crawling is allowed
# ===========================
def test_crawling_is_allowed(url):
    """
    Checks if crawling is allowed for the given URL using robots.txt.
    Args:
        url (str): The URL to check.
    """

    # Extract the base URL
    parsed_url = urlparse(url)
    robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"

    # Check robots.txt for scraping permissions
    rp = RobotFileParser()
    rp.set_url(robots_url)
    try:
        rp.read()
        if not rp.can_fetch("*", url):
            print("The website does not allow scraping.")
            return False
        print(f"爬取被允许 (robots.txt URL: {robots_url})")
        return True
    except Exception as e:
        print(f"无法访问 robots.txt 文件: {e} (URL: {robots_url})")
        print("默认允许爬取，继续执行...")
        return True


# ===========================
# Fetching and Parsing Data
# ===========================
def parse_lottery_data(div_element):
    """
    Parses lottery data from the given Selenium WebElement.
    Args:
        div_element (WebElement): The main container element containing lottery data.
    Returns:
        dict: Parsed lottery data.
    """
    result = {}

    try:
        # Parse period number
        period_element = div_element.find_element(By.CSS_SELECTOR, "div.N-dq")
        result["期数"] = period_element.text.split("：")[-1].strip()
    except NoSuchElementException:
        print("期数元素未找到 (CSS Selector: div.N-dq)")
        result["期数"] = None

    try:
        # Parse draw date
        time_element = div_element.find_element(By.CSS_SELECTOR, "div.sj > span")
        try:
            result["开奖时间"] = datetime.strptime(
                time_element.text.replace("开奖时间：", "").replace("年", "-").replace("月", "-").replace("日", ""),
                "%Y-%m-%d"
            ).isoformat()
        except ValueError as ve:
            print(f"日期解析失败: {time_element.text} (CSS Selector: div.sj > span)")
            result["开奖时间"] = None
    except NoSuchElementException:
        print("开奖时间元素未找到 (CSS Selector: div.sj > span)")
        result["开奖时间"] = None

    try:
        # Parse red ball numbers
        red_balls = div_element.find_elements(By.CSS_SELECTOR, "dl.kjq div.kjqQq > span.kjqH")
        result["红球号码"] = [ball.text for ball in red_balls]
    except NoSuchElementException:
        print("红球号码元素未找到 (CSS Selector: dl.kjq div.kjqQq > span.kjqH)")
        result["红球号码"] = []
    
    try:
        # Parse blue ball numbers
        blue_balls = div_element.find_elements(By.CSS_SELECTOR, "div.kjqHq > span.kjqL")
        result["蓝球号码"] = [ball.text for ball in blue_balls]
    except NoSuchElementException:
        print("蓝球号码元素未找到 (CSS Selector: div.kjqHq > span.kjqL)")
        result["蓝球号码"] = []
    
    try:
        # Parse ball order
        ball_order = div_element.find_elements(By.CSS_SELECTOR, "dl.cqsx div.kjqQq > span.kjqH")
        result["出球顺序"] = [ball.text for ball in ball_order]
    except NoSuchElementException:
        print("出球顺序元素未找到 (CSS Selector: dl.cqsx div.kjqQq > span.kjqH)")
        result["出球顺序"] = []
    
    try:
        # Parse award details
        awards = []
        rows = div_element.find_elements(By.CSS_SELECTOR, ".qkbg tr")[1:]  # Skip header row
        for row in rows:
            cols = row.find_elements(By.TAG_NAME, "td")
            if len(cols) >= 4:
                award = {
                    "奖项": cols[0].text.strip(),
                    "中奖注数": cols[1].text.strip().replace(",", ""),
                    "单注奖金": cols[2].text.strip().replace(",", ""),
                    "中奖条件": cols[3].text.strip()
                }
                awards.append(award)
            elif len(cols) == 1 and awards:  # Handle rowspan cases
                # Append additional conditions to the last award
                awards[-1]["中奖条件"] += f", {cols[0].text.strip()}"
        result["奖项详情"] = awards
    except NoSuchElementException:
        print("奖项详情元素未找到 (CSS Selector: .qkbg tr)")
        result["奖项详情"] = []

    return result


# ===========================
# Saving Data
# ===========================

def save_structured_data(data, filename=None):
    """
    Saves structured data to a JSON file.
    Args:
        data (dict): The data to save.
        filename (str): Optional filename. If not provided, a timestamped filename will be generated.
    Returns:
        str: The filename where the data was saved.
    """
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"lottery_result_{timestamp}.json"

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"数据已保存至 {filename}")
    return filename


# ===========================
# Main Functionality
# ===========================

def main(url_str):
    """
    Main function to fetch, parse, and save lottery data.
    """
    if not url_str.strip():
        url_str = sys.argv[1] if len(sys.argv) > 1 else input("请输入目标URL: ")

    # Validate URL
    if not re.match(r'^https?://', url_str):
        print("输入的 URL 无效，请输入以 http:// 或 https:// 开头的完整 URL。")
        return
    
    # Configure Chrome options
    options = configure_chrome_options()  

    # Test the crawling permission
    if not test_crawling_is_allowed(url_str):
        print("爬取被禁止，程序终止。")
        return

    # Configure Selenium WebDriver
    driver = get_realistic_driver(options)
    if not driver:
        print("无法初始化浏览器实例，程序终止。")
        return


    try:
        # Navigate to the target URL
        driver.get(url_str)
        driver.implicitly_wait(10)

        # Wait for the main container to load
        div_element_kjxxN = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@class='kjxxN']"))
        )

        # Parse lottery data
        lottery_data = parse_lottery_data(div_element_kjxxN)
        print("结构化数据:", lottery_data)

        # Save structured data to a JSON file
        save_structured_data(lottery_data)
    except WebDriverException as e:
        print(f"执行过程中发生错误: {e}")

    finally:
        driver.quit()
        print("浏览器已安全关闭")


if __name__ == "__main__":
    
    url_str = "https://www.zhcw.com/kjxx/ssq/kjxq/?kjData=2024090"
    main(url_str)
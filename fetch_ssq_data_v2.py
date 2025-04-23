import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import Select
import requests
import time
import random

CHROME_OPTIONS = webdriver.ChromeOptions()
CHROME_OPTIONS.add_argument("--disable-blink-features=AutomationControlled")
CHROME_OPTIONS.add_experimental_option("excludeSwitches", ["enable-automation"])
CHROME_OPTIONS.add_argument('--ignore-certificate-errors')

def human_like_delay(min=1, max=3):
    time.sleep(random.uniform(min, max))

def fetch_with_requests(url):
    # Step 1: Set up headers to simulate a browser request
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }

    # Step 2: Check the robots.txt file to see if scraping is allowed
    robots_url = url + "robots.txt"
    robots_response = requests.get(robots_url, headers=headers)

    if robots_response.status_code == 200:
        print("robots.txt content:")
        print(robots_response.text[:10])  # Print the first 500 characters of robots.txt
        if "Disallow: /" in robots_response.text:
            print("The website does not allow scraping.")
            return
        else:
            print("The website allows scraping.")
    else:
        print("Could not fetch robots.txt. Proceeding with caution...")

    # Step 3: Send a GET request to the server
    response = requests.get(url, headers=headers)

    # Step 4: Print the server's response status code
    print(f"Server Response Status Code: {response.status_code}")

    # Step 5: Check if the request was successful
    if response.status_code == 200:
        # Step 6: Save the full content to a file for inspection
        with open("webpage_content.html", "w", encoding="utf-8") as file:
            file.write(response.text)
        print("The full content has been saved to 'webpage_content.html'.")
    else:
        print("Failed to fetch the webpage. Please check the URL or your connection.")


def parse_lottery_data(div_element):
    result = {}
    
    # 解析期数
    period_element = div_element.find_element(By.CSS_SELECTOR, "div.N-dq")
    result["期数"] = period_element.text.split("：")[-1].strip()

    # 解析开奖时间
    time_element = div_element.find_element(By.CSS_SELECTOR, "div.sj > span")
    
    result["开奖时间"] = datetime.strptime(time_element.text.replace("开奖时间：","").replace("年", "-").replace("月", "-").replace("日", ""), "%Y-%m-%d").isoformat()

    # 解析红球号码
    red_balls = div_element.find_elements(By.CSS_SELECTOR, "dl.kjq div.kjqQq > span.kjqH")
    result["红球号码"] = [ball.text for ball in red_balls]

    # 解析蓝球号码
    blue_balls = div_element.find_elements(By.CSS_SELECTOR, "div.kjqHq > span.kjqL")
    result["蓝球号码"] = [ball.text for ball in blue_balls]

    # 解析出球顺序
    ball_order = div_element.find_elements(By.CSS_SELECTOR, "dl.cqsx div.kjqQq > span.kjqH")
    result["出球顺序"] = [ball.text for ball in ball_order]

    # 解析奖项信息
    awards = []
    rows = div_element.find_elements(By.CSS_SELECTOR, ".qkbg tr")[1:]  # 跳过表头
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
    result["奖项详情"] = awards

    return result

def save_structured_data(data, filename=None):
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"lottery_result_{timestamp}.json"
    
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"数据已保存至 {filename}")
    return filename

def main():
    url_str = "https://www.zhcw.com/kjxx/ssq/kjxq/?kjData=2024090"

    # Comment out fetch_with_requests if not needed
    fetch_with_requests(url_str)
            
    # 添加自定义HTTP请求头
    caps = DesiredCapabilities.CHROME.copy()
    caps['goog:loggingPrefs'] = {'performance': 'ALL'}

    CHROME_OPTIONS.set_capability('goog:loggingPrefs', caps['goog:loggingPrefs'])
    CHROME_OPTIONS.add_argument('--disable-blink-features=AutomationControlled')
    CHROME_OPTIONS.add_argument('--disable-extensions')
    CHROME_OPTIONS.add_argument('--disable-popup-blocking')
    CHROME_OPTIONS.add_argument('--disable-web-security')

    print("caps.values：", caps.values)
    print("CHROME_OPTIONS.arguments", CHROME_OPTIONS.arguments)

    
    driver = webdriver.Chrome(options=CHROME_OPTIONS)
    try:
        # 隐式等待对动态加载内容不够可靠
        driver.implicitly_wait(10)
        driver.get(url_str)
        
        # 修改前后截图对比
        driver.save_screenshot('before.png')
    
        # 处理动态加载​：使用显式等待确保元素加载完成。
        div_element_kjxxN = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@class='kjxxN']"))
        )

        # 
        div_element_xqxl = div_element_kjxxN.find_element(By.XPATH, ".//div[@class='xqxl']")
        # 展开下拉菜单
        driver.execute_script('arguments[0].setAttribute("data-zt", "t")', div_element_xqxl)

        options = div_element_xqxl.find_elements(By.TAG_NAME, "li")
        for option in options:
            if option.text == "2025038":
                option.click()


        div_element_N_dq = div_element_xqxl.find_element(By.XPATH, "//div[@class='N-dq']")
        print("期数：", div_element_N_dq.text)

        div_element_kjxxN_new = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@class='kjxxN']"))
        )

        # 定位到开奖时间的元素
        div_element_sj = div_element_kjxxN_new.find_element(By.CSS_SELECTOR, "div.sj > span")
        # 获取开奖时间的文本内容，并打印
        print(div_element_sj.text)

        # 获取红球号码
        red_balls = div_element_kjxxN_new.find_elements(By.CSS_SELECTOR, "dl.kjq div.kjqQq > span.kjqH")
        red_ball_values = [ball.text for ball in red_balls]
        print("红球号码:", red_ball_values)

        # 获取蓝球号码
        blue_balls = div_element_kjxxN_new.find_elements(By.CSS_SELECTOR, "div.kjqHq > span.kjqL")
        blue_ball_values = [ball.text for ball in blue_balls]
        print("蓝球号码:", blue_ball_values)

        # 获取出球顺序
        ball_order = div_element_kjxxN_new.find_elements(By.CSS_SELECTOR, "dl.cqsx div.kjqQq > span.kjqH")
        ball_order_values = [ball.text for ball in ball_order]
        print("出球顺序:", ball_order_values)

        lottery_data = parse_lottery_data(div_element_kjxxN_new)
        print("结构化数据:", lottery_data)
        # 存储结构化数据
        save_structured_data(lottery_data)

        # 执行修改操作...
        driver.save_screenshot('after.png')
        

    finally:
        driver.quit()
        print("浏览器已安全关闭")

if __name__ == "__main__":
    main()
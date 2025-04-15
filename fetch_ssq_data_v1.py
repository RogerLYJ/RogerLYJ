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
    # ===== 1. 提取奖池和销售金额 =====
    kjqtxx_div = div_element.find_element(By.XPATH, "./preceding-sibling::div[@class='kjqtxx']")
    pool_amount = kjqtxx_div.find_element(By.CSS_SELECTOR, ".jc strong").text.strip()
    sales_amount = kjqtxx_div.find_element(By.CSS_SELECTOR, ".xs").text.split("：")[1].replace("元", "").strip()

    # ===== 2. 解析中奖情况表格（动态处理rowspan）=====
    table = div_element.find_element(By.CSS_SELECTOR, ".qkbg table")
    rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")
    
    prize_data = []
    rowspan_cache = {}  # 缓存跨行数据 {列索引: (值, 剩余行数)}

    for row in rows:
        cells = row.find_elements(By.TAG_NAME, "td")
        current_data = {}

        # 处理单元格并更新缓存
        for col_idx, cell in enumerate(cells):
            # 读取缓存数据或新数据
            if col_idx in rowspan_cache:
                current_data[col_idx] = rowspan_cache[col_idx]["value"]
                rowspan_cache[col_idx]["remaining"] -= 1
                if rowspan_cache[col_idx]["remaining"] == 0:
                    del rowspan_cache[col_idx]
            else:
                cell_text = cell.text.strip()
                rowspan = int(cell.get_attribute("rowspan") or 1)
                if rowspan > 1:
                    rowspan_cache[col_idx] = {
                        "value": cell_text,
                        "remaining": rowspan - 1
                    }
                current_data[col_idx] = cell_text

        # 结构化存储（动态适配列位置）
        if len(cells) >= 4:
            prize_data.append({
                "奖项": current_data.get(0, ""),
                "中奖注数": current_data.get(1, ""),
                "单注奖金": current_data.get(2, "").replace("元", ""),
                "中奖条件": current_data.get(3, "")
            })

    # ===== 3. 提取一等奖分布和兑奖期限 =====
    first_prize_text = div_element.find_element(
        By.XPATH, ".//dl[dt[contains(., '一等奖中奖情况')]]/dd"
    ).text.strip()
    
    deadline_text = div_element.find_element(
        By.XPATH, ".//dl[dt[contains(., '兑奖期限')]]/dd"
    ).text.split("，")[0].strip()

    print("奖池金额：", pool_amount,
        "销售金额：", sales_amount,
        "中奖明细：", prize_data,
        "一等奖分布：", first_prize_text,
        "兑奖截止日：", deadline_text)


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

        # 定位到父级可点击元素
        # div_element_kjxxN = driver.find_element(By.XPATH, "/html/body//div[2]//div[4]//div[2]//div[1]//div[1]//div[contains(@class, 'kjxxN')]"))
        # div_element_kjxxN = driver.find_element(By.XPATH, "//div[contains(@class, 'kjxxN') and @data-v]")
        # div_element_kjxxN = driver.find_element(By.XPATH, "//div[@class='kjxxN']")
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

        parse_lottery_data(div_element_kjxxN_new)

        # div_element_N_dq = div_element_xqxl.find_element(By.CSS_SELECTOR, "div.N-dq[data-v]")    

        # # 获取关键信息
        # # print(div_element_N_dq)
        # print(div_element_N_dq.get_attribute("class"), " ：", div_element_N_dq.text)

        # # 方法1：使用setAttribute
        # driver.execute_script("""
        #     arguments[0].setAttribute('data-v', '2025038');
        # """, div_element_N_dq)

        # # # 方法2：通过dataset（仅限data-*属性）
        # # driver.execute_script(
        # #     "arguments[0].dataset.v = '2025038';",
        # #     div_element_N_dq
        # # )
        # print(div_element_N_dq.get_attribute("class"), " ：", div_element_N_dq.text)

        # 同步更新显示值
        # strong_element_N_t = div_element_xqxl.find_element(By.CLASS_NAME, "N-t")
        # print(strong_element_N_t.get_attribute("class"), " ：", strong_element_N_t.text)
        # driver.execute_script(
        #     "arguments[0].textContent = '2025038';",
        #     strong_element_N_t
        # )
        # print(strong_element_N_t.get_attribute("class"), " ：", strong_element_N_t.text)

        # div_element_N_lb = div_element_xqxl.find_element(By.CLASS_NAME, "N-lb")
        # print(div_element_N_lb.get_attribute("class"), " ：", div_element_N_lb.text)
        # driver.execute_script(
        #     "arguments[0].textContent = '1';",
        #     div_element_N_lb
        # )

        # # 获取关键信息
        # print(div_element_N_lb.get_attribute("class"), " ：", div_element_N_lb.text)

        # 执行修改操作...
        driver.save_screenshot('after.png')
        

    finally:
        driver.quit()
        print("浏览器已安全关闭")

if __name__ == "__main__":
    main()
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import os
import time

# Set up Chrome options (headless mode)
# chrome_options = webdriver.ChromeOptions()
# chrome_options.add_argument("--headless")
# chrome_options.add_argument("--disable-gpu")
# chrome_options.add_argument("--window-size=1920x1080")
# chrome_options.add_argument("--no-sandbox")
# chrome_options.add_argument("--disable-dev-shm-usage")
# driver = webdriver.Chrome(options=chrome_options)

driver = webdriver.Chrome()
url = "https://huggingface.co/spaces/Kwai-Kolors/Kolors-Virtual-Try-On"
driver.get(url)

try:
    WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    print("Page loaded successfully.")

    iframe = WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.TAG_NAME, "iframe"))
    )
    driver.switch_to.frame(iframe)
    print("Switched to iFrame.")

    file_inputs = WebDriverWait(driver, 60).until(
        EC.presence_of_all_elements_located((By.TAG_NAME, "input"))
    )
    if len(file_inputs) < 2:
        raise Exception("Less than 2 upload buttons found!")

    person_image_path = r"D:\Pictures\person.png"
    cloth_image_path = r"D:\Pictures\cloth_1.png"

    file_inputs[0].send_keys(person_image_path)
    print("Uploaded person image.")
    time.sleep(10) 

    file_inputs[1].send_keys(cloth_image_path)
    print("Uploaded cloth image.")
    time.sleep(10)  

    run_button = WebDriverWait(driver, 120).until(
        EC.element_to_be_clickable((By.ID, "button"))
    )
    driver.execute_script("arguments[0].click();", run_button)
    print("Clicked the Run button.")


    a_element = WebDriverWait(driver, 180).until(
         EC.presence_of_element_located((By.XPATH, '//a[@download="image.webp"]'))
    )
    image_url = a_element.get_attribute("href")
    print("Extracted Image URL:", image_url)

    # Download the final image
    # image_data = requests.get(image_url).content
    # output_path = os.path.join(os.getcwd(), "result.webp")
    # with open(output_path, "wb") as file:
    #     file.write(image_data)
    # print(f"Downloaded final result image: {output_path}")

except Exception as e:
    print("Error occurred:", e)
finally:
    driver.quit()



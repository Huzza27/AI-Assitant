from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from email_processing import get_email_body, wait_for_new_email
from selenium.webdriver.common.keys import Keys
import time

def open_firefox(url):
    # If geckodriver is not in your PATH, specify the path to geckodriver.exe
    driver = webdriver.Firefox()
    driver.get(url)


def login_to_canvas_with_2fa(username, password, email_user, email_pass, imap_server):
    
    # Use ChromeDriver with Opera options
    driver = webdriver.Firefox() # Make sure ChromeDriver is in your PATH
    driver.get("https://myaccess.sierracollege.edu/my.policy")

 # Add logic to check for the session restart link and click it
    try:
        wait = WebDriverWait(driver, 10)
        session_restart_link = wait.until(EC.presence_of_element_located((By.XPATH, "//a[text()='click here']")))
        session_restart_link.click()
    except TimeoutException:
        print("Session restart link not found, proceeding with login")

    # Fill in the username and password
    driver.find_element(By.ID, "input_1").send_keys(username)  # Update with actual ID"
    driver.find_element(By.ID, "input_2").send_keys(password)  # Update with actual ID
    driver.find_element(By.CLASS_NAME, "submit").click()  # Update with actual ID

    #Click email 2fa button
    wait = WebDriverWait(driver, 5)
    sendEmailButton = driver.execute_script("return document.getElementsByTagName('a')[2];")
    driver.execute_script("arguments[0].click();", sendEmailButton)

    # Adding a delay after clicking, simulating reading time or reaction time

    # Wait for the 2FA input field to be present
    wait = WebDriverWait(driver, 10)
    two_factor_field = wait.until(EC.presence_of_element_located((By.ID, "input_2")))  # Update with actual ID
    submit_button =driver.find_element(By.CLASS_NAME, "submit") 
    two_factor_code = wait_for_new_email(email_user, email_pass, imap_server, sender_email)

    if two_factor_code:
        two_factor_field.send_keys(two_factor_code)
        submit_button.click()
    else:
        print("Failed to retrieve the 2FA code.")

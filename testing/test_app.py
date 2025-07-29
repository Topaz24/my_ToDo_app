import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from time import sleep

@pytest.fixture
def driver():
    # Set Chrome to headless mode
    options = Options()
    
    #adding the standard options to make it headless and compatible in other enviorments
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)

    # Open the app (make sure it's running locally)
    driver.get("http://localhost:80")
    yield driver
    driver.quit()

def test_title(driver):
    #title check
    assert "To do" in driver.title

def test_input(driver):
    #adding a task with the value "add1" to the to do list
    input_field = driver.find_element(By.NAME, "task")
    add_button = driver.find_element(By.ID, "send")
    input_field.send_keys("add1")
    
    #submitting the task
    add_button.click()
    sleep(2)

    #making sure the task was created
    task_item = driver.find_element(By.XPATH, "//li[contains(text(), 'add1')]")
    assert "add1" in task_item.text

def test_toggle(driver):
    #find the toggle button then find what the color is at first
    toggle_button = driver.find_element(By.XPATH, "//li[contains(text(), 'add1')]//button[@class='box']")
    initial_color = toggle_button.value_of_css_property('background-color')
    
    #using the toggle button to the other one then checking if the color indeed changed
    toggle_button.click()
    sleep(2)
    toggle_button = driver.find_element(By.XPATH, "//li[contains(text(), 'add1')]//button[@class='box']")
    new_color = toggle_button.value_of_css_property('background-color')
    assert initial_color != new_color, f"Color did not change: {initial_color} != {new_color}"

def test_delete(driver):
    #not good delete aksdkjdkasd
    #check for the delete button and delete the task we added before
    delete_button = driver.find_element(By.XPATH, "//li[contains(text(), 'add1')]//button[@id='del']")
    delete_button.click()
    sleep(5)
    
    #checking to see if the task was deleted, elements will retuen an empty list if not found
    task_items = driver.find_elements(By.XPATH, "//li[contains(text(), 'add1')]")
    assert len(task_items) == 0 , "the task wasnt deleted"

from selenium.webdriver.common.by import By

header_profile_link = (By.XPATH, "//a[@id='header_profile_link']")

solutions_tab = (By.XPATH, "//a[text()='Solutions']")
h5_loading_more = (By.XPATH, "//div//h5[text()= 'Loading more items...')]")

solution_list_item = (By.XPATH, "//div[@class='list-item-solutions']")
solution_kata_link = (By.XPATH, "/div[@class='item-title']//a")
solution_kyu = (By.XPATH, "/div[@class='item-title']/div[contains(@class, 'hex')]/div/span")
solution_language = (By.XPATH, "/h6")
solution_code = (By.XPATH, "//pre//code")

kata_description = (By.ID, "description")

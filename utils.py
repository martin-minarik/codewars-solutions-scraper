import locators
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def js_click(driver, elem):
    driver.execute_script("arguments[0].click();", elem)


def enter_codewars(driver, _session_id):
    driver.get("https://www.codewars.com/")
    driver.add_cookie({"name": "_session_id", "value": _session_id})
    driver.get("https://www.codewars.com/")


def enter_solutions_page(driver):
    wait = WebDriverWait(driver, timeout=60, poll_frequency=1)

    profile_link_elem = driver.find_element(*locators.header_profile_link)
    profile_url = profile_link_elem.get_attribute('href')
    driver.get(profile_url)

    wait.until(EC.presence_of_element_located(locators.solutions_tab))
    solutions_tab_elem = driver.find_element(*locators.solutions_tab)
    js_click(driver, solutions_tab_elem)


def scrape_solutions(driver):
    first_tab_handle = driver.current_window_handle
    driver.execute_script("window.open('about:blank','image_tab');")
    driver.switch_to.window(driver.window_handles[-1])
    second_tab_handle = driver.current_window_handle
    driver.switch_to.window(first_tab_handle)

    # Move to end of page until all solutions are loaded
    while driver.find_elements(*locators.h5_loading_more):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        driver.implicitly_wait(0.5)

    solutions = []

    for solution_elem in driver.find_elements(*locators.solution_list_item):
        kata_link_elem = solution_elem.find_element(*locators.solution_kata_link)
        kata_url = kata_link_elem.get_attribute('href')
        kata_title = kata_link_elem.text
        kyu = solution_elem.find_element(*locators.solution_kyu).text
        language = solution_elem.find_element(*locators.solution_language).text
        code = solution_elem.find_element(*locators.solution_code).text

        driver.switch_to.window(second_tab_handle)
        driver.get(kata_url)
        description = driver.find_element(*locators.kata_description).text
        driver.switch_to.window(first_tab_handle)

        solutions.append({"kata_url": kata_url,
                          "kata_title": kata_title,
                          "kata_description": description,
                          "kyu": kyu,
                          "language": language,
                          "code": code})

    # TODO: consider caching passing config with already scraped solutions

    return solutions

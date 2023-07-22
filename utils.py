import locators
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import os
from language_extensions import language_map


def trim_long_str(name, replacement='', max_length=35):
    return f'{name[:max_length - 3]}{replacement}' if len(name) > max_length else name


def js_click(driver, elem):
    driver.execute_script("arguments[0].click();", elem)


def enter_codewars(context):
    context.driver.get("https://www.codewars.com/")
    context.driver.add_cookie({"name": "_session_id", "value": context.config["_session_id"]})
    context.driver.get("https://www.codewars.com/")


def enter_solutions_page(context):
    driver = context.driver

    profile_link_elem = driver.find_element(*locators.header_profile_link)
    profile_url = profile_link_elem.get_attribute('href')
    driver.get(profile_url)

    context.wait.until(EC.presence_of_element_located(locators.solutions_tab))
    solutions_tab_elem = driver.find_element(*locators.solutions_tab)
    js_click(driver, solutions_tab_elem)


def scrape_solutions(context):
    driver = context.driver
    wait = context.wait

    try:
        wait.until(EC.presence_of_element_located(locators.solution_list_item))
    except TimeoutException:
        TimeoutError("No solutions found.")

    # Move to end of page until all solutions are loaded
    while driver.find_elements(*locators.h5_loading_more):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        driver.implicitly_wait(0.5)

    solutions = []

    for solution_elem in driver.find_elements(*locators.solution_list_item):
        kata_link_elem = solution_elem.find_element(*locators.solution_kata_link)
        kata_url = kata_link_elem.get_attribute('href')
        kata_title = kata_link_elem.text
        kyu = solution_elem.find_element(*locators.solution_kyu).text.lower()
        language = solution_elem.find_element(*locators.solution_language).text.rstrip(':')
        code = solution_elem.find_element(*locators.solution_code).text

        driver.switch_to.window(context.second_tab_handle)
        driver.get(kata_url)
        description = driver.find_element(*locators.kata_description).text
        driver.switch_to.window(context.first_tab_handle)

        solutions.append({"kata_id": kata_url.rsplit("/", 1)[1],
                          "kata_url": kata_url,
                          "kata_title": kata_title,
                          "kata_description": description,
                          "kyu": kyu,
                          "language": language,
                          "code": code})

    return solutions


def save_solutions(solutions):
    for solution in solutions:
        directory_path = rf"codewars\{solution['kyu']}\{solution['kata_id']}"
        os.makedirs(directory_path, exist_ok=True)

        solution_file_path = os.path.join(directory_path,
                                          f"solution{language_map.get(solution['language'])}")

        with open(solution_file_path, 'w', encoding="utf-8") as file:
            file.write(solution["code"])

        with open(os.path.join(directory_path, "README.md"), "w", encoding="utf-8") as file:
            file.write(solution["kata_description"])

from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import os
from time import sleep
from collections import Counter
from itertools import islice
from itertools import count
import posixpath

import locators
from language_extensions import language_map
from markdownify import markdownify


def trim_long_str(name, replacement='', max_length=35):
    return f'{name[:max_length - 3]}{replacement}' if len(name) > max_length else name


def to_markdown_link(url, alias):
    return f"[{alias}]({url})"


def to_markdown_table(data: list[dict], alias_key_pairs: dict):
    aggregate_functions = [v for v in alias_key_pairs.values() if callable(v)]
    aggregated_values = [func(row) for row in data for func in aggregate_functions]
    it_aggregated_values = iter(aggregated_values)
    it_idx_aggregate = count()

    lengths = [
        max(len(alias),
            *((len(row[key]) for row in data)
              if isinstance(key, str) else
              (len(aggregated_value) for aggregated_value in islice(aggregated_values, next(it_idx_aggregate),
                                                                    None,
                                                                    len(aggregate_functions))))
            )

        for alias, key in alias_key_pairs.items()
    ]

    table_rows = ['|'.join(f"{alias: ^{length + 2}}" for alias, length in zip(alias_key_pairs.keys(), lengths, )),
                  '|'.join(f":{'-' * length}:" for length in lengths)]

    table_rows.extend(
        '|'.join(
            f"{row[key] if isinstance(key, str) else next(it_aggregated_values): ^{length + 2}}"
            for key, length in zip(alias_key_pairs.values(), lengths)
        )
        for row in data
    )

    return '\n'.join(f"|{table_row}|" for table_row in table_rows)


def js_click(driver, elem):
    driver.execute_script("arguments[0].click();", elem)


def enter_codewars(driver_context, _session_id):
    driver_context.driver.get("https://www.codewars.com/")
    driver_context.driver.add_cookie({"name": "_session_id", "value": _session_id})
    driver_context.driver.get("https://www.codewars.com/")


def enter_solutions_page(driver_context):
    driver = driver_context.driver

    profile_link_elem = driver.find_element(*locators.header_profile_link)
    profile_url = profile_link_elem.get_attribute('href')
    driver.get(profile_url)

    driver_context.wait.until(EC.presence_of_element_located(locators.solutions_tab))
    solutions_tab_elem = driver.find_element(*locators.solutions_tab)
    js_click(driver, solutions_tab_elem)


def scrape_solutions(driver_context):
    driver = driver_context.driver
    wait = driver_context.wait

    try:
        wait.until(EC.presence_of_element_located(locators.solution_list_item))
    except TimeoutException:
        TimeoutError("No solutions found.")

    # Move to end of page until all solutions are loaded
    while driver.find_elements(*locators.h5_loading_more):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(0.1)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight - 20);")
        sleep(0.1)

    solutions = []

    for solution_elem in driver.find_elements(*locators.solution_list_item):
        kata_link_elem = solution_elem.find_element(*locators.solution_kata_link)
        kata_url = kata_link_elem.get_attribute('href')
        kata_title = kata_link_elem.text
        kyu = solution_elem.find_element(*locators.solution_kyu).text.lower()
        language = solution_elem.find_element(*locators.solution_language).text.rstrip(':')
        code = solution_elem.find_element(*locators.solution_code).text

        driver.switch_to.window(driver_context.second_tab_handle)
        driver.get(kata_url)
        description = driver.find_element(*locators.kata_description).get_attribute("innerHTML")
        driver.switch_to.window(driver_context.first_tab_handle)

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
        directory_path = rf"codewars\{solution['kyu']}\{solution['kata_id']}_{solution['language'].lower()}"
        os.makedirs(directory_path, exist_ok=True)

        solution_file_path = os.path.join(directory_path,
                                          f"solution{language_map.get(solution['language'].lower(), '.txt')}")

        with open(solution_file_path, 'w', encoding="utf-8") as file:
            file.write(solution["code"])

        with open(os.path.join(directory_path, "README.md"), "w", encoding="utf-8") as file:
            md_text = markdownify(solution["kata_description"], heading_style="ATX")

            file.write(f"# {solution['kata_title']}\n\n")
            file.write(f"**<{solution['kata_url']}>**\n\n")
            file.write(f"Difficulty: **{solution['kyu']}**\n\n")
            file.write(f"Language: **{solution['language']}**\n\n")
            file.write("# Description:\n\n")
            file.write(md_text)


def write_summary_readme(solutions):
    sorted_solutions = sorted(solutions, key=lambda s: s["kyu"])

    md_table = to_markdown_table(sorted_solutions,
                                 keys_order_alias={"kyu": "Difficulty",
                                                   "language": "Language",
                                                   "kata_title": "Kata",
                                                   "kata_id": "Kata ID"},
                                 )

    with open(r"codewars\README.md", "w", encoding="utf-8") as file:
        file.write("# Summary\n\n")

        file.write(f"**Total:** {len(solutions)}\n\n")

        file.writelines([f"**{k}:** {v}\n\n"
                         for k, v in Counter(s["language"] for s in solutions).most_common()])

        file.write(md_table)

from bs4 import BeautifulSoup
import requests
from tkinter import messagebox


def make_unordered_list(ol_element):
    item_symbol = "*"
    the_list = ol_element.find_all("li", recursive=False)

    for li in the_list:
        if li.contents:
            if isinstance(li.contents[0], str):
                li.contents[0].replace_with(f"{item_symbol} {li.contents[0]}")
            else:
                li.insert(0, f"{item_symbol} ")
        nested_ol = li.find("ol")
        if nested_ol:
            make_unordered_list(nested_ol)


def enumerate_list(ol_element):
    the_list = ol_element.find_all("li", recursive=False)
    for index, li in enumerate(the_list, start=1):
        enumeration = f"{index})"
        if li.contents:
            if isinstance(li.contents[0], str):
                li.contents[0].replace_with(f"{enumeration} {li.contents[0]}")

            else:
                li.insert(0, f"{enumeration} ")

        nested_ol = li.find("ol")
        if nested_ol:
            make_unordered_list(nested_ol)


def merge_strings(input_list):
    result = []
    buffer = ""
    for s in input_list:
        stripped_str = s.strip()
        if stripped_str:
            if stripped_str[0].isdigit():
                if buffer:
                    result.append(buffer)
                buffer = s
            elif stripped_str.startswith("*"):
                buffer += " " + s
    if buffer:
        result.append(buffer)

    return result


def process_def_list(definition_list):
    # remove citations through bold numbers
    the_list = definition_list.find_all("li")
    for li in the_list:
        first_c = li.find(True)
        if first_c and first_c.name == "b" and first_c.get_text().strip().isdigit():
            li.decompose()
    # remove citations through classes
    for unwanted in definition_list.find_all(
        class_=[
            "citation-whole",
            "h-usage-example",
            "Latn mention e-example",
            "cited-source",
            "q-hellip-sp",
            "q-hellip-b",
            "see-cites",
            "external text",
            "mw-empty-elt",
        ]
    ):
        unwanted.extract()
    # definition list - raw html
    enumerate_list(definition_list)
    # definition list - ordered list in raw html
    remaining_text = definition_list.get_text()
    lines = remaining_text.splitlines()
    merged_strings = merge_strings(lines)
    final_res = [i.replace("*", "\n*") for i in merged_strings]
    return final_res


def from_word_to_list(word, notify=1):
    word.strip()
    url = f"https://en.wiktionary.org/wiki/{word}"

    response = requests.get(url)
    parts_of_speech = [
        "Noun",
        "Verb",
        "Adverb",
        "Adjective",
        "Interjection",
        "Conjunction",
        "Pronoun",
        "Preposition",
        "Numeral",
        "Proper_noun",
    ]
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        english_section = soup.find("h2", string="English")
        if not english_section:
            if notify == 1:
                messagebox.showinfo(
                    "Ошибка!", f"Данное слово не используется в английском"
                )
            return 1
        list_of_res = []
        for i in parts_of_speech:
            # Below we retrieve the following HTML tag, e.g. <h3 id="Noun">Noun</h3>
            part_section = soup.find(id=i)
            # part section - list of parts of speech for the word
            if part_section:
                # Below we retrieve an ordered list under id Noun
                # definition_list - nearly raw html
                definition_list = part_section.findNext("ol")
                if definition_list:
                    # processed_list - formatted list (no HTML elements)
                    processed_list = process_def_list(definition_list)
                    processed_list.insert(0, i)
                    list_of_res.append(processed_list)
        return list_of_res
    else:
        if notify == 1:
            messagebox.showinfo("Уведомление", f"Данное слово не найдено в словаре")
        return 1

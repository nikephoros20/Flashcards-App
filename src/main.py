from parser import from_word_to_list
import sqlite3
import random
import tkinter as tk
from tkinter import messagebox
from tkinter import font
from tkinter import simpledialog
from tkinter import scrolledtext

#####################################################################################################################################################
# AUXILIARY FUNCTIONS
#####################################################################################################################################################
def destroy_current_frame():
    global current_frame
    if current_frame:
        current_frame.destroy()
        current_frame = None

def is_dict_empty():
    cursor.execute("SELECT COUNT(*) FROM dictionary;")
    row_count = cursor.fetchone()[0]
    if row_count == 0:
        return True
    else:
        return False

#####################################################################################################################################################
# ADDING AND DELETING
#####################################################################################################################################################
def add_several_words(list):
    res = [i.strip() for i in list.split(",")]
    already_added = []
    not_found = []
    added = []
    for word in res:
        cursor.execute("SELECT * FROM dictionary WHERE word=?", (word,))
        dict_tuple = cursor.fetchone()
        if dict_tuple == None:
            def_list = from_word_to_list(word, notify=0)
            if def_list != 1:
                definition = " ".join(word for sublist in def_list for word in sublist)
                cursor.execute(
                    "INSERT INTO dictionary (word, definition, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP)",
                    (word, definition),
                )
                connection.commit()
                added.append(word)
            else:
                not_found.append(word)
                continue
        else:
            already_added.append(word)
            continue
    main_menu()
    parts = []
    if added:
        parts.append(f"Добавлены: {', '.join(map(str, added))}")
    if already_added:
        parts.append(f"Уже в словаре: {', '.join(map(str, already_added))}")
    if not_found:
        parts.append(f"Не найдены: {', '.join(map(str, not_found))}")
    messagebox.showinfo("Результаты", "\n".join(parts))


def what_to_add(request):
    if "," in request:
        add_several_words(request)
    else:
        add_word(request)


def add_word(word):
    cursor.execute("SELECT * FROM dictionary WHERE word=?", (word,))
    dict_tuple = cursor.fetchone()

    if dict_tuple:
        messagebox.showinfo("Уведомление", f'Слово "{word}" уже есть в словаре.')
        editing_menu(dict_tuple, buttons_config=2)
    else:
        def_list = from_word_to_list(word)
        if def_list != 1:
            definition = " ".join(word for sublist in def_list for word in sublist)
            cursor.execute(
                "INSERT INTO dictionary (word, definition, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP)",
                (word, definition),
            )
            connection.commit()
            messagebox.showinfo(
                "Уведомление",
                f'Слово "{word}" найдено онлайн, выберите дальнейшие действия.',
            )
            cursor.execute("SELECT * FROM dictionary WHERE word=?", (word,))
            dict_tuple = cursor.fetchone()
            editing_menu(dict_tuple, buttons_config=1)
        else:
            main_menu()


def delete_word(word):
    cursor.execute("DELETE FROM dictionary WHERE word = ?", (word,))
    connection.commit()


#####################################################################################################################################################
# EDITING MENU FUNCTIONS
#####################################################################################################################################################
def editing_menu(dict_tuple, buttons_config=0, list_settings=None):
    # buttons_config = 0 - all buttons are present, default names;
    # 1 - two buttons, 2nd button - Не сохранять, for 1st encounter
    # 2 - two buttons, 2nd button - Удалить (default)
    destroy_current_frame()
    edit_frame = tk.Frame(root, bg="linen")
    edit_frame.pack(fill="both", expand=True)
    global current_frame
    current_frame = edit_frame

    the_word = dict_tuple[1]
    label = tk.Label(edit_frame, text=f"{the_word}", font=("Arial", 20), bg="linen")
    label.pack(pady=20)

    edit_entry = tk.scrolledtext.ScrolledText(edit_frame, height=10, width=70)
    edit_entry.insert("1.0", dict_tuple[2])
    edit_entry.pack()

    embolden(edit_entry)
    editing_buttons(edit_frame, the_word, edit_entry, list_settings, buttons_config)


def embolden(edit_entry):
    needed_font = font.Font(size=12, weight="bold")
    edit_entry.tag_configure("bold", font=needed_font)

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
    for i in parts_of_speech:
        start_index = "1.0"
        while True:
            start_index = edit_entry.search(i, start_index, stopindex=tk.END)
            if not start_index:
                break
            end_index = f"{start_index}+{len(i)}c"
            edit_entry.tag_add("bold", start_index, end_index)
            start_index = end_index


def editing_buttons(edit_frame, the_word, edit_entry, list_settings, buttons_config):
    button_frame = tk.Frame(edit_frame, bg="linen")
    button_frame.pack()

    button1 = tk.Button(
        button_frame,
        text="Сохранить",
        command=lambda: (
            update_word(the_word, edit_entry.get("1.0", "end-1c")),
            main_menu() if list_settings is None else word_list(*list_settings),
        ),
    )
    button1.pack(side="left", padx=5)

    button2 = tk.Button(
        button_frame,
        text="Не сохранять" if buttons_config == 1 else "Удалить",
        command=lambda: (
            delete_word(the_word),
            messagebox.showinfo("Уведомление", f"Слово удалено"),
            word_list(*list_settings) if list_settings else main_menu(),
        ),
    )
    button2.pack(side="left", padx=5)
    if buttons_config !=1:
        button3 = tk.Button(
            button_frame,
            text="Обнулить прогресс",
            command=lambda: change_stage(the_word, 1, change_rev_date=None, nullify=1),
        )
        button3.pack(side="left", padx=5)

    if buttons_config == 0:
        sorting_frame = tk.Frame(edit_frame, bg="linen")
        sorting_frame.pack(pady=10)
        word_list_button = tk.Button(
            sorting_frame,
            text="Список слов",
            command=lambda: word_list(*list_settings),
        )
        word_list_button.pack(side="left", padx=5)
        back_button = tk.Button(sorting_frame, text="Главное меню", command=main_menu)
        back_button.pack(side="left", padx=5)


def update_word(word, definition):
    cursor.execute(
        "UPDATE dictionary SET definition = ?, updated_at = CURRENT_TIMESTAMP WHERE word = ?",
        (definition, word),
    )
    connection.commit()

    cursor.execute("SELECT definition FROM dictionary WHERE word = ?", (word,))
    result = cursor.fetchone()
    if result:
        messagebox.showinfo("Уведомление", f"Данное определение добавлено")


#####################################################################################################################################################
# WORD LIST
#####################################################################################################################################################
def word_list(
    sort_arg="дате создания", prev_sort_arg=None, page=0, order_arg=0, sort_clicked=0
):
    list_settings = (sort_arg, prev_sort_arg, page, order_arg, sort_clicked)

    order_arg = switch_order(sort_arg, prev_sort_arg, order_arg, sort_clicked)

    rows, number_of_rows, max_page = get_rows(sort_arg, order_arg, page)

    if rows:
        word_list_frame = setup_frame_and_list(rows, page, list_settings)

        lower_navigation(word_list_frame, number_of_rows, sort_arg, max_page, page)
        page_buttons(
            word_list_frame, page, max_page, number_of_rows, sort_arg, order_arg
        )
        sorting_buttons(word_list_frame, sort_arg, order_arg, page)

    else:
        messagebox.showerror(
            "Ошибка!", "Словарь пуст. Добавьте слова, чтобы начать их изучение"
        )
        main_menu()
    


def switch_order(sort_arg, prev_sort_arg, order_arg, sort_clicked):
    if prev_sort_arg == sort_arg and sort_clicked == 1:
        order_arg = (order_arg + 1) % 2
    return order_arg


def get_rows(sort_arg, order_arg, page):
    sorting_kinds = {
        "дате изменения": "updated_at ",
        "алфавиту": "word COLLATE NOCASE ",
        "дате создания": "created_at ",
    }
    order_kinds = {1: "DESC", 0: "ASC"}
    column_name = sorting_kinds[sort_arg]
    order = order_kinds[order_arg]

    cursor.execute("SELECT COUNT(*) FROM dictionary")
    number_of_rows = cursor.fetchone()[0]
    max_page = (number_of_rows - 1) // 10

    page = min(page, max_page)

    current_range = page * 10
    cursor.execute(
        f"SELECT * FROM dictionary ORDER BY {column_name}{order} LIMIT 10 OFFSET {current_range}"
    )
    rows = cursor.fetchall()

    return rows, number_of_rows, max_page


def setup_frame_and_list(rows, page, list_settings):
    destroy_current_frame()
    word_list_frame = tk.Frame(root, bg="linen")
    word_list_frame.pack(fill="both", expand=True)
    global current_frame
    current_frame = word_list_frame

    for i, dict_tuple in enumerate(rows, start=1 + page * 10):
        button = tk.Button(
            word_list_frame,
            text=f"{i}) {dict_tuple[1]}",
            wraplength=600,
            anchor="center",
            width=75,
            command=lambda t=dict_tuple: editing_menu(t, list_settings=list_settings),
        )
        button.pack(anchor="w", padx=3)

    return word_list_frame


def lower_navigation(word_list_frame, number_of_rows, sort_arg, max_page, page):
    lower_frame = tk.Frame(word_list_frame, bg="linen")
    lower_frame.pack(side="bottom", pady=(0, 5))

    back_button = tk.Button(
        word_list_frame,
        text="...",
        command=lambda: (main_menu())
    )
    back_button.place(x=2, y=412)

    if number_of_rows > 10:
        specific_page_edit_entry = tk.Entry(lower_frame, width=5)
        specific_page_edit_entry.pack(side="left")
        go_to_page = tk.Button(
            lower_frame,
            text="Перейти",
            command=lambda: word_list(
                sort_arg,
                page=input_validation(specific_page_edit_entry.get(), max_page, page),
            ),
        )
        go_to_page.pack(side="left")


def page_buttons(word_list_frame, page, max_page, number_of_rows, sort_arg, order_arg):
    forward_back_frame = tk.Frame(word_list_frame, bg="linen")
    forward_back_frame.pack(side="bottom", pady=3)

    if page > 0:
        prev_button = tk.Button(
            forward_back_frame,
            text="Назад",
            command=lambda: word_list(sort_arg, page=page - 1, order_arg=order_arg),
        )
        prev_button.pack(side="left")

    if page > 0 or (page * 10) + 10 < number_of_rows:
        page_label = tk.Label(
            forward_back_frame, text=f"Страница {page + 1}/{max_page + 1}", bg="linen"
        )
        page_label.pack(side="left")

    if (page * 10) + 10 < number_of_rows:
        next_button = tk.Button(
            forward_back_frame,
            text="Вперёд",
            command=lambda: word_list(sort_arg, page=page + 1, order_arg=order_arg),
        )
        next_button.pack(side="left")


def sorting_buttons(word_list_frame, sort_arg, order_arg, page):
    sorting_frame = tk.Frame(word_list_frame, bg="linen")
    sorting_frame.pack(side="bottom")

    selected_option = tk.StringVar()
    selected_option.set(sort_arg)

    s_button_text = "Сортировать по ↑" if order_arg == 0 else "Сортировать по ↓"
    sort_button = tk.Button(
        sorting_frame,
        text=s_button_text,
        command=lambda: word_list(
            selected_option.get(),
            prev_sort_arg=sort_arg,
            order_arg=order_arg,
            sort_clicked=1,
            page=page,
        ),
    )
    sort_button.pack(side="left")

    dropdown = tk.OptionMenu(
        sorting_frame,
        selected_option,
        "дате изменения",
        "алфавиту",
        "дате создания",
    )
    dropdown.pack(side="left")


def input_validation(input_value, max_page, current_page):
    try:
        res = int(input_value)
        if res - 1 <= max_page and res > 0:
            return res - 1
        else:
            return current_page
    except ValueError:
        return current_page


#####################################################################################################################################################
# LEARN PAGE
#####################################################################################################################################################

def learn(the_word=None, reverse_side=0, advance=0):
    if is_dict_empty() == True:
        messagebox.showerror(
            "Ошибка!", "Словарь пуст. Добавьте слова, чтобы начать их изучение"
        )
        return 
         
    learning_stages = {
        1: {"sql": None, "rus": "<1 мин"},
        2: {"sql": "+5 minute", "rus": "<5 мин"},
        3: {"sql": "+10 minute", "rus": "<10 мин"},
        4: {"sql": "+1 hour", "rus": "<1 час"},
        5: {"sql": "+1 day", "rus": "1 день"},
        6: {"sql": "+3 day", "rus": "3 дней"},
        7: {"sql": "+7 day", "rus": "7 дней"},
        8: {"sql": "+14 day", "rus": "14 дней"},
        9: {"sql": "+21 day", "rus": "21 дней"},
        10: {"sql": "+1 month", "rus": "1 месяц"},
        11: {"sql": "+2 month", "rus": "2 месяца"},
        12: {"sql": "+3 month", "rus": "3 месяца"},
        13: {"sql": "+6 month", "rus": "6 месяцев"},
        14: {"sql": "+9 month", "rus": "9 месяцев"},
        15: {"sql": "+12 month", "rus": "1 год"},
    }

    if not the_word:
        the_word, dict_tuple = get_word_to_learn(advance, learning_stages)
        if not the_word:
            return

    else:
        cursor.execute("""SELECT * FROM dictionary WHERE word=?;""", (the_word,))
        dict_tuple = cursor.fetchone()

    learn_frame = set_learning_frame()
    display_word_to_learn(learn_frame, dict_tuple, reverse_side)
    stage_buttons(learn_frame, dict_tuple, reverse_side, learning_stages, advance)


def set_learning_frame():
    destroy_current_frame()
    learn_frame = tk.Frame(root, bg="linen")
    learn_frame.pack(fill="both", expand=True)
    global current_frame
    current_frame = learn_frame
    return learn_frame


def get_word_to_learn(advance, learning_stages):
    how_much_adv = f"+{advance} day"

    cursor.execute(
        "SELECT * FROM dictionary WHERE revision_date <= DATETIME('now',?);",
        (how_much_adv,),
    )
    to_revise = cursor.fetchall()

    if to_revise:
        dict_tuple = random.choice(to_revise)
        return dict_tuple[1], dict_tuple

    for i in range(2, 5):
        cursor.execute(
            "SELECT * FROM dictionary WHERE revision_date <= DATETIME('now',?);",
            (learning_stages[i]["sql"],),
        )
        to_revise = cursor.fetchall()
        if to_revise:
            dict_tuple = random.choice(to_revise)
            return dict_tuple[1], dict_tuple
    res = extend_revision()
    return res


def extend_revision():
    revise_on = simpledialog.askstring(
        "Отлично!",
        "Все слова на сейчас повторены.\nЕсли хотите, выберите на сколько дней\nхотите идти вперёд плана",
    )

    if revise_on:
        valid_revise_on = advance_validation(revise_on)
        if valid_revise_on:
            learn(advance=valid_revise_on)
        else:
            messagebox.showerror("Ошибка!", "Вы ввели недопустимое значение")
            main_menu()
    else:
        main_menu()
    return None, None


def display_word_to_learn(learn_frame, dict_tuple, reverse_side):
    learn_text = f"{dict_tuple[1]}" if reverse_side == 0 else dict_tuple[2]

    if reverse_side == 0:
        label = tk.Label(learn_frame, text=learn_text, font=("Arial", 20), bg="linen")
        label.pack(pady=20)
    else:
        card_displayed = tk.scrolledtext.ScrolledText(
            learn_frame, wrap="word", height=15, width=70
        )
        card_displayed.pack(side="top", pady=10)
        card_displayed.insert("1.0", learn_text)


def stage_buttons(learn_frame, dict_tuple, reverse_side, learning_stages, advance):
    the_word = dict_tuple[1]
    stage_number = dict_tuple[5]

    navigation_frame = tk.Frame(learn_frame, bg="linen")
    navigation_frame.pack(pady=10, side="bottom")
    back = tk.Button(learn_frame, text="...", command=main_menu)
    back.place(x=2, y=412)

    learn_button_frame = tk.Frame(learn_frame, bg="linen")
    learn_button_frame.pack(pady=10, side="bottom")

    if reverse_side == 0:
        button_show = tk.Button(
            learn_button_frame,
            text="Показать",
            command=lambda: learn(the_word=the_word, reverse_side=1, advance=advance),
        )
        button_show.pack(side="left", padx=5, pady=20)
    else:
        button1 = tk.Button(
            learn_button_frame,
            text="<1 мин",
            command=lambda: change_stage(
                the_word, 1, change_rev_date=None, advance=advance
            ),
        )
        button1.pack(side="left", padx=5, pady=20)

        if stage_number != 1:
            button2 = tk.Button(
                learn_button_frame,
                text=f'{learning_stages[stage_number]["rus"]}',
                command=lambda: change_stage(
                    the_word,
                    stage_number,
                    learning_stages[stage_number]["sql"],
                    advance=advance,
                ),
            )
            button2.pack(side="left", padx=5,pady=20 )

        button3 = tk.Button(
            learn_button_frame,
            text=f'{learning_stages[stage_number+1]["rus"]}',
            command=lambda: change_stage(
                the_word,
                stage_number + 1,
                learning_stages[stage_number + 1]["sql"],
                advance=advance,
            ),
        )
        button3.pack(side="left", padx=5, pady=20)

        if stage_number != 15:
            button4 = tk.Button(
                learn_button_frame,
                text=f'{learning_stages[stage_number+2]["rus"]}',
                command=lambda: change_stage(
                    the_word,
                    stage_number + 2,
                    learning_stages[stage_number + 2]["sql"],
                    advance=advance,
                ),
            )
            button4.pack(side="left", padx=5, pady=20)


def change_stage(word, stage, change_rev_date, advance=None, nullify=None):
    if stage > 15:
        stage = 15

    query = (
        """
        UPDATE dictionary
        SET stage = ?, 
            revision_date = DATETIME(revision_date, ?),
            updated_at = CURRENT_TIMESTAMP
        WHERE word = ?;
    """
        if change_rev_date
        else """
        UPDATE dictionary
        SET stage = ?, 
            revision_date = CURRENT_TIMESTAMP,
            updated_at = CURRENT_TIMESTAMP
        WHERE word = ?;
    """
    )
    params = (stage, change_rev_date, word) if change_rev_date else (stage, word)

    cursor.execute(query, params)
    connection.commit()

    if nullify:
        messagebox.showinfo("Уведомление", "Прогресс изучения обнулён")
    else:
        learn(advance=advance)


def advance_validation(revise_on):
    try:
        int_revise_on = int(revise_on)
        return int_revise_on if int_revise_on > 0 else None
    except ValueError:
        return None


#####################################################################################################################################################
# MAIN MENU
#####################################################################################################################################################
def main_menu():

    destroy_current_frame()
    global current_frame
    main_menu_frame = tk.Frame(root, bg="linen")

    current_frame = main_menu_frame

    search_edit_entry = tk.Entry(main_menu_frame, width=30)
    search_edit_entry.pack(pady=(60, 20))

    search_button = tk.Button(
        main_menu_frame,
        text="Найти слово",
        width=25,
        fg="Black",
        command=lambda: what_to_add(search_edit_entry.get()),
    )
    search_button.pack(pady=15, anchor="center")

    list_button = tk.Button(
        main_menu_frame, text="Список слов", width=25, command=word_list
    )
    list_button.pack(pady=15, anchor="center")

    learn_button = tk.Button(
        main_menu_frame, text="Учить слова", width=25, command=learn
    )
    learn_button.pack(pady=15, anchor="center")

    exit_button = tk.Button(main_menu_frame, text="Выйти", width=25, command=root.quit)
    exit_button.pack(pady=15, anchor="center")

    main_menu_frame.pack(fill="both", expand=True)


#####################################################################################################################################################
# GUI AND SQL SETUP
#####################################################################################################################################################
root = tk.Tk()
root.title("Language App")
root.geometry("600x450")
root.configure(bg="linen")
current_frame = None
connection = sqlite3.connect("words.db")
cursor = connection.cursor()
cursor.execute(
    """CREATE TABLE IF NOT EXISTS dictionary (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word TEXT UNIQUE NOT NULL,
    definition TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    stage INTEGER CHECK (stage BETWEEN 1 AND 15) DEFAULT 1,
    revision_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""
)

main_menu()
root.mainloop()

cursor.close()
connection.close()

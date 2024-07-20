from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Выбрать комитет")],
        [KeyboardButton(text="Добавить человека")],
        [KeyboardButton(text="Обновить баллы за ВК активности")],
        [KeyboardButton(text="Выгрузить статистику ГУСС-топа")],
        [KeyboardButton(text="Выгрузить последние действия")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder="Выбери действие из меню",
    selective=True
)

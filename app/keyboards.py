from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from app.database.requests import get_users, get_hw, get_task_status_for_user, get_users_with_rating, get_user_level

profile_kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📝 Домашние задания", callback_data="profile_hw"),
            InlineKeyboardButton(text="🏆 Рейтинг", callback_data="profile_rating")
        ],
        [
            InlineKeyboardButton(text="💼 Материалы", url='https://t.me/+yjWa_F_HzQgzNTIy'),
            InlineKeyboardButton(text="⚙️ Настройки", callback_data="profile_settings")
        ]
    ])

profile_settings_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Изменить ФИ", callback_data="settings_edit_fi")],
        [InlineKeyboardButton(text="↩️ Назад в профиль", callback_data="back_to_profile")]
    ])

profile_settings_edit_user_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Нет ❌', callback_data='no'), InlineKeyboardButton(text='Да ✅', callback_data='yes')],
])

materials_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="💼 Материалы", url='https://t.me/+yjWa_F_HzQgzNTIy')]
])

admin_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Добавить ДЗ 📝', callback_data='add_hw')],
    [InlineKeyboardButton(text='Управлениями пользователями 👥', callback_data='users_managements')],
    [InlineKeyboardButton(text='Просмотр статистики 📊', callback_data='see_statistic')]
])

skip = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Пропустить ⏭️', callback_data='skip')]
])

set_points = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='5'), KeyboardButton(text='10')],
    [KeyboardButton(text='15'), KeyboardButton(text='20')],
    [KeyboardButton(text='25'), KeyboardButton(text='30')],
], resize_keyboard=True, one_time_keyboard=True)

finish_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="✅ Завершить отправку")]
], resize_keyboard=True)


async def get_rating_users():
    keyboard = InlineKeyboardBuilder()
    users = await get_users_with_rating()

    for user in users:
        level_info = await get_user_level(user.points)
        rating = getattr(user, '_rating', 0)

        if rating == 1:
            emoji = "🥇"
        elif rating == 2:
            emoji = "🥈"
        elif rating == 3:
            emoji = "🥉"
        else:
            emoji = "🔹"

        button_text = f"{emoji}{rating}. {user.su} | {level_info['name']} | {user.points} баллов."

        keyboard.add(InlineKeyboardButton(
            text=button_text,
            callback_data=f'rating_{user.id}'
        ))

    keyboard.add(InlineKeyboardButton(
        text="↩️ Назад в профиль",
        callback_data="back_to_profile"
    ))

    return keyboard.adjust(1).as_markup()


async def get_homeworks():
    keyboard = InlineKeyboardBuilder()
    tasks = await get_hw()

    for task in tasks:
        keyboard.add(InlineKeyboardButton(text=f'{task.task_name} | {task.points}', callback_data=f'task_{task.id}'))
    keyboard.add(InlineKeyboardButton(text="↩️ Назад в профиль", callback_data="back_to_profile"))

    return keyboard.adjust(1).as_markup()


async def hw_kb(task, tg_id):
    task_status = await get_task_status_for_user(tg_id, task.id)

    if task_status == 'in progress ⌛️':
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='На проверке ⌛️', callback_data='in_progress')],
            [InlineKeyboardButton(text="↩️ Назад в профиль", callback_data="back_to_profile")]
        ])
    elif task_status == 'approved ✅':
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Проверено ✅', callback_data='approved')],
            [InlineKeyboardButton(text="↩️ Назад в профиль", callback_data="back_to_profile")]
        ])
    elif task_status == 'declined ❌':
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Отклоненно ❌', callback_data='declined')],
            [InlineKeyboardButton(text="↩️ Назад в профиль", callback_data="back_to_profile")]
        ])
    else:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Сдать на проверку 📝', callback_data=f'send_hw_{task.id}')],
            [InlineKeyboardButton(text="↩️ Назад в профиль", callback_data="back_to_profile")]
        ])


async def get_users_kb():
    users = await get_users()
    keyboard = InlineKeyboardBuilder()

    for user in users:
        keyboard.add(InlineKeyboardButton(text=f'{user.su}', callback_data=f'check_user_hw_{user.tg_id}'))
    return keyboard.adjust(2).as_markup()

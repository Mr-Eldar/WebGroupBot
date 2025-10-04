import asyncio
from _datetime import datetime

from aiogram import Router, F
from aiogram.enums import ChatAction
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, TelegramObject, InputMediaPhoto, ReplyKeyboardRemove
from aiogram.filters import CommandStart, Command

from app.database.requests import *
from app.keyboards import *
from app.states import *

user = Router()


async def send_typing_action(event: TelegramObject):
    user_id = getattr(event.from_user, 'id', None)
    bot = getattr(event, 'bot', None)

    if bot and user_id:
        await bot.send_chat_action(chat_id=user_id, action=ChatAction.TYPING)
        await asyncio.sleep(0.5)


@user.message(CommandStart())
async def cmd_start(message: Message):
    await send_typing_action(message)
    await message.answer_sticker('CAACAgUAAxkBAAEPXzZoxsCW7T8qaMp_-9lOzggZ6c5-xwACXhQAArP_iVVdQXtnlQYGRTYE')
    await message.answer('🚀 <b>Добро пожаловать в цифровое пространство 4-й группы!</b>\n\n'
        'Я твой персональный ассистент в мире веб-разработки. Здесь ты сможешь:\n\n'
        
        '✅ Принимать вызовы (ДЗ)\n'
        '✅ Следить за прогрессом\n' 
        '✅ Соревноваться с другими\n'
        '✅ Стать лучшим разработчиком\n\n'
        
        '📊 Твой статус: <b>Новичок</b>\n'
        '‼️‼️ ➡️ Напиши <b>/profile</b> чтобы бот корректно работал ‼️‼️\n\n'
        
        '<b>Не теряй время — код ждет!</b> 💻')


@user.message(Command('help'))
async def cmd_help(message: Message):
    await send_typing_action(message)
    await message.answer_sticker('CAACAgIAAxkBAAEPXzRoxsAcKrXTtcGuID5HfPM4VteRnAAChwIAAladvQpC7XQrQFfQkDYE')
    await message.answer('👋 Добро пожаловать в <b>WebBot4Group</b>, официального бота для нашей группы!\n\n'
        'Я здесь, чтобы помочь вам организовать учебный процесс и сделать его более эффективным.\n\n'

        '📌 <b>ЧТО Я УМЕЮ</b>:\n\n'

        '<b>Для учеников:</b>\n'
        '✅ Отслеживание всех домашних заданий и дедлайнов\n'
        '✅ Личный кабинет с вашей статистикой и рейтингом\n'
        '✅ Удобная система отметки о выполнении ДЗ\n'
        '✅ Рейтинговая система с баллами за выполненные задания\n'
        '✅ История всех ваших выполненных работ\n\n'

        '<b>Для преподавателя:</b>\n'
        '🎓 Простая публикация новых заданий\n'
        '🎓 Контроль выполнения ДЗ всеми студентами\n'
        '🎓 Система автоматического начисления баллов\n'
        '🎓 Просмотр статистики по группе\n\n'

        '🔹 <b>С чего начать?</b>\n'
        'Если вы еще не зарегистрированы - просто введите свое ФИО когда я попрошу.\n\n'

        '🔹 <b>Основные команды:</b>\n'
        '<b>/start</b> - начать работу\n'
        '<b>/profile</b> - ваш личный кабинет\n'
        '<b>/hw</b> - посмотреть текущие задания\n'
        '<b>/rating</b> - рейтинг группы\n'
        '<b>/history</b> - история выполненных заданий\n\n'

        'Разработано специально для 4 группы веб-разработки! 🚀')


@user.message(Command('profile'))
@user.callback_query(F.data == 'back_to_profile')
async def cmd_profile(event: Message | CallbackQuery, state: FSMContext):
    user = await find_user(event.from_user.id)
    await update_user_ratings()
    await send_typing_action(event)
    if isinstance(event, Message):
        if not user:
            await event.answer('🎯 <b>Начни свой путь в веб-разработке!</b>\n\n'
                                'Для старта нужно создать аккаунт. <b>Введи свое ФИ чтобы:</b>\n\n'

                                '✨ Получить доступ к ДЗ и проектам\n'
                                '📊 Начать отслеживать свой прогресс\n'
                                '🏆 Занять место в рейтинге группы\n\n'

                                'Введи ФИО в формате: <b>Фамилия Имя</b>\n\n'

                                '<b>Готовы стать лучшим разработчиком?</b> 💻')
            await state.set_state(Reg.sn)
        else:
            level_info = await get_user_level(user.points)

            await event.answer(
                f'📊 <b>УЧЕБНЫЙ DASHBOARD — {user.su}</b>\n\n'
                f'👤 <b>ПРОФИЛЬ</b>\n'
                f'<b>ID: {event.from_user.id}</b>\n'
                f'<b>Группа: Web-4</b>\n'
                f'<b>Уровень: {level_info["name"]}</b>\n'
                f'<b>Прогресс: {get_level_progress_bar(level_info["progress"])}</b>\n\n'
                f'📈 <b>СТАТИСТИКА</b>\n'
                f'💯 Всего баллов: {user.points}\n'
                f'✅ Выполнено ДЗ: {user.completed_hw}\n'
                f'🏆 Рейтинг: #{user.rating}\n\n'
                f'📋 <b>БЫСТРЫЕ ДЕЙСТВИЯ</b>\n'
                '/hw — Все задания\n'
                '/rating — Полный рейтинг\n'
                '/materials — Учебные материалы\n'
                '/help — Помощь\n\n',
                reply_markup=profile_kb
            )
    else:
        if not user:
            await event.message.answer('🎯 <b>Начни свой путь в веб-разработке!</b>\n\n'
                            'Для старта нужно создать аккаунт. <b>Введи свое ФИ чтобы:</b>\n\n'

                            '✨ Получить доступ к ДЗ и проектам\n'
                            '📊 Начать отслеживать свой прогресс\n'
                            '🏆 Занять место в рейтинге группы\n\n'

                            'Введи ФИО в формате: <b>Фамилия Имя</b>\n\n'

                            '<b>Готовы стать лучшим разработчиком?</b> 💻')
            await state.set_state(Reg.sn)
        else:
            user = await find_user(event.from_user.id)
            user_profile = await find_user_by_id(user.id)  # Нужно создать эту функцию
            level_info = await get_user_level(user_profile.points)

            await event.message.edit_text(
                f'📊 <b>УЧЕБНЫЙ DASHBOARD — {user.su}</b>\n\n'
                f'👤 <b>ПРОФИЛЬ</b>\n'
                f'<b>ID: {event.from_user.id}</b>\n'
                f'<b>Группа: Web-4</b>\n'
                f'<b>Уровень: {level_info["name"]}</b>\n'
                f'<b>Прогресс: {get_level_progress_bar(level_info["progress"])}</b>\n\n'
                f'📈 <b>СТАТИСТИКА</b>\n'
                f'💯 Всего баллов: {user.points}\n'
                f'✅ Выполнено ДЗ: {user.completed_hw}\n'
                f'🏆 Рейтинг: #{user_profile.rating}\n\n'
                f'📋 <b>БЫСТРЫЕ ДЕЙСТВИЯ</b>\n'
                '/hw — Все задания\n'
                '/rating — Полный рейтинг\n'
                '/materials — Учебные материалы\n'
                '/help — Помощь\n\n',
                reply_markup=profile_kb
            )


@user.message(Command('hw'))
@user.callback_query(F.data == 'profile_hw')
async def cmcq_hw(event: Message | CallbackQuery):
    if isinstance(event, Message):
        user = await find_user(event.from_user.id)
        level_info = await get_user_level(user.points)
        await send_typing_action(event)
        await event.answer('📚 <b>Мои домашние задания</b>\n\n'
                        '📊 <b>Общая статистика:</b>\n'
                        f'✅ Выполнено: {user.completed_hw}\n'
                        f'🔴 Просрочено: {user.expired_hw}\n'    
                        f'💯 <b>Набрано баллов:</b> {user.points}\n'
                        f'🏆 <b>Уровень:</b> {level_info["name"]}\n\n'    
                        '🎯 <b>Доступные действия:</b>\n'
                        '• 📋 Посмотреть все задания\n'
                        '• ⏰ Ближайшие дедлайны\n'
                        '• ✅ Выполненные работы\n'
                        '• 🎯 Выбрать задание для выполнения\n\n'   
                        'Выбери нужный раздел:', reply_markup=await get_homeworks())
    else:
        user = await find_user(event.from_user.id)
        level_info = await get_user_level(user.points)
        await send_typing_action(event)
        await event.message.edit_text('📚 <b>Мои домашние задания</b>\n\n'
                        '📊 <b>Общая статистика:</b>\n'
                        f'✅ Выполнено: {user.completed_hw}\n'
                        f'🔴 Просрочено: {user.expired_hw}\n'
                        f'💯 <b>Набрано баллов:</b> {user.points}\n'
                        f'🏆 <b>Уровень:</b> {level_info["name"]}\n\n'
                        '🎯 <b>Доступные действия:</b>\n'
                        '• 📋 Посмотреть все задания\n'
                        '• ⏰ Ближайшие дедлайны\n'
                        '• ✅ Выполненные работы\n'
                        '• 🎯 Выбрать задание для выполнения\n\n'
                        'Выбери нужный раздел:', reply_markup=await get_homeworks())


@user.message(Command('rating'))
@user.callback_query(F.data == 'profile_rating')
async def clb_rating_list(event: Message | CallbackQuery):
    await update_user_ratings()
    if isinstance(event, Message):
        user_obj = await find_user(event.from_user.id)
    else:
        user_obj = await find_user(event.from_user.id)

    if not user_obj:
        if isinstance(event, Message):
            await event.answer("❌ Пользователь не найден. Используйте /profile")
        else:
            await event.answer("❌ Пользователь не найден")
        return

    await send_typing_action(event)

    if isinstance(event, Message):
        await event.answer_sticker('CAACAgIAAxkBAAEPXzhoxsDcFdEF2pFVN312vT9FPV7DdgACfgIAAladvQpBYnRfUWys5DYE')
        await event.answer('📊 <b>Рейтинговая система</b>\n\n'
                        'Смотри свой прогресс и сравни с другими студентами группы.\n\n'
                        f'🏆 <b>Твоя позиция:</b> #{user_obj.rating}\n'
                        f'💯 <b>Баллов:</b> {user_obj.points}\n'
                        f'✅ <b>Выполнено:</b> {user_obj.completed_hw}',
                        reply_markup=await get_rating_users())
    else:
        await event.message.edit_text('📊 <b>Рейтинговая система</b>\n\n'
                                    'Смотри свой прогресс и сравни с другими студентами группы.\n\n'
                                    f'🏆 <b>Твоя позиция:</b> #{user_obj.rating}\n'
                                    f'💯 <b>Баллов:</b> {user_obj.points}\n'
                                    f'✅ <b>Выполнено:</b> {user_obj.completed_hw}',
                                    reply_markup=await get_rating_users())


@user.message(Command('materials'))
async def cmd_materials(message: Message):
    await send_typing_action(message)
    await message.answer_sticker('CAACAgUAAxkBAAEPX0JoxsGml6RWrwViJTBv48WCmScG1gACZhMAAjWqIVWR0e-We8liMDYE')
    await message.answer('🤩 Плагины, курсы, фишки, все в этом роде здесь 👇', reply_markup=materials_kb)


@user.message(SendHwForCheck.hw_photos, F.text == "✅ Завершить отправку")
async def finish_photo_sending(message: Message, state: FSMContext):
    data = await state.get_data()
    photos = data.get('photos', [])
    findUser = await find_user(message.from_user.id)
    level_info = await get_user_level(findUser.points)

    if not photos:
        await message.answer('❌ Вы не прислали ни одного фото!')
        return

    media_group = []
    for photo_id in photos:
        media_group.append(InputMediaPhoto(media=photo_id))

    await message.bot.send_media_group(1870291778, media=media_group)

    await message.bot.send_message(
        1870291778,
        f"📘 <b>НОВОЕ ДОМАШНЕЕ ЗАДАНИЕ</b>\n"
        f"✨ ━━━━━━━━━━━━━━━━━━ ✨\n\n"
        f"👤 <b>Студент:</b> {findUser.su}\n"
        f"🎯 <b>Уровень:</b> {level_info['name']}\n"
        f"⭐ <b>Баллы:</b> {findUser.points}\n"
        f"✅ <b>Выполнено ДЗ:</b> {findUser.completed_hw}\n\n"
        f"🆔 <code>ID:{message.from_user.id}</code>\n"
        f"🕒 <i>{datetime.now().strftime('%d.%m.%Y %H:%M')}</i>",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Одобрить ДЗ",
                    callback_data=f"check_success_hw_{data['hw_task_id']}"
                ),
                InlineKeyboardButton(
                    text="⚠️ Дз выполненно не правильно",
                    callback_data=f"check_danget_hw_{message.from_user.id}_{data['hw_task_id']}"
                ),
                InlineKeyboardButton(
                    text="❌ Отклонить",
                    callback_data=f"check_reject_hw_{message.from_user.id}_{data['hw_task_id']}"
                )
            ]
        ]),
        parse_mode="HTML"
    )

    await assign_task_to_user(message.from_user.id, data['hw_task_id'])

    await message.answer(
        "🎉 <b>Работа отправлена на проверку!</b>\n\n"
        "📊 Статус: На проверке ⏳\n"
        "⏰ Примерное время: 1-2 дня\n"
        "💬 Ты получишь уведомление когда работу проверят",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardRemove()
    )

    await state.clear()


@user.callback_query(F.data == 'profile_settings')
async def clb_profile_settings(callback: CallbackQuery):
    await send_typing_action(callback)
    await callback.message.edit_text('⚙️ <b>Настройки профиля</b>\n\n'
        'Здесь ты можешь настроить бота под себя:\n'
        '🎨 <b>Изменить ФИ</b> - изменить Фамилию Имя\n\n'
        'Выбери нужный раздел для настройки:', reply_markup=profile_settings_kb)


@user.callback_query(F.data == 'settings_edit_fi')
async def clb_settings_edit_fi(callback: CallbackQuery, state: FSMContext):
    await send_typing_action(callback)
    await callback.message.edit_text('✏️ <b>Редактирование профиля</b>\n\n'
                                    '<i>Захотели изменить свое ФИ? Или допустили ошибку?</i>\n\n'
                                    '<b>Без проблем! Просто напиши свое ФИ заново.</b>')
    await state.set_state(EditUser.new_sn)


@user.callback_query(F.data.startswith('task_'))
async def clb_task_info(callback: CallbackQuery):
    task_id = callback.data.split('_')[1]
    task = await get_hw_by_id(task_id)  # Теперь передается правильный тип
    await send_typing_action(callback)
    await callback.answer()
    await callback.message.edit_text('📚 <b>Новое домашнее задание!</b>\n\n'
                                    f'🎯 <b>Название:</b> {task.task_name}\n'
                                    f'📅 <b>Дедлайн:</b> {task.task_complete_time}\n'
                                    f'💯 <b>Баллы:</b> {task.points}\n\n'
                                    '📋 <b>Описание:</b>\n'
                                    f'<b>{task.task_description}</b>\n\n'
                                    '📎 <b>Материалы:</b>\n'
                                    f'{task.task_materials}\n\n', 
                                    reply_markup=await hw_kb(task, callback.from_user.id))


@user.callback_query(F.data.startswith('send_hw_'))
async def clb_send_hw(callback: CallbackQuery, state: FSMContext):
    await send_typing_action(callback)
    await callback.answer()
    await callback.message.edit_text('📸 <b>Отправка выполненного задания</b>\n\n'
                                    'Пришли фото твоей работы (можно несколько):\n\n'
                                    '🎯 <b>Что можно отправить:</b>\n'
                                    '• Скриншоты кода\n'
                                    '• Фото интерфейса\n'
                                    '• Демонстрацию работы\n'
                                    '• Результаты тестирования\n\n'
                                    '📌 <b>Как отправить:</b>\n'
                                    '1. Нажми на скрепку 📎\n'
                                    '2. Выбери "Галерея" или "Фото"\n'
                                    '3. Выбери несколько фото (удерживай для множественного выбора)\n'
                                    '4. Отправь все сразу')
    task_id = callback.data.split('_')[-1]
    await state.update_data(hw_task_id=task_id)
    await state.set_state(SendHwForCheck.hw_photos)


@user.callback_query(F.data.startswith('rating_'))
async def get_rating_user_info(callback: CallbackQuery):
    await send_typing_action(callback)
    user_id = int(callback.data.split('_')[1])
    user_profile = await find_user_by_id(user_id)  # Нужно создать эту функцию

    if not user_profile:
        await callback.answer("❌ Пользователь не найден")
        return

    # Получаем информацию об уровне
    level_info = await get_user_level(user_profile.points)

    profile_text = (
        f"👤 <b>ПРОФИЛЬ — {user_profile.su}</b>\n\n"
        f"🎯 <b>Уровень:</b> {level_info['name']}\n"
        f"⭐ <b>Баллы:</b> {user_profile.points}\n"
        f"🏆 <b>Рейтинг:</b> #{user_profile.rating}\n"
        f"✅ <b>Выполнено ДЗ:</b> {user_profile.completed_hw}\n\n"
        f"📊 <b>Прогресс уровня:</b> {get_level_progress_bar(level_info['progress'])}\n\n"
    )

    await callback.message.edit_text(
        profile_text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='↩️ Назад в рейтинг', callback_data='profile_rating')]
        ])
    )
    await callback.answer()


@user.callback_query(F.data == 'in_progress')
async def clb_task_in_progress(callback: CallbackQuery):
    await callback.answer('Ваше задание уже на проверке учителем. ⌛️')


@user.callback_query(F.data == 'approved')
async def clb_task_in_progress(callback: CallbackQuery):
    await callback.answer('Ваше задание было успешно пройдено. ✅')


@user.callback_query(F.data == 'declined')
async def clb_task_in_progress(callback: CallbackQuery):
    await callback.answer('Ваше задание было отклонено. ❌')


@user.callback_query(F.data.startswith('check_success_hw_'))
async def check_success_hw_process(callback: CallbackQuery, state: FSMContext):
    try:
        task_id = int(callback.data.split('_')[-1])  # Преобразуем в int
        await state.update_data(task_id=task_id)

        await callback.message.bot.delete_message(callback.message.chat.id, callback.message.message_id - 1)
        await callback.message.answer(
            '👤 Выберите пользователя которому засчитать это ДЗ.',
            reply_markup=await get_users_kb()
        )
        await callback.answer()
        await state.set_state(CheckHw.user_id)
    except Exception as e:
        await callback.answer("❌ Ошибка при обработке")
        print(f"Error: {e}")


@user.callback_query(F.data.startswith('check_reject_hw_'))
async def check_reject_hw_process(callback: CallbackQuery, state: FSMContext):
    try:
        task_id = int(callback.data.split('_')[-1])  # Преобразуем в int
        await state.update_data(task_id=task_id)

        await callback.message.bot.delete_message(callback.message.chat.id, callback.message.message_id - 1)
        await callback.message.answer(
            '👤 Выберите пользователя которому отклонить это ДЗ.',
            reply_markup=await get_users_kb()
        )
        await callback.answer()
        await state.set_state(RejectHw.user_id)
    except Exception as e:
        await callback.answer("❌ Ошибка при обработке")
        print(f"Error: {e}")


@user.callback_query(F.data.startswith('check_danger_hw_'))
async def check_danger_hw_process(callback: CallbackQuery, state: FSMContext):
    try:
        task_id = int(callback.data.split('_')[-1])  # Преобразуем в int
        await state.update_data(task_id=task_id)

        await callback.message.bot.delete_message(callback.message.chat.id, callback.message.message_id)
        await callback.message.answer(
            '👤 Выберите пользователя которому хотите сообщить о неправильном ДЗ.',
            reply_markup=await get_users_kb()
        )
        await callback.answer()
        await state.set_state(DangerHw.user_id)
    except Exception as e:
        await callback.answer("❌ Ошибка при обработке")
        print(f"Error: {e}")


@user.callback_query(CheckHw.user_id, F.data.startswith('check_user_hw_'))
async def check_user_hw_process(callback: CallbackQuery, state: FSMContext):
    try:
        user_id = int(callback.data.split('_')[-1])
        data = await state.get_data()
        task_id = data['task_id']

        task = await get_hw_by_id(task_id)
        points = int(task.points) if isinstance(task.points, str) else task.points

        # Одобряем ДЗ и получаем информацию об уровне
        level_info = await approve_user_hw(user_id, task_id, points)

        # Отправляем уведомление пользователю
        try:
            message_text = (
                "🎉 <b>Ваше ДЗ одобрено!</b>\n\n"
                f"✅ Работа принята\n"
                f"⭐ Вам начислено {points} баллов\n"
            )

            if level_info:
                if level_info["max_level"]:
                    message_text += f"🏆 Достигнут максимальный уровень: {level_info['name']}!\n"
                else:
                    message_text += (
                        f"📈 Новый уровень: {level_info['name']}\n"
                        f"📊 Прогресс: {get_level_progress_bar(level_info['progress'])}\n"
                        f"🎯 До следующего уровня: {level_info['progress']['required'] - level_info['progress']['current']} баллов\n"
                    )

            message_text += "\n📈 Продолжайте в том же духе!"

            await callback.bot.send_message(
                user_id,
                message_text,
                parse_mode="HTML"
            )
        except:
            print(f"Не удалось отправить сообщение пользователю {user_id}")

        await callback.answer("✅ ДЗ успешно одобрено!")
        await callback.message.edit_text(f'✅ ДЗ засчитано пользователю!')

    except Exception as e:
        await callback.answer("❌ Ошибка при одобрении ДЗ")
        print(f"Error: {e}")

    await state.clear()


@user.callback_query(RejectHw.user_id, F.data.startswith('check_user_hw_'))
async def reject_user_hw_process(callback: CallbackQuery, state: FSMContext):
    try:
        await state.update_data(user_id=callback.data.split('_')[-1])
        data = await state.get_data()

        await decline_user_hw(data['user_id'], data['task_id'])

        # Отправляем уведомление пользователю
        try:
            message_text = (
                "❌ <b>Ваше ДЗ было отклонено!</b>\n\n"
            )

            await callback.bot.send_message(
                data['user_id'],
                message_text,
                parse_mode="HTML"
            )
        except:
            print(f"Не удалось отправить сообщение пользователю {data['user_id']}")

        await callback.answer("❌ ДЗ было отклонено!")
        await callback.message.edit_text('❌ ДЗ было отклонено!')

    except Exception as e:
        await callback.answer("❌ Ошибка при одобрении ДЗ")
        print(f"Error: {e}")

    await state.clear()


@user.callback_query(DangerHw.user_id, F.data.startswith('check_user_hw_'))
async def danger_user_hw_process(callback: CallbackQuery, state: FSMContext):
        await callback.answer()
        await state.update_data(user_id=callback.data.split('_')[-1])
        await callback.message.edit_text('✏️ Отлично теперь объясните почему это дз выполненно не правильно.')
        await state.set_state(DangerHw.description)


@user.message(Reg.sn)
async def reg_surname_name(message: Message, state: FSMContext):
    await send_typing_action(message)
    await state.update_data(user_sn=message.text)
    data = await state.get_data()
    await message.answer('🎯 <b>Отлично! Твой профиль создан!</b>\n\n'    
        f'<b>{data['user_sn']}</b>, добро пожаловать в команду будущих разработчиков!\n\n'
        
        f'Твой текущий статус: <b>Новичок</b>\n'
        'Баллов: <b>0</b> → но это ненадолго!\n\n'
        
        '<b>Готов к первому заданию? Жми /hw</b>')
    await set_user(message.from_user.id, data['user_sn'])
    await state.clear()


@user.message(EditUser.new_sn)
async def reg_surname_name(message: Message, state: FSMContext):
    await send_typing_action(message)
    await state.update_data(new_user_sn=message.text)
    await message.answer('⭐️ <b>Отлично ФИ было успешно обновленно!</b>\n\n'
                         'Вы уверены в том, чтобы окончательно обновить информацию о себе?',
                         reply_markup=profile_settings_edit_user_kb)
    await state.set_state(EditUser.sure)
    await message.delete()
    await message.bot.delete_message(message.chat.id, message.message_id - 1)


@user.callback_query(EditUser.sure)
async def reg_surname_name(callback: CallbackQuery, state: FSMContext):
    await send_typing_action(callback)
    if F.data == 'yes':
        await callback.answer('🎉 Поздравляем, информация о вас была успешно обновлена')
        data = await state.get_data()
        await edit_user(callback.from_user.id, data['new_user_sn'])
        await cmd_profile(callback, state)
    elif F.data == 'no':
        await cmd_profile(callback, state)
        await state.clear()
    await state.clear()


@user.message(SendHwForCheck.hw_photos, F.photo)
async def hw_send_photos(message: Message, state: FSMContext):
    data = await state.get_data()
    photos = data.get('photos', [])

    photos.append(message.photo[-1].file_id)
    await state.update_data(photos=photos)

    # Просим прислать еще или завершить
    await message.answer(
        "📸 Фото добавлено! Пришлите еще или нажмите '✅ Завершить отправку'",
        reply_markup=finish_kb
    )


@user.message(DangerHw.description)
async def danger_hw(message: Message, state: FSMContext):
    try:
        await state.update_data(danger_desc=message.text)
        data = await state.get_data()

        await danger_user_hw(data['user_id'], data['task_id'])

        # Отправляем уведомление пользователю
        try:
            message_text = (
                "❌ <b>Ваше ДЗ было отклонено!\n"
                f"По причине: {data['danger_desc']}</b>\n\n"
            )

            await message.bot.send_message(
                data['user_id'],
                message_text,
                parse_mode="HTML"
            )
        except:
            print(f"Не удалось отправить сообщение пользователю {data['user_id']}")

        await message.answer("❌ ДЗ было отклонено!")

    except Exception as e:
        await message.answer("❌ Ошибка при отклонении ДЗ")
        print(f"Error: {e}")

    await state.clear()
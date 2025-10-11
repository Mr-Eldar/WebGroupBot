from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Filter, CommandStart, Command

from app.keyboards import *
from app.states import *
from app.database.requests import add_task

admin = Router()


class Admin(Filter):
    def __init__(self):
        self.admins = [1870291778, 5221334023]

    async def __call__(self, message: Message):
        return message.from_user.id in self.admins
    

@admin.message(Admin(), Command('admin'))
async def cmd_start(message: Message):
        await message.answer_sticker('CAACAgIAAxkBAAEPX7loxtKsgYJJycyXX2WAIX1ztonXugACeAIAAladvQr8ugi1kX0cDDYE')
        await message.answer('⚙️ <b>Панель администратора</b>\n\n'
                            'Добро пожаловать в систему управления ботом! Здесь вы можете управлять учебным процессом.\n\n'
                            '📋 <b>Доступные функции:</b>\n'
                            '• Создание новых заданий 📝\n'
                            '• Управление пользователями 👥\n'
                            '• Просмотр статистики 📊\n\n'
                            '💡 <b>Используйте кнопки ниже для управления</b>', reply_markup=admin_kb)


@admin.message(Admin(), Command('send_report'))
async def cmd_send_report(message: Message, state: FSMContext):
    await message.answer(f'Укажите <b>телеграм ID</b> пользователя для того чтобы отправить ему репорт.')
    await state.set_state(SendReport.telegram_ID)


@admin.callback_query(F.data == 'add_hw')
async def clb_add_hw(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text('📝 <b>Создание ДЗ</b>\n\n'    
    'Чтобы создать новое задание, вам понадобится:\n\n'
    '• Название (например: "Создать сайт-портфолио") 🎯\n'
    '• Описание требований и задач 📋\n'
    '• Дедлайн сдачи (формат: ДД.ММ.ГГГГ ЧЧ:ММ) 📅\n'
    '• Количество баллов (0-15) 💯\n\n'
    '<b>Дополнительно:</b> 📎\n'
    '• Файлы с материалами 📎\n'
    '• Ссылки на ресурсы 🎯 \n'
    '• Примеры выполнения 📋\n\n'
    '<b>Напиши название задания чтобы начать:</b>')
    await state.set_state(CreateTask.taskName)


@admin.message(CreateTask.taskName)
async def st_task_name(message: Message, state: FSMContext):
    if not message.text:
        await message.answer('❌ Извините, но мне кажется вы отправили мне, явно не текст.')
        return
    await state.update_data(task_name=message.text)
    await message.delete()
    await message.bot.delete_message(message.chat.id, message.message_id - 1)
    await message.answer('📋 <b>Описание задания</b>\n\n'
    'Опишите что нужно сделать студентам:\n\n'
    'Пример: <i>"Создать одностраничный сайт-портфолио с использованием HTML, CSS и JavaScript. Должны быть разделы: о себе, проекты, контакты."</i>')
    await state.set_state(CreateTask.taskDesc)


@admin.message(CreateTask.taskDesc)
async def st_task_desc(message: Message, state: FSMContext):
    if not message.text:
        await message.answer('❌ Извините, но мне кажется вы отправили мне, явно не текст.')
        return
    await state.update_data(task_desc=message.text)
    await message.delete()
    await message.bot.delete_message(message.chat.id, message.message_id - 1)
    await message.answer('⏰ <b>Дедлайн сдачи</b>\n\n'
    'Укажи когда нужно сдать задание:\n\n'
    'Пример: <i>"25.12.2024 23:59"</i>')
    await state.set_state(CreateTask.taskCompleteTime)


@admin.message(CreateTask.taskCompleteTime)
async def st_task_complete_time(message: Message, state: FSMContext):
    if not message.text:
        await message.answer('❌ Извините, но мне кажется вы отправили мне, явно не текст.')
        return
    await state.update_data(task_complete_time=message.text)
    await message.delete()
    await message.bot.delete_message(message.chat.id, message.message_id - 1)
    await message.answer('💯 <b>Награда за задание</b>\n\n'
    'Сколько баллов получит студент?\n\n'
    'Пример: <b>15</b>', reply_markup=set_points)
    await state.set_state(CreateTask.taskMaterials)


@admin.message(CreateTask.taskMaterials)
async def st_task_complete_points(message: Message, state: FSMContext):
    if not message.text:
        await message.answer('❌ Извините, но мне кажется вы отправили мне, явно не текст.')
        return
    await state.update_data(task_complete_points=message.text)
    await message.delete()
    await message.bot.delete_message(message.chat.id, message.message_id - 1)
    await message.answer('📎 <b>Дополнительные материалы</b>\n\n'
                            'Можно прикрепить:\n\n'
                            '• Ссылки на ресурсы 🔗\n'
                            '• Примеры выполнения 🎯\n'
                            '• Фото задания только одно. 📎\n\n'
                            '<b>Или нажмите "Пропустить"</b> ⏭️', reply_markup=skip)
    await state.set_state(CreateTask.taskFinallyAdd)


@admin.callback_query(CreateTask.taskFinallyAdd)
@admin.message(CreateTask.taskFinallyAdd)
async def st_task_finally_add(event: Message | CallbackQuery, state: FSMContext):
    if isinstance(event, Message):
        users = await get_users()
        if event.photo:
            await state.update_data(task_finally_add=event.photo[-1].file_id)
        else:
            await state.update_data(task_finally_add=event.text)
        data = await state.get_data()
        await add_task(data['task_name'], data['task_desc'], data['task_complete_time'], data['task_complete_points'],
                    data['task_finally_add'])
        await event.answer('✅ <b>Задание успешно создано!</b>\n\n'
                            f'🎯 <b>{data['task_name']}</b>\n'
                            f'📅 <b>Дедлайн:</b> {data['task_complete_time']}\n'
                            f'💯 <b>Баллы:</b> {data['task_complete_points']}\n\n'
                            f'📊 <b>Статус:</b> Опубликовано для всех студентов\n'
                            '📢 Уведомления отправлены\n'
                            '⏰ Напоминание придет за 24 часа\n\n'
                            '💡 <i>Студенты уже видят задание в списке ДЗ</i>')
        await event.answer('Расслыка уведомления о новом дз пользователям началась.')
        for user in users:
            try:
                if event.photo:
                    await event.bot.send_photo(chat_id=user.tg_id,
                                            photo=data['task_finally_add'],
                                            caption=f'📣 <b>НОВОЕ ДОМАШНЕЕ ЗАДАНИЕ!</b>\n\n'
                                                    f'🎯 <b>{data["task_name"]}</b>\n\n'
                                                    f'📅 <b>Дедлайн:</b> {data["task_complete_time"]}\n'
                                                    f'💯 <b>Баллы:</b> {data["task_complete_points"]}\n\n'
                                                    f'📋 <b>Описание:</b>\n'
                                                    f'<b>{data["task_desc"]}</b>\n\n'
                                                    f'💡 <i>Не откладывай - начинай работать уже сегодня!</i>\n\n'
                                                    f'📝 Используй команду /hw чтобы посмотреть все задания')
                else:
                    await event.bot.send_message(chat_id=user.tg_id,
                                            text=f'📣 <b>НОВОЕ ДОМАШНЕЕ ЗАДАНИЕ!</b>\n\n'
                                                f'🎯 <b>{data['task_name']}</b>\n\n'
                                                f'📅 <b>Дедлайн:</b> {data['task_complete_time']}\n'
                                                f'💯 <b>Баллы:</b> {data['task_complete_points']}\n\n'
                                                f'📋 <b>Описание:</b>\n'
                                                f'<b>{data['task_desc']}</b>\n\n'
                                                f'💡 <i>Не откладывай - начинай работать уже сегодня!</i>\n\n'
                                                f'📝 Используй команду /hw чтобы посмотреть все задания')
            except:
                pass
                await state.clear()
        await event.answer('Расслыка уведомления о новом дз пользователям была окончена.')
        await state.clear()
    else:
        users = await get_users()
        if F.data == 'skip':
            await state.update_data(task_finally_add='Не указанно.')
        data = await state.get_data()
        await event.answer()
        await add_task(data['task_name'], data['task_desc'], data['task_complete_time'], data['task_complete_points'],
                    data['task_finally_add'])
        await event.message.edit_text('✅ <b>Задание успешно создано!</b>\n\n'
                        f'🎯 <b>{data['task_name']}</b>\n'
                        f'📅 <b>Дедлайн:</b> {data['task_complete_time']}\n'
                        f'💯 <b>Баллы:</b> {data['task_complete_points']}\n\n'
                        f'📊 <b>Статус:</b> Опубликовано для всех студентов\n'
                        '📢 Уведомления отправлены\n'
                        '⏰ Напоминание придет за 24 часа\n\n'
                        '💡 <i>Студенты уже видят задание в списке ДЗ</i>')
        await event.message.answer('Расслыка уведомления о новом дз пользователям началась.')
        for user in users:
            try:
                await event.message.bot.send_message(chat_id=user.tg_id,
                                            text=f'📣 <b>НОВОЕ ДОМАШНЕЕ ЗАДАНИЕ!</b>\n\n'
                                                f'🎯 <b>{data['task_name']}</b>\n\n'
                                                f'📅 <b>Дедлайн:</b> {data['task_complete_time']}\n'
                                                f'💯 <b>Баллы:</b> {data['task_complete_points']}\n\n'
                                                f'📋 <b>Описание:</b>\n'
                                                f'<b>{data['task_desc']}</b>\n\n'
                                                f'💡 <i>Не откладывай - начинай работать уже сегодня!</i>\n\n'
                                                f'📝 Используй команду /hw чтобы посмотреть все задания')
            except:
                pass
                await state.clear()
        await event.message.answer('Расслыка уведомления о новом дз пользователям была окончена.')
        await state.clear()


@admin.message(Admin(), SendReport.telegram_ID)
async def get_report_tg_id(message: Message, state: FSMContext):
    if len(message.text) < 10:
        await message.answer('❌ Некорректный ID!')
        return
    await state.update_data(telegram_id=message.text)
    await message.answer('Теперь опишите ваш репорт.')
    await state.set_state(SendReport.description)


@admin.message(Admin(), SendReport.description)
async def get_report_tg_id(message: Message, state: FSMContext):
    await state.update_data(report_desc=message.text)
    data = await state.get_data()
    await message.bot.send_message(chat_id=data['telegram_id'], text=f'Здраствуйте уважаемый пользователь {message.from_user.first_name} телеграмм бота <b>Web-Разработка</b> 💻\n\n'
                                                                     f'Вас беспокоит администрация данного тг бота, по причине: {data["report_desc"]}\n\n'
                                                                     f'Мы даем вам первое предупреждение, за нарушение правил пользования ботом.\n'
                                                                     f'<b>Еще одно замечание и вы будете удалены из бота.</b>\n\n'
                                                                     f'Просим понять нас и выполнить наши просьбы.')
    await message.answer('Пользователь получил предупреждение.')
    await state.clear()
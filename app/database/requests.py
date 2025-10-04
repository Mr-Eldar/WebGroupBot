from app.database.models import async_session
from app.database.models import User, Task, UserTask
from sqlalchemy import select, update, delete, desc


LEVEL_SYSTEM = {
    1: {"name": "Новичок 🟢", "points_required": 0},
    2: {"name": "Ученик 📚", "points_required": 50},
    3: {"name": "Разработчик 💻", "points_required": 150},
    4: {"name": "Профи 🚀", "points_required": 300},
    5: {"name": "Эксперт 🏆", "points_required": 500},
    6: {"name": "Мастер 🎯", "points_required": 750},
    7: {"name": "Гуру 🌟", "points_required": 1000},
    8: {"name": "Легенда ⚡", "points_required": 1500}
}


async def get_user_level(points: int):
    """Получить уровень пользователя на основе баллов"""
    for level, info in reversed(LEVEL_SYSTEM.items()):
        if points >= info["points_required"]:
            return {
                "level": level,
                "name": info["name"],
                "points_required": info["points_required"],
                "next_level_points": LEVEL_SYSTEM.get(level + 1, {}).get("points_required", None),
                "progress": calculate_level_progress(points, level)
            }
    return LEVEL_SYSTEM[1]


def calculate_level_progress(points: int, current_level: int) -> dict:
    """Рассчитать прогресс до следующего уровня"""
    current_level_points = LEVEL_SYSTEM[current_level]["points_required"]
    next_level_points = LEVEL_SYSTEM.get(current_level + 1, {}).get("points_required")

    if not next_level_points:  # Максимальный уровень
        return {
            "percentage": 100,
            "current": points - current_level_points,
            "required": 0,
            "max_level": True
        }

    level_range = next_level_points - current_level_points
    current_progress = points - current_level_points
    percentage = min(100, int((current_progress / level_range) * 100))

    return {
        "percentage": percentage,
        "current": current_progress,
        "required": level_range,
        "max_level": False
    }


async def update_user_level(tg_id: int):
    """Обновить уровень пользователя в базе данных"""
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if user:
            level_info = await get_user_level(user.points)
            user.level = level_info["name"]  # Сохраняем название уровня
            await session.commit()
            return level_info
        return None


def get_level_progress_bar(progress: dict) -> str:
    """Создать строку прогресс-бара"""
    if progress["max_level"]:
        return "▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ MAX LEVEL! 🎉"

    filled = int(progress["percentage"] / 5)  # 20 символов = 100%
    empty = 20 - filled

    progress_bar = "▓" * filled + "░" * empty
    return f"{progress_bar} {progress['percentage']}%"


async def set_user(tg_id, sn):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        
        if not user:
            session.add(User(tg_id=tg_id, su=sn))
            await session.commit()


async def find_user(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        return user


async def find_user_by_id(user_id: int):
    async with async_session() as session:
        return await session.scalar(select(User).where(User.id == user_id))


async def edit_user(tg_id, new_sn):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if user:
            user.su = new_sn
            await session.commit()
            return user
        return None


async def get_users():
    async with async_session() as session:
        return await session.scalars(select(User))


# ТАСКИ

async def add_task(taskName, taskDesc, taskTime, taskPoints, taskMaterials):
    async with async_session() as session:
        task = await session.scalar(select(Task).where(Task.task_name == taskName))

        if not task:
            # Преобразуем taskPoints в int, если это строка
            points_value = int(taskPoints) if isinstance(taskPoints, str) else taskPoints
            
            session.add(Task(
                task_name=taskName, 
                task_description=taskDesc,
                task_complete_time=taskTime, 
                points=points_value,  # Теперь это число
                task_materials=taskMaterials
            ))
            await session.commit()
        return task


async def assign_task_to_user(tg_id, task_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if user:
            # Преобразуем task_id в число
            task_id_int = int(task_id)
            user_task = await session.scalar(
                select(UserTask).where(
                    UserTask.user_id == user.id,
                    UserTask.task_id == task_id_int  # Используем число
                )
            )

            if not user_task:
                user_task = UserTask(
                    user_id=user.id,
                    task_id=task_id_int,  # Используем число
                    status='in progress ⌛️'
                )
                session.add(user_task)
            else:
                user_task.status = 'in progress ⌛️'

            await session.commit()
            return True
        return False


async def update_task_status(tg_id, status):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if user:
            user.task_status = status
            await session.commit()
            return True
        return False


async def get_task_status_for_user(tg_id, task_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if not user:
            return None

        # Преобразуем task_id в число
        task_id_int = int(task_id) if isinstance(task_id, str) else task_id
        user_task = await session.scalar(
            select(UserTask).where(
                UserTask.user_id == user.id,
                UserTask.task_id == task_id_int  # Используем число
            )
        )
        return user_task.status if user_task else None


async def get_current_task(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if not user:
            return None

        user_task = await session.scalar(
            select(UserTask).where(UserTask.user_id == user.id)
        )
        return user_task


# ДОМАШКА


async def get_hw():
    async with async_session() as session:
        return await session.scalars(select(Task))


async def get_hw_by_id(task_id):
    async with async_session() as session:
        # Преобразуем task_id в число
        task_id_int = int(task_id) if isinstance(task_id, str) else task_id
        return await session.scalar(select(Task).where(Task.id == task_id_int))


async def approve_user_hw(tg_id, task_id, points):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if user:
            old_points = user.points
            user.points += points
            user.completed_hw += 1

            # Преобразуем task_id в число
            task_id_int = int(task_id)
            userTask = await session.scalar(
                select(UserTask).where(
                    UserTask.user_id == user.id,
                    UserTask.task_id == task_id_int  # Используем число
                )
            )
            if userTask:
                userTask.status = 'approved ✅'

            await session.commit()

            # ОБНОВЛЯЕМ УРОВЕНЬ ПОЛЬЗОВАТЕЛЯ
            level_info = await update_user_level(tg_id)

            # Обновляем рейтинг если баллы изменились
            if old_points != user.points:
                await update_user_ratings()

            return level_info  # Возвращаем информацию об уровне
        return False


async def decline_user_hw(tg_id, task_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if user:
            user.expired_hw += 1
            
            # Преобразуем task_id в число
            task_id_int = int(task_id) if isinstance(task_id, str) else task_id
            userTask = await session.scalar(
                select(UserTask).where(
                    UserTask.user_id == user.id,
                    UserTask.task_id == task_id_int  # Используем число
                )
            )
            if userTask:
                userTask.status = 'declined ❌'
                await session.commit()
                return True  # Успешно отклонено
        return False  # Пользователь или задача не найдены


async def danger_user_hw(tg_id, task_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if user:
            # Преобразуем task_id в число
            task_id_int = int(task_id) if isinstance(task_id, str) else task_id
            userTask = await session.scalar(
                select(UserTask).where(
                    UserTask.user_id == user.id,
                    UserTask.task_id == task_id_int  # Используем число
                )
            )
            if userTask:
                userTask.status = 'not started'
                await session.commit()
                return True  # Успешно отклонено
        return False  # Пользователь или задача не найдены



# РЕЙТИНГ

async def get_users_with_rating():
    async with async_session() as session:
        users = await session.scalars(
            select(User).order_by(desc(User.points))
        )
        users_list = list(users)

        for index, user in enumerate(users_list, 1):
            user.rating = index
            user._rating = index

        return users_list


async def update_user_ratings():
    async with async_session() as session:
        try:
            users = await session.scalars(
                select(User).order_by(desc(User.points))
            )
            users_list = list(users)

            for index, user in enumerate(users_list, 1):
                user.rating = index

            await session.commit()

        except Exception as e:
            print(f"Ошибка при обновлении рейтинга: {e}")


async def update_single_user_rating(user_id):
    async with async_session() as session:
        users = await session.scalars(
            select(User).order_by(desc(User.points))
        )
        users_list = list(users)

        for index, user in enumerate(users_list, 1):
            user.rating = index

        await session.commit()
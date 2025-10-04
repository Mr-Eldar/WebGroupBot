from aiogram.fsm.state import State, StatesGroup


class Reg(StatesGroup):
    sn = State()


class EditUser(StatesGroup):
    new_sn = State()
    sure = State()


class CreateTask(StatesGroup):
    taskName = State()
    taskDesc = State()
    taskCompleteTime = State()
    taskCompletePoints = State()
    taskMaterials = State()
    taskFinallyAdd = State()


class SendHwForCheck(StatesGroup):
    hw_photos = State()


class CheckHw(StatesGroup):
    task_id = State()
    user_id = State()


class RejectHw(StatesGroup):
    task_id = State()
    user_id = State()


class DangerHw(StatesGroup):
    task_id = State()
    user_id = State()
    description = State()
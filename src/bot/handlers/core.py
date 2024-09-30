from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from src.database import Database
from src.bot.callbacks.menu import user_menu


async def update_user_menu(db: Database, state: FSMContext, message: Message):
    """
    Updates the user menu based on current state.
    :param message: The Message object that triggered the function.
    :param db: The Database object.
    :param state: The FSMContext object.
    :return: None.
    """
    data = await state.get_data()
    callback = data.get('callback')
    callback_data = data.get('callback_data')

    if message:
        await message.delete()
    await user_menu(callback=callback, callback_data=callback_data, db=db, state=state)

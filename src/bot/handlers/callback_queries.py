from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from src.bot.keyboards.callbacks import MenuCallback
from src.bot.handlers.core import get_menu_content
from src.database.database import Database
from src.bot.utils.states import AddPerson

router = Router()


@router.callback_query(MenuCallback.filter())
async def user_menu(callback: CallbackQuery, callback_data: MenuCallback, db: Database, state: FSMContext):
    """
    Updates the user menu.
    :param callback: 'CallbackQuery' object.
    :param callback_data: 'MenuCallback' callback factory.
    :param db: 'Database' object.
    :param state: Current state.
    :return:
    """
    current_state = await state.get_state()
    fsm_data = await state.get_data()

    if not current_state and user_menu == 'add_person':
        await state.set_state(AddPerson.vk_url)

    text, kb = await get_menu_content(
        level=callback_data.level,
        menu_name=callback_data.menu_name,
        db=db,
        current_state=current_state,
        fsm_data=fsm_data,
        committee=callback_data.committee,
        page=callback_data.page
    )

    await callback.message.edit_text(
        text=text,
        reply_markup=kb
    )
    await callback.answer()


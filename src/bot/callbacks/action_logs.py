from aiogram.types import CallbackQuery
from aiogram import Router, F

from src.database import Database
from src.config_reader import settings
from src.bot.template_engine import render_template
from src.bot.utils.points_declension import points_declension
from src.enums import ActionType
from src.api import TelegraphAPI

router = Router()


@router.callback_query(F.data == "action_logs")
async def action_logs(callback: CallbackQuery, db: Database, telegraph_api: TelegraphAPI):
    """
    This function generates and sends a telegraph page with statistics about the top person in the GUSS-top.
    :param telegraph_api: The TelegraphAPI object.
    :param callback: The CallbackQuery object.
    :param db: The Database object.
    :return: None.
    """
    audit_logs = await db.get_audit_logs(settings.ACTION_LOGS_LIMIT)
    content = render_template("action_logs.html", audit_logs=audit_logs, action_types=ActionType,
                              points_declension=points_declension)

    page_url = await telegraph_api.create_page(title='ГУСС-топ | История действий', html_content=content)

    await callback.message.answer(page_url)

from aiogram.types import CallbackQuery
from aiogram import Router, F

from src.database import Database, Person
from src.bot.utils.points_declension import points_declension
from src.bot.template_engine import render_template
from src.api import TelegraphAPI

router = Router()


def get_person_points(person: Person) -> dict[str, int]:
    """
    Calculates and returns a dictionary containing the points for each category for a given person.
    :param person: The person for whom the points are to be calculated.
    :return:
    """
    person_points = {}
    for p in person.points:
        person_points[p.category.name] = p.points_value

    return person_points


@router.callback_query(F.data == "guss_top_stats")
async def guss_top_stats(callback: CallbackQuery, db: Database, telegraph_api: TelegraphAPI):
    """
    This function generates and sends a telegraph page with statistics about the top person in the GUSS-top.
    :param telegraph_api: The TelegraphAPI object.
    :param callback: The CallbackQuery object.
    :param db: The Database object.
    :return: None.
    """
    person_points_top = await db.get_person_points_top()
    committees = await db.get_committees(join_persons=True, join_person_points=True)

    content = render_template("guss_top_stats.html", person_points_top=person_points_top,
                              committees=committees, points_declension=points_declension,
                              get_person_points=get_person_points)

    page_url = await telegraph_api.create_page(title='ГУСС-топ | Статистика', html_content=content)

    await callback.message.answer(page_url)

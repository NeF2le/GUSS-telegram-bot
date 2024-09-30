from src.api import TelegraphAPI
from src.database import Database
from src.bot.template_engine import render_template
from src.enums import DocumentType


async def get_document_process_result_url(document_type: DocumentType, document_id: int, db: Database,
                                          telegraph_api: TelegraphAPI) -> str:
    if document_type == DocumentType.PROTOCOL:
        protocol = await db.get_protocol(id=document_id, join_persons=True)
        committee = await db.get_committee(id=protocol.committee_id)
        content = render_template('protocol_process_result.html', protocol_persons=protocol.persons,
                                  committee_name=committee.name)
        page_url = await telegraph_api.create_page(
            title=f'{committee.name} | Протокол №{protocol.number} за {protocol.date}',
            html_content=content
        )
        return page_url
    elif document_type == DocumentType.EVENT_REGISTRATION_TABLE:
        table = await db.get_event_registration_table(id=document_id, join_persons=True)
        content = render_template('reg_table_process_result.html', table_persons=table.persons)
        page_url = await telegraph_api.create_page(
            title=f'{table.title}',
            html_content=content
        )
        return page_url

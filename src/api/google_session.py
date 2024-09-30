from gspread import Spreadsheet, service_account
from gspread.exceptions import APIError, SpreadsheetNotFound, GSpreadException
from builtins import PermissionError
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import re

from src.exceptions import GoogleAPIError
from src.utils.person_name import format_person_name
from datetime import datetime
from src.schemas import (GoogleDocProtocolDTO, ProtocolPersonDTO, EventRegistrationTableDTO,
                         EventRegistrationTablePersonDTO)


class GoogleAPI:
    """
    A class to interact with Google Docs and Sheets APIs.
    """

    def __init__(self, credentials_file: str):
        """
        Initializes a GoogleAPI instance with the provided service account credentials file.
        :param credentials_file: The path to the service account credentials file in JSON format.
        """
        self.credentials_file = credentials_file
        scopes_docs = ['https://www.googleapis.com/auth/documents.readonly']
        scopes_sheets = ['https://www.googleapis.com/auth/spreadsheets.readonly']
        credentials_docs = self._get_credentials(scopes_docs)
        self.service_docs = self._build_service('docs', 'v1', credentials_docs)
        self.service_sheets = service_account(filename=self.credentials_file, scopes=scopes_sheets)

    def _get_credentials(self, scopes: list[str]):
        return Credentials.from_service_account_file(self.credentials_file, scopes=scopes)

    @staticmethod
    def _build_service(service_name: str, version: str, credentials: Credentials):
        return build(service_name, version, credentials=credentials)

    @staticmethod
    def _convert_protocol_status_to_bool(protocol_status: str) -> bool:
        """
        Checks if the protocol status indicates that it has been checked.
        :param protocol_status: The status of the protocol to be checked.
        :return: True if the protocol status indicates that it has been checked, False otherwise.
        """
        protocol_status = protocol_status.strip()

        pattern = r'^проверено$'
        return re.match(pattern, protocol_status, re.IGNORECASE) is not None

    @staticmethod
    def _is_protocol_date_valid(protocol_date: str) -> bool:
        """
        Checks if the provided protocol date is in a valid 'dd.mm.yyyy' format.
        :param protocol_date: The date of the protocol to be checked.
        :return: True if the protocol date is valid, False otherwise.
        """
        try:
            datetime.strptime(protocol_date, '%d.%m.%Y')
            return True
        except ValueError:
            return False

    @staticmethod
    def _get_text_from_cell(cell) -> str:
        return cell['content'][0]['paragraph']['elements'][0]['textRun']['content'].strip()

    @staticmethod
    def _extract_persons_from_docs(persons_cell: dict) -> list[ProtocolPersonDTO]:
        """
        Extracts and formats person names from a given cell in a Google Docs document.

        The function iterates through the content of the cell, identifies bullet points,
        extracts the full name from each bullet point, formats the name into separate first and last names,
        and creates a ProtocolPersonDTO object for each valid name.

        :param persons_cell: A dictionary representing the cell in the Google Docs document.
            It contains the content of the cell, including paragraphs and bullet points.
        :return: A list of ProtocolPersonDTO objects, each representing a person's name.
            If no valid names are found, an empty list is returned.
        """
        persons = []
        for record in persons_cell['content']:
            if 'bullet' not in record['paragraph']:
                continue

            full_name = record['paragraph']['elements'][0]['textRun']['content'].strip()

            try:
                person = ProtocolPersonDTO(full_name=full_name)
                persons.append(person)
            except ValueError:
                continue

        return persons

    def get_protocols_data(self, document_id: str) -> list[GoogleDocProtocolDTO]:
        """
        Retrieves and processes protocol data from a Google Docs document.

        The function extracts protocol data from a specified Google Docs document based on certain criteria,
        such as protocol status, number, date, and persons involved. The extracted data is then formatted
        into GoogleDocProtocolDTO objects and returned as a list.

        :param document_id: The unique identifier of the Google Docs document.
        :return: A list of GoogleDocProtocolDTO objects representing the extracted protocol data.
            If no valid protocols are found, an empty list is returned.
        """
        document: dict = self.service_docs.documents().get(documentId=document_id).execute()
        content: list[dict] = document.get('body').get('content')

        protocols = []
        for block in content:
            table = block.get('table')

            # If block isn't a table object, then skip it. Because a protocol should be in table view.
            if not table:
                continue

            table_rows = table.get('tableRows')
            number = self._get_text_from_cell(table_rows[2]['tableCells'][1])
            status_text = self._get_text_from_cell(table_rows[0]['tableCells'][0])
            status = self._convert_protocol_status_to_bool(status_text)

            if not number.isdigit():
                number = None

            # If status is 'checked', then create 'GoogleDocProtocolDTO' with a protocol date and persons.
            # Else create it without a date and persons.
            if status:
                protocol_date = self._get_text_from_cell(table_rows[3]['tableCells'][1])
                if not self._is_protocol_date_valid(protocol_date):
                    protocol_date = None

                persons = self._extract_persons_from_docs(table_rows[5]['tableCells'][1])
                protocol = GoogleDocProtocolDTO(number=number, protocol_date=protocol_date, persons=persons,
                                                status=status)
            else:
                protocol = GoogleDocProtocolDTO(status=status, number=number)

            protocols.append(protocol)

        return protocols

    @staticmethod
    def _get_worksheet_names(table: Spreadsheet) -> list[str]:
        worksheets = table.worksheets()
        return [worksheet.title for worksheet in worksheets]

    def get_table_by_url(self, table_url: str) -> Spreadsheet:
        try:
            return self.service_sheets.open_by_url(table_url)
        except SpreadsheetNotFound:
            raise SpreadsheetNotFound(f"Spreadsheet not found at URL: {table_url}")
        except APIError:
            raise GoogleAPIError
        except PermissionError:
            raise PermissionError(f"Permission denied to access spreadsheet at URL: {table_url}")

    def check_table_exists(self, table_url: str) -> bool:
        try:
            _ = self.get_table_by_url(table_url)
            return True
        except (GSpreadException, PermissionError):
            return False

    def check_table_access(self, table_url: str) -> bool:
        try:
            _ = self.get_table_by_url(table_url)
            return True
        except (GSpreadException, PermissionError):
            return False

    def check_table_requirements(self, table: Spreadsheet) -> bool:
        sheet_names = self._get_worksheet_names(table)
        columns = self._get_worksheet_columns(table, sheet_names[0])

        required_columns = ['ФИО', 'Отметка']
        if not all(col in columns for col in required_columns):
            return False

        return True

    @staticmethod
    def _get_worksheet_columns(table: Spreadsheet, sheet_name: str) -> list[str]:
        worksheet = table.worksheet(sheet_name)
        columns = worksheet.get('1:1')
        return columns[0]

    def get_table_title(self, table_url: str) -> str:
        try:
            table = self.get_table_by_url(table_url)
            return table.title
        except SpreadsheetNotFound:
            raise SpreadsheetNotFound(f"table with url {table_url} not found'")

    def get_worksheet_data(self, table_url: str, sheet_name: str) -> list[dict]:
        try:
            table = self.get_table_by_url(table_url)
            worksheet = table.worksheet(sheet_name)
            rows = worksheet.get_all_records()
            return rows
        except SpreadsheetNotFound:
            raise SpreadsheetNotFound(f"table with url {table_url} not found'")

    @staticmethod
    def _extract_name_and_surname(full_name: str) -> (str, str):
        parts = format_person_name(full_name).split()
        if len(parts) >= 2:
            return parts[0], parts[1]

    @staticmethod
    def _extract_persons_from_sheet(table: Spreadsheet, sheet_name: str) -> list[EventRegistrationTablePersonDTO]:
        try:
            worksheet = table.worksheet(sheet_name)
            rows = worksheet.get_all_records()

            persons = []
            for row in rows:
                person_full_name = row.get('ФИО')
                status = row.get('Отметка')
                if person_full_name and status:
                    person = EventRegistrationTablePersonDTO(full_name=person_full_name, status=status)
                    persons.append(person)
            return persons
        except APIError:
            return []

    def get_event_registration_table_data(self, table_url: str) -> EventRegistrationTableDTO:
        try:
            table = self.get_table_by_url(table_url)
            table_title = self.get_table_title(table_url)
            sheet_names = self._get_worksheet_names(table)
            sheet_name = sheet_names[0]

            persons = self._extract_persons_from_sheet(table, sheet_name)
            event_registration_table = EventRegistrationTableDTO(title=table_title, table_url=table_url,
                                                                 persons=persons)

            return event_registration_table
        except (SpreadsheetNotFound, GoogleAPIError, PermissionError):
            raise

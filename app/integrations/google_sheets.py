import os
import gspread
from google.oauth2.service_account import Credentials
from app.config.settings import settings


class GoogleSheetsService:

    def __init__(self):

        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]

        credentials = (
            Credentials
            .from_service_account_file(
                settings.google_credentials_path,
                scopes=scopes
            )
        )

        self.client = gspread.authorize(
            credentials
        )

        self.spreadsheet = (
            self.client.open_by_key(
                settings.google_sheet_id
            )
        )

    def get_or_create_sheet(
        self,
        sheet_name: str
    ):

        try:

            return self.spreadsheet.worksheet(
                sheet_name
            )

        except Exception:

            return (
                self.spreadsheet
                .add_worksheet(
                    title=sheet_name,
                    rows=1000,
                    cols=30
                )
            )

    def replace_sheet_data(
        self,
        sheet_name: str,
        rows: list[list]
    ):

        worksheet = self.get_or_create_sheet(
            sheet_name
        )

        worksheet.clear()

        if rows:

            worksheet.update(
                rows
            )

    def format_sheet(
        self,
        sheet_name: str
    ):

        worksheet = self.get_or_create_sheet(
            sheet_name
        )

        self.spreadsheet.batch_update(
            {
                "requests": [
                    {
                        "updateSheetProperties": {
                            "properties": {
                                "sheetId": worksheet.id,
                                "gridProperties": {
                                    "frozenRowCount": 1
                                }
                            },
                            "fields": "gridProperties.frozenRowCount"
                        }
                    }
                ]
            }
        )
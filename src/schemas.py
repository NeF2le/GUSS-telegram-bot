import re

from pydantic import BaseModel, ConfigDict, Field, field_validator
from datetime import datetime, date
from typing import Any

from src.database.models import Person


class CategoryWithPointsDTO(BaseModel):
    category: str
    points_value: int


class CommitteeDTO(BaseModel):
    name: str


class PersonDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    first_name: str
    last_name: str
    vk_id: int
    committees: list[CommitteeDTO]
    points: list[CategoryWithPointsDTO]

    @classmethod
    def from_orm(cls, person: Person):
        points = [
            CategoryWithPointsDTO(
                category=point.category.name,
                points_value=point.points_value
            )
            for point in person.points
        ]
        return cls(
            first_name=person.first_name,
            last_name=person.last_name,
            vk_id=person.vk_id,
            committees=[CommitteeDTO(name=committee.name) for committee in person.committees],
            points=points
        )


class AuditLogDTO(BaseModel):
    action_type: str
    table_name: str
    old_data: dict[str, Any]
    new_data: dict[str, Any]
    changed_at: datetime
    changed_by: str


class ProtocolPersonDTO(BaseModel):
    full_name: str = Field(frozen=True)

    @staticmethod
    def _format_name(name: str) -> str:
        name_parts = name.split()
        formatted_parts = [part.capitalize().replace("ё", "е").replace('Ё', 'Е') for part in name_parts]
        return ' '.join(formatted_parts)

    @field_validator("full_name")
    @classmethod
    def check_valid_name(cls, name: str) -> str:
        name = cls._format_name(name)
        if not re.match(r'^[А-Яа-яЁё\s]+$', name):
            raise ValueError("The name can only consist of Cyrillic letters")
        if len(name.split()) != 2:
            raise ValueError("The name can't be that short or long")
        return name


class EventRegistrationTablePersonDTO(BaseModel):
    full_name: str = Field(frozen=True)
    status: bool

    @staticmethod
    def _format_name(name: str) -> str:
        name_parts = name.split()
        formatted_parts = [part.capitalize().replace("ё", "е").replace('Ё', 'Е') for part in name_parts]
        return ' '.join(formatted_parts)

    @field_validator('full_name')
    @classmethod
    def check_valid_full_name(cls, name: str) -> str:
        name = cls._format_name(name)
        parts = name.split()
        if len(parts) == 3:
            return f'{parts[0]} {parts[1]}'
        elif len(parts) == 2:
            return name
        else:
            raise ValueError("The name can't be that short or long")

    @field_validator('status', mode='before')
    @classmethod
    def check_valid_status(cls, status: str) -> bool:
        if status == 'TRUE':
            return True
        else:
            return False


class GoogleDocProtocolDTO(BaseModel):
    status: bool
    number: int | None = Field(gt=0, default=None)
    protocol_date: date | None = None
    persons: list[ProtocolPersonDTO] | None = None

    @field_validator("protocol_date", mode='before')
    @classmethod
    def check_valid_protocol_date(cls, protocol_date: str | None = None) -> date | None:
        if protocol_date is None:
            return None
        try:
            protocol_date = datetime.strptime(protocol_date, '%d.%m.%Y').date()
            return protocol_date
        except ValueError or TypeError:
            return None

    def is_valid(self):
        return self.number and self.status and self.protocol_date and self.persons


class EventRegistrationTableDTO(BaseModel):
    title: str
    table_url: str
    persons: list[EventRegistrationTablePersonDTO] | None = None

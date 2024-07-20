from pydantic import BaseModel
from datetime import datetime
from typing import Any


class PersonDTO(BaseModel):
    first_name: str
    last_name: str
    vk_id: int
    committees: list["CommitteeDTO"]


# class PersonWithPointsInCategoryDTO(PersonDTO):
#     category: "CategoryDTO"
#     points_value: int

class PersonWithPointsInCategoryDTO(BaseModel):
    person: "PersonDTO"
    category: "CategoryDTO"
    points_value: int


class PersonWithPointsDTO(PersonDTO):
    points: list["CategoryWithPointsDTO"]


class CategoryDTO(BaseModel):
    name: str


class CategoryWithPointsDTO(BaseModel):
    category: "CategoryDTO"
    points_value: int


class CategoriesWithPointsDTO(BaseModel):
    points: list["CategoryWithPointsDTO"]


class CommitteeDTO(BaseModel):
    name: str


class ActivityDTO(BaseModel):
    name: str


class PostDTO(BaseModel):
    url: str


class VkActivityDTO(BaseModel):
    person: "PersonDTO"
    activity: "ActivityDTO"
    post: "PostDTO"


class AuditLogDTO(BaseModel):
    action_type: str
    table_name: str
    old_data: dict[str, Any]
    new_data: dict[str, Any]
    # changed_by: str
    # changed_at: datetime

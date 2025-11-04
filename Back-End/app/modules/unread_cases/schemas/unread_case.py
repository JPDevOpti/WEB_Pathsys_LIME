"""Pydantic schemas for unread cases module."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, validator, ConfigDict


def to_camel(string: str) -> str:
    parts = string.split("_")
    return parts[0] + "".join(word.capitalize() for word in parts[1:])


class CamelModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )


class TestItemBase(CamelModel):
    code: str = Field(..., min_length=1, max_length=100)
    quantity: int = Field(..., gt=0)
    name: Optional[str] = Field(None, max_length=255)


class TestItem(TestItemBase):
    pass


class TestGroupBase(CamelModel):
    type: str = Field(..., pattern=r"^(LOW_COMPLEXITY_IHQ|HIGH_COMPLEXITY_IHQ|SPECIAL_IHQ|HISTOCHEMISTRY)$")
    tests: List[TestItem] = Field(default_factory=list)


class TestGroup(TestGroupBase):
    pass


class UnreadCaseBase(CamelModel):
    case_code: Optional[str] = Field(None, min_length=1, max_length=50)
    is_special_case: bool = Field(default=False)

    # Patient information (optional for special cases)
    document_type: Optional[str] = Field(None, max_length=10)
    patient_document: Optional[str] = Field(None, max_length=50)
    first_name: Optional[str] = Field(None, max_length=100)
    second_name: Optional[str] = Field(None, max_length=100)
    first_last_name: Optional[str] = Field(None, max_length=100)
    second_last_name: Optional[str] = Field(None, max_length=100)
    patient_name: Optional[str] = Field(None, max_length=200)

    # Entity information
    entity_code: Optional[str] = Field(None, max_length=50)
    entity_name: Optional[str] = Field(None, max_length=255)
    institution: Optional[str] = Field(None, max_length=255)

    notes: Optional[str] = Field(None, max_length=1000)

    # Tests
    test_groups: List[TestGroup] = Field(default_factory=list)

    # Legacy fields for backward compatibility
    low_complexity_ihq: Optional[str] = None
    low_complexity_plates: Optional[int] = None
    high_complexity_ihq: Optional[str] = None
    high_complexity_plates: Optional[int] = None
    special_ihq: Optional[str] = None
    special_plates: Optional[int] = None
    histochemistry: Optional[str] = None
    histochemistry_plates: Optional[int] = None

    # Logistics
    number_of_plates: int = Field(default=0, ge=0)
    delivered_to: Optional[str] = Field(None, max_length=255)
    delivery_date: Optional[str] = Field(None, max_length=50)
    entry_date: Optional[str] = Field(None, max_length=50)
    received_by: Optional[str] = Field(None, max_length=255)
    status: str = Field(default="En proceso", max_length=100)

    elaborated_by: Optional[str] = Field(None, max_length=255)
    receipt: Optional[str] = Field(None, max_length=255)

    @validator("case_code", pre=True, always=True)
    def normalize_case_code(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        return value.strip().upper()

    @validator("document_type", pre=True, always=True)
    def normalize_document_type(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        return value.strip().upper()


class UnreadCaseCreate(UnreadCaseBase):
    pass


class UnreadCaseUpdate(CamelModel):
    is_special_case: Optional[bool]
    document_type: Optional[str]
    patient_document: Optional[str]
    first_name: Optional[str]
    second_name: Optional[str]
    first_last_name: Optional[str]
    second_last_name: Optional[str]
    patient_name: Optional[str]
    entity_code: Optional[str]
    entity_name: Optional[str]
    institution: Optional[str]
    notes: Optional[str]
    test_groups: Optional[List[TestGroup]]
    low_complexity_ihq: Optional[str]
    low_complexity_plates: Optional[int]
    high_complexity_ihq: Optional[str]
    high_complexity_plates: Optional[int]
    special_ihq: Optional[str]
    special_plates: Optional[int]
    histochemistry: Optional[str]
    histochemistry_plates: Optional[int]
    number_of_plates: Optional[int]
    delivered_to: Optional[str]
    delivery_date: Optional[str]
    entry_date: Optional[str]
    received_by: Optional[str]
    status: Optional[str]
    elaborated_by: Optional[str]
    receipt: Optional[str]


class UnreadCaseResponse(UnreadCaseBase):
    id: str = Field(...)
    created_at: Optional[datetime]
    updated_at: Optional[datetime]


class UnreadCaseListResponse(CamelModel):
    items: List[UnreadCaseResponse]
    total: int
    page: int
    limit: int


class UnreadCaseFilter(CamelModel):
    search_query: Optional[str] = None
    selected_institution: Optional[str] = None
    selected_test_type: Optional[str] = None
    selected_status: Optional[str] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    sort_key: Optional[str] = None
    sort_order: Optional[str] = None
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=25, ge=1, le=200)


class BulkMarkDeliveredRequest(CamelModel):
    case_codes: List[str]
    delivered_to: str
    delivery_date: Optional[str] = None


class BulkMarkDeliveredResponse(CamelModel):
    updated: List[UnreadCaseResponse]


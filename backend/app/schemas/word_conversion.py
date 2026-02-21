"""
Pydantic schemas for Word-to-HTML conversion pipeline.
"""

from pydantic import BaseModel


class ValidationItem(BaseModel):
    rule: str
    passed: bool
    detail: str | None = None


class ConversionResult(BaseModel):
    html: str
    warnings: list[str]
    validation: list[ValidationItem]
    merge_fields_detected: list[str]
    is_valid: bool

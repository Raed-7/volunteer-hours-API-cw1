from pydantic import AliasChoices, BaseModel, EmailStr, Field


class VolunteerBase(BaseModel):
    volunteer_no: str | None = Field(
        default=None,
        max_length=100,
        validation_alias=AliasChoices("volunteer_no", "volunteer_id", "volunteer_number", "id"),
        description="Optional volunteer number or external identifier.",
    )
    name: str = Field(
        min_length=2,
        max_length=255,
        validation_alias=AliasChoices("name", "full_name", "volunteer_name"),
        description="Volunteer name (accepts input aliases such as full_name or volunteer_name).",
    )
    email: EmailStr | None = None
    phone: str | None = Field(
        default=None,
        max_length=50,
        validation_alias=AliasChoices("phone", "mobile", "phone_number", "contact"),
    )


class VolunteerCreate(VolunteerBase):
    pass


class VolunteerUpdate(BaseModel):
    volunteer_no: str | None = Field(
        default=None,
        max_length=100,
        validation_alias=AliasChoices("volunteer_no", "volunteer_id", "volunteer_number", "id"),
    )
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=255,
        validation_alias=AliasChoices("name", "full_name", "volunteer_name"),
    )
    email: EmailStr | None = None
    phone: str | None = Field(
        default=None,
        max_length=50,
        validation_alias=AliasChoices("phone", "mobile", "phone_number", "contact"),
    )


class VolunteerRead(VolunteerBase):
    id: int

    model_config = {"from_attributes": True}

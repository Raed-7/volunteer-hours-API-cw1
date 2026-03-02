from pydantic import AliasChoices, BaseModel, EmailStr, Field


class VolunteerBase(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=255,
        validation_alias=AliasChoices("name", "full_name"),
        description="Volunteer name (accepts input alias: full_name).",
    )
    email: EmailStr
    phone: str | None = Field(default=None, max_length=50)


class VolunteerCreate(VolunteerBase):
    pass


class VolunteerUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=255, validation_alias=AliasChoices("name", "full_name"))
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=50)


class VolunteerRead(VolunteerBase):
    id: int

    model_config = {"from_attributes": True}

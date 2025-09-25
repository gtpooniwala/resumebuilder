from pydantic import BaseModel

class Resume(BaseModel):
    name: str
    email: str
    phone: str
    summary: str
    experience: list[dict]
    education: list[dict]
    skills: list[str]

# TODO: Implement user-specific resumes when user management is added.
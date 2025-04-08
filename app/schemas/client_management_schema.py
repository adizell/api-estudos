from pydantic import BaseModel


class ClientCreateResponse(BaseModel):
    client_id: str
    client_secret: str

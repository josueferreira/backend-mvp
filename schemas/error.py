from pydantic import BaseModel


class ErrorSchema(BaseModel):
    """ Define como uma mensagem de erro que será apresentada
    """
    mesage: str

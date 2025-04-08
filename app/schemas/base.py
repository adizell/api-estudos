from pydantic import BaseModel


class CustomBaseModel(BaseModel):
    def dict(self, *args, **kwargs):
        # Chama a função 'dict' da classe pai (BaseModel) para obter o dicionário padrão dos atributos
        d = super().dict(*args, **kwargs)
        # Filtra o dicionário para remover itens onde o valor é None
        d = {k: v for k, v in d.items() if v is not None}
        # Retorna o dicionário filtrado
        return d

from sqlalchemy import Column, Integer, String, Text, Float, DateTime
from datetime import datetime
from typing import Union
from  model import Base

class Viagem(Base):
    __tablename__ = 'viagem'

    id = Column("pk_viagem", Integer, primary_key=True)
    destino = Column(String(4000))
    detalhes = Column(String(4000))
    rating = Column(Float)
    fotos = Column(String(4000))  # Lista das URLs dos arquivos
    data_insercao = Column(DateTime, default=datetime.now())

    def __init__(self, destino:str, detalhes:str, rating:float, fotos:str,
                 data_insercao:Union[DateTime, None] = None):
        """
        Cria uma Viagem

        Arguments:
            destino: nome da viagem.
            detalhes: detalhes da viagem.
            rating: nota avaliada
            fotos: caminho ou URL de acesso as imagens da viagem
            data_insercao: data de quando a viagem foi inserida à base
        """
        self.destino = destino
        self.detalhes = detalhes
        self.rating = rating
        self.fotos = fotos
        if data_insercao:
            self.data_insercao = data_insercao


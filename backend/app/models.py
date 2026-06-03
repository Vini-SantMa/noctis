from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float, Text
from sqlalchemy.orm import relationship, validates
from abc import ABC, abstractmethod
from .database import Base
import requests




class IExportavel: #interface  para as classes user, usergame e lista
    def exportar_dados(self):
        """Método que toda classe que assinar este contrato deve ter"""
        raise NotImplementedError("A classe precisa implementar o exportar_dados()")

def processar_exportacao(entidade: IExportavel):
    return entidade.exportar_dados()


# ABSTRACT FACTORY IMPLEMENTACAO
#

class IGameDataBuscador(ABC):
    """Contrato para processo de buscar as info basicas dos jogos na API externa"""
    @abstractmethod
    def buscar_detalhes_jogo(self, game_id: str):
        pass

class IPlayerStatusBuscador(ABC):
    """Contrato para buscar as estatisticas do jogador na APi ecterna"""

    @abstractmethod
    def buscar_stats(self, player_id: str):
        pass

#
# ABSTRACT FACTORY
#

class IPlataformaFactory(ABC):
    """Contrato da fábrica -> definir o que todas as plataformas devem fornecer para nosso sistema"""
    @abstractmethod
    def criar_buscador_jogos(self) ->IGameDataBuscador:
        pass
    @abstractmethod
    def criar_buscador_status(self) -> IPlayerStatusBuscador:
        pass
    

#Modelo da Steam,
class SteamGameBuscador(IGameDataBuscador):
    #Buscar os dados dentro da steam
    def buscar_detalhes_jogo(self, game_id: str):
        #Espaço para implementar a api da steam

        return{
             "plataforma": "steam", "titulo": f"Jogo Steam {game_id}", "capa": "https://cdn.akamai.steamstatic.com/sample.jpg"}
        
class SteamStatusBuscador(IPlayerStatusBuscador):
    # Implementacao para buscar os status dos jogadores la na steam
    def buscar_status_jogador(self, player_id: str):
        #Requisicao para api da steam
        return { "horas_jogadas": 120.5, "conquistas": "45/90"}

class SteamFactory(IPlataformaFactory):
    def criar_buscador_jogos(self) -> IGameDataBuscador:
        return SteamGameBuscador()
    def criar_buscador_status(self) -> IPlayerStatusBuscador:
        
        return SteamStatusBuscador()

# ==========================================
# MODELOS DO BANCO DE DADOS
# ==========================================

class User(Base, IExportavel):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    avatar = Column(Text, nullable=True)

    # IMPLEMENTAÇÃO DO POLIMORFISMO
    def exportar_dados(self):
        return {"tipo": "Jogador", "nome": self.username, "contato": self.email}

class RecoveryCode(Base):
    __tablename__ = "recovery_codes"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True)
    code = Column(String)
    expires_at = Column(String)

class UserGame(Base, IExportavel):
    __tablename__ = "user_games"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    game_id = Column(String, nullable=False) 
    titulo = Column(String, nullable=True) 
    capa = Column(String, nullable=True)
    dados_jogo = Column(Text, nullable=True)
    status_principal = Column(String, default="Quero Jogar") 
    favorito = Column(Boolean, default=False)
    
    # ENCAPSULAMENTO: Atributo "privado"
    _horas_jogadas = Column("horas_jogadas", Float, default=0.0)

    nota_geral = Column(Float, nullable=True) 
    comentario = Column(String, nullable=True)
    criterios = Column(String, nullable=True) 
    conquistas = Column(String, nullable=True) 
    conquistas_personalizadas = Column(String, nullable=True)

    user = relationship("User", backref="meus_jogos")

    # ENCAPSULAMENTO: Métodos Get, Set e Validação Interceptadora
    @validates('_horas_jogadas')
    def validate_horas(self, key, value):
        if value < 0:
            raise ValueError("As horas jogadas não podem ser negativas!")
        return value

    @property
    def horas_jogadas(self):
        return self._horas_jogadas

    @horas_jogadas.setter
    def horas_jogadas(self, value):
        self._horas_jogadas = value

    # IMPLEMENTAÇÃO DO POLIMORFISMO
    def exportar_dados(self):
        return {"tipo": "Jogo na Biblioteca", "titulo": self.titulo, "horas": self.horas_jogadas}

class Lista(Base, IExportavel):
    __tablename__ = "listas"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id")) 
    list_id = Column(String, unique=True, index=True)
    nome = Column(String)
    descricao = Column(String, nullable=True)
    jogos = Column(Text, default="[]") 
    criado_em = Column(Float)

    # IMPLEMENTAÇÃO DO POLIMORFISMO
    def exportar_dados(self):
        return {"tipo": "Lista Customizada", "nome_lista": self.nome, "jogos_contidos": self.jogos}

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float, Text
from sqlalchemy.orm import relationship, validates
from abc import ABC, abstractmethod
from .database import Base
import requests
import json



class IExportavel: #interface  para as classes user, usergame e lista
    def exportar_dados(self):
        """Método que toda classe que assinar este contrato deve ter"""
        raise NotImplementedError("A classe precisa implementar o exportar_dados()")

def processar_exportacao(entidade: IExportavel):
    return entidade.exportar_dados()


# ABSTRACT FACTORY IMPLEMENTACAO


class IGameDataBuscador(ABC):
    """Contrato para processo de buscar as info basicas dos jogos na API externa"""
    @abstractmethod
    def buscar_detalhes_jogo(self, game_id: str):
        pass

class IPlayerStatusBuscador(ABC):
    """Contrato para buscar as estatisticas do jogador na APi ecterna"""

    @abstractmethod
    def buscar_status_jogador(self, player_id: str, game_id: str):
        pass

#
# ABSTRACT FACTORYco
#

class IPlataformaFactory(ABC):
    """Contrato da fábrica -> definir o que todas as plataformas devem fornecer para nosso sistema"""
    @abstractmethod
    def criar_buscador_jogos(self) ->IGameDataBuscador:
        pass
    @abstractmethod
    def criar_buscador_status(self) -> IPlayerStatusBuscador:
        pass
    

#Modelo da Steam

# IMPLEMENTACAO DA WEBAPI PARA TESTAR STEAM

class SteamGameBuscador(IGameDataBuscador):
    #Buscar os dados dentro da steam
    
    
    def buscar_detalhes_jogo(self, game_id: str):
        game_id_str = str(game_id)
        # Pedimos em português se houver
        url = f"https://store.steampowered.com/api/appdetails?appids={game_id_str}&l=brazilian"
        try:
            resposta = requests.get(url).json()
            
            if resposta and resposta.get(game_id_str, {}).get("success"):
                dados = resposta[game_id_str]["data"]
                
                # Pega os géneros e formata numa lista simples
                generos_raw = dados.get("genres", [])
                generos = [g.get("description") for g in generos_raw] if generos_raw else ["Desconhecido"]
                
                desenvolvedores = dados.get("developers", ["Desconhecida"])
                dev_principal = desenvolvedores[0] if desenvolvedores else "Desconhecida"
                
                desc_curta = dados.get("short_description", "").strip()
                desc_longa = dados.get("about_the_game", "").strip()
                descricao_final = desc_curta if desc_curta else desc_longa
                if not descricao_final:
                    descricao_final = "A Steam não disponibilizou uma sinopse para este game"
                    
                return {
                    "plataforma": "Steam",
                    "titulo": dados.get("name"),
                    "capa": f"https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/{game_id_str}/library_600x900.jpg",
                    #"capa": dados.get("header_image", "Sem capa"),
                    "desenvolvedora": dev_principal,
                    "descricao": descricao_final,
                    #"descricao": dados.get("short_description", "Sem descrição disponível."),
                    "lancamento": dados.get("release_date", {}).get("date", "Desconhecido"),
                    "generos": generos
                }
                
            return {"erro": f"Falha na Steam. Resposta oficial: {resposta}"}
            
        except Exception as e:
            return {"erro": f"Erro de conexão com a Valve: {str(e)}"}
    """
    def buscar_detalhes_jogo(self, game_id: str):
        #Espaço para implementar a api da steam
        game_id_str = str(game_id)
        url = f"https://store.steampowered.com/api/appdetails?appids={game_id_str}"
        try:
            resposta = requests.get(url).json()
            
            # Verifica se a Steam retornou sucesso
            if resposta and resposta.get(game_id_str, {}).get("success"):
                dados = resposta[game_id_str]["data"]
                return {
                    "plataforma": "Steam",
                    "titulo": dados.get("name"),
                    "capa": dados.get("header_image", "Sem capa"),
                    "desenvolvedora": dados.get("developers", ["Desconhecida"])[0]
                }
                
            # O RAIO-X: Se falhar, devolvemos a resposta oficial da Steam no Swagger!
            return {"erro": f"Falha na Steam. Resposta oficial: {resposta}"}
            
        except Exception as e:
            return {"erro": f"Erro de conexão com a Valve: {str(e)}"}"""
            
            
        
    """ game_id_str = str(game_id)
        url = f"https://store.steampowered.com/api/appdetails?appids={game_id}"
        resposta = requests.get(url).json()
        
        #Identificar sucesso na requisicao da api
        if resposta.get(game_id, {}).get("sucess"):
            dados = resposta[game_id]["data"]
            return{
                "plataforma": "Steam",
                "titulo": dados.get("name"),
                "capa": dados.get("header_image"),
                "desenvolvedora": dados.get("developers", ["Desconhecida"])[0]
                
            }
        return{ "erro": "jogo não encontrado"}"""

      #  return{
           #  "plataforma": "steam", "titulo": f"Jogo Steam {game_id}", "capa": "https://cdn.akamai.steamstatic.com/sample.jpg"}
        
class SteamStatusBuscador(IPlayerStatusBuscador):
    # Implementacao para buscar os status dos jogadores la na steam
    def buscar_status_jogador(self, player_id: str, game_id: str):
        #Requisicao para api da steam
        STEAM_API = "50A713B67631D0979739B7F996B831B6"
       #return { "horas_jogadas": 120.5, "conquistas": "45/90"}
        url = f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={STEAM_API}&steamid={player_id}&format=json"
        
        try:
           resposta = requests.get(url).json()
           jogos = resposta.get("response",{}).get("games", [])
           
           # O FILTRO: Procura o jogo exato na biblioteca da Steam
           horas_do_jogo = 0.0
           for jogo in jogos:
               if str(jogo.get("appid")) == str(game_id):
                   horas_do_jogo = jogo.get("playtime_forever", 0) / 60.0
                   break
           
           total_jogos = len(jogos)
           horas_totais = sum(jogo.get("playtime_forever", 0) for jogo in jogos) / 60
           
           return {
               "total_jogos_na_conta": total_jogos,
               "horas_totais_jogadas": round(horas_totais, 1),
               "horas_do_jogo": round(horas_do_jogo, 1) 
           }
        except Exception:
            return {"erro": "falha na busca das informacoes da conta"}
        """
        try:
           resposta = requests.get(url).json()
           jogos = resposta.get("response",{}).get("games", [])
           total_jogos = len(jogos)
           horas_totais = sum(jogo.get("playtime_forever", 0) for jogo in jogos) / 60
           
           return {
               "total_jogos_na_conta": total_jogos,
               "horas_totais_jogadas": round(horas_totais, 1)
           }
        except Exception:
            return {
                "erro": "falha na busca das informacoes da conta. Perfil privado ou Id invalido"
            }"""

class SteamFactory(IPlataformaFactory):
    def criar_buscador_jogos(self) -> IGameDataBuscador:
        return SteamGameBuscador()
    def criar_buscador_status(self) -> IPlayerStatusBuscador:
        
        return SteamStatusBuscador()

# ---------- Padrão ADAPTER ------------------
class SteamAdapter:
    """
    Adapter para padronizar a resposta da Steam e deixá-la 
    pronta para ser salva no banco de dados do NOCTIS.
    """
    def __init__(self, buscador_jogo: IGameDataBuscador, buscador_status: IPlayerStatusBuscador, api_key: str):
        self.buscador_jogo = buscador_jogo
        self.buscador_status = buscador_status
        self.api_key = api_key

    def formatar_para_banco(self, game_id: str, player_id: str) -> dict:
        # > Puxa os dados base do jogo
        dados_base = self.buscador_jogo.buscar_detalhes_jogo(game_id)
        
        # > Puxa as horas jogadas da conta
        # (Para ficar perfeito no futuro, o ideal seria buscar as horas específicas DESSA ID)
        dados_status = self.buscador_status.buscar_status_jogador(player_id, game_id)
        horas_registradas = dados_status.get("horas_do_jogo", 0.0)
        
        # > Procura conquistas da steam
        
        texto_conquistas = "{}" 
        url_conquistas = f"https://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v0001/?appid={game_id}&key={self.api_key}&steamid={player_id}"
        
        try:
            resposta_achievements = requests.get(url_conquistas).json()
            player_stats = resposta_achievements.get("playerstats", {})
            
            if player_stats.get("success"):
                lista_conquistas = player_stats.get("achievements", [])
                
                # dicionario para atender ao front ja implementado
                dict_conquistas = {}
                for c in lista_conquistas:
                    if c.get("achieved") == 1:
                        # pega o nome do troféu da Steam e marca como True
                        nome_conquista = c.get("apiname", f"Troféu_Desconhecido")
                        dict_conquistas[nome_conquista] = True
                        
                # converte pra um json para o banco
                texto_conquistas = json.dumps(dict_conquistas)
        except Exception:
            pass
        
        status_calculado = "Quero Jogar"
        if horas_registradas > 0:
            status_calculado = "Jogando"

        # 4. O RETORNO UNIFICADO
        
        dados_jogo_fake_rawg = {
            "id": f"steam-{game_id}",
            "name": dados_base.get("titulo", "Jogo Desconhecido"),
            "title": dados_base.get("titulo", "Jogo Desconhecido"),
            "cover": dados_base.get("capa", ""),
            "background_image": dados_base.get("capa", ""),
            "description": dados_base.get("descricao", ""),
            "description_raw": dados_base.get("descricao", ""),
            "releaseYear": dados_base.get("lancamento", ""),
            "developer": dados_base.get("desenvolvedora", ""),
            "genres": dados_base.get("generos", [])
        }
        
        return {
            "game_id": f"steam-{game_id}",
            "titulo": dados_base.get("titulo", "Jogo Desconhecido"),
            "capa": dados_base.get("capa", ""),
            "dados_jogo": json.dumps(dados_jogo_fake_rawg),
           
            "horas_jogadas": horas_registradas,
            "conquistas": texto_conquistas, # Agora envia um JSON válido!
            "status_principal": status_calculado, 
            "favorito": False
        }
        """"
        texto_conquistas = "0/0"
        url_conquistas = f"https://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v0001/?appid={game_id}&key={self.api_key}&steamid={player_id}"
        
        try:
            resposta_achievements = requests.get(url_conquistas).json()
            player_stats = resposta_achievements.get("playerstats", {})
            
            if player_stats.get("success"):
                lista_conquistas = player_stats.get("achievements", [])
                total = len(lista_conquistas)
                completas = sum(1 for c in lista_conquistas if c.get("achieved") == 1)
                texto_conquistas = f"{completas}/{total}"
            else:
                erro_msg = player_stats.get("error", "Bloqueado por Privacidade")
                texto_conquistas = f"Erro Steam: {erro_msg}"
        except Exception as e:
            texto_conquistas = f"Erro Interno: {str(e)}"
            # Se o perfil for privado ou o jogo não tiver conquistas
            pass

        # > retorno dos dados já de forma organizada, para encaixar no banco
        return {
            "game_id": str(game_id),
            "titulo": dados_base.get("titulo", "Jogo Desconhecido"),
            "capa": dados_base.get("capa", ""),
            "horas_jogadas": dados_status.get("horas_totais_jogadas", 0.0),
            "conquistas": texto_conquistas,
            "status_principal": "Quero Jogar", # Status padrão
            "favorito": False
        } """
        
#-----



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
    
    horas_jogadas = Column(Float, default=0.0)

    nota_geral = Column(Float, nullable=True) 
    comentario = Column(String, nullable=True)
    criterios = Column(String, nullable=True) 
    conquistas = Column(String, nullable=True) 
    conquistas_personalizadas = Column(String, nullable=True)

    user = relationship("User", backref="meus_jogos")

    # Validação inteligente direto na coluna
    @validates('horas_jogadas')
    def validate_horas(self, key, value):
        if value < 0:
            raise ValueError("As horas jogadas não podem ser negativas!")
        return value
    """__tablename__ = "user_games"

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

    # @property
    def horas_jogadas(self):
        return self._horas_jogadas

    @horas_jogadas.setter
    def horas_jogadas(self, value):
        self._horas_jogadas = value"""

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

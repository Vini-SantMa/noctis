from abc import ABC, abstractmethod

# 1. A INTERFACE DO ESTADO
class EstadoJogo(ABC):
    @abstractmethod
    def avaliar(self, nota: float) -> dict:
        """Regra: Define o que acontece ao tentar avaliar o jogo neste estado"""
        pass


class QueroJogarState(EstadoJogo):
    def avaliar(self, nota: float) -> dict:
        #  Bloqueia a avaliação se o jogo não foi jogado
        return {"sucesso": False, "erro": "Não é permitido avaliar um jogo que está na lista de 'Quero Jogar'."}

class JogandoState(EstadoJogo):
    def avaliar(self, nota: float) -> dict:
        return {"sucesso": True, "mensagem": "Avaliação parcial em progresso registrada."}

class JogadoState(EstadoJogo):
    def avaliar(self, nota: float) -> dict:
        return {"sucesso": True, "mensagem": "Avaliação final registrada com sucesso!"}

class PlatinadoState(EstadoJogo):
    def avaliar(self, nota: float) -> dict:
        return {"sucesso": True, "mensagem": "Avaliação de Platina registrada com louvor!"}

class AbandonadoState(EstadoJogo):
    def avaliar(self, nota: float) -> dict:
        return {"sucesso": True, "mensagem": "Avaliação de jogo abandonado registrada."}

# 3. O CONTEXTO (O Gerenciador que a nossa API vai chamar)
class ContextoAvaliacao:
    def __init__(self, status_str: str):
        self.estado = self._obter_estado_por_string(status_str)

    def _obter_estado_por_string(self, status_str: str) -> EstadoJogo:
        # Mapeia a string do db para a classe de estados real
        mapa_estados = {
            "Quero Jogar": QueroJogarState(),
            "Jogando": JogandoState(),
            "Jogado": JogadoState(),
            "Platinado": PlatinadoState(),
            "Abandonado": AbandonadoState()
        }
        # Vai assumir como jogado em caso de algo inesperado
        return mapa_estados.get(status_str, JogadoState())

    def tentar_avaliar(self, nota: float) -> dict:
        # Delegar para o estado current
        return self.estado.avaliar(nota)
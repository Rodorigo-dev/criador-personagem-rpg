from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from enum import Enum

class Raca(str, Enum):
    HUMANO = "Humano"
    ELFO = "Elfo"
    ANAO = "Anão"
    ORC = "Orc"
    TIEFLING = "Tiefling"
    HALFLING = "Halfling"
    GNOMO = "Gnomo"
    DRACONATO = "Draconato"
    MEIO_ELFO = "Meio-Elfo"
    MEIO_ORC = "Meio-Orc"

class Classe(str, Enum):
    BARBARO = "Bárbaro"
    BARDO = "Bardo"
    BRUXO = "Bruxo"
    CLERIGO = "Clérigo"
    DRUIDA = "Druida"
    FEITICEIRO = "Feiticeiro"
    GUERREIRO = "Guerreiro"
    LADINO = "Ladino"
    MAGO = "Mago"
    MONGE = "Monge"
    PALADINO = "Paladino"
    PATRULHEIRO = "Patrulheiro"

class Atributos(BaseModel):
    forca: int = Field(ge=8, le=15, description="Força física do personagem")
    destreza: int = Field(ge=8, le=15, description="Agilidade e reflexos")
    constituicao: int = Field(ge=8, le=15, description="Vigor e resistência")
    inteligencia: int = Field(ge=8, le=15, description="Raciocínio e conhecimento")
    sabedoria: int = Field(ge=8, le=15, description="Intuição e percepção")
    carisma: int = Field(ge=8, le=15, description="Força de personalidade")

class PersonagemDnD(BaseModel):
    nome: str = Field(description="Nome do personagem")
    sexo: str = Field(description="Sexo do personagem", default="Masculino")
    raca: Raca = Field(description="Raça do personagem")
    classe: Classe = Field(description="Classe do personagem")
    nivel: int = Field(default=1, ge=1, le=20, description="Nível do personagem")
    antecedente: str = Field(description="Antecedente do personagem")
    alinhamento: str = Field(description="Alinhamento moral e ético")
    atributos: Atributos = Field(description="Atributos base do personagem")
    historia: str = Field(description="História de origem do personagem")
    pericias: List[str] = Field(default_list=[], description="Lista de perícias")
    equipamento: List[str] = Field(default_list=[], description="Lista de equipamentos")
    caracteristicas: Dict[str, str] = Field(default_factory=dict, description="Características especiais") 
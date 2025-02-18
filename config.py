from typing import Dict

# Configuração de caminhos
KNOWLEDGE_BASE_PATH = "knowledge_base.faiss"
PDF_PATH = "player-book.pdf"

# Estrutura dos capítulos
CAPITULOS: Dict[str, Dict[str, any]] = {
    "character_creation": {"start": 11, "end": 16, "name": "Criação de Personagens"},
    "races": {"start": 17, "end": 43, "name": "Raças"},
    "classes": {"start": 45, "end": 121, "name": "Classes"},
    "personality": {"start": 123, "end": 143, "name": "Personalidades e Antecedentes"},
    "equipment": {"start": 145, "end": 163, "name": "Equipamento"},
    "customization": {"start": 165, "end": 171, "name": "Opções de Personalização"},
    "abilities": {"start": 175, "end": 181, "name": "Utilizando Habilidades"},
    "adventuring": {"start": 183, "end": 189, "name": "Aventurando-se"},
    "combat": {"start": 191, "end": 200, "name": "Combate"},
    "spellcasting": {"start": 203, "end": 207, "name": "Conjuração"},
    "spells": {"start": 209, "end": 289, "name": "Magias"}
}

# Mapeamento de palavras-chave para capítulos
KEYWORD_MAPPING = {
    "races": ['raça', 'elfo', 'anão', 'humano', 'halfling', 'draconato', 'gnomo', 'tiefling'],
    "classes": ['classe', 'bárbaro', 'bardo', 'bruxo', 'clérigo', 'druida', 'feiticeiro', 
                'guerreiro', 'ladino', 'mago', 'monge', 'paladino', 'patrulheiro'],
    "personality": ['antecedente', 'personalidade', 'inspiração', 'alinhamento'],
    "equipment": ['equipamento', 'arma', 'armadura', 'item', 'ferramenta'],
    "spells": ['magia', 'feitiço', 'conjuração', 'spell'],
    "abilities": ['habilidade', 'perícia', 'atributo'],
    "combat": ['combate', 'luta', 'ataque', 'dano']
} 
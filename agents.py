from langchain.agents import Tool, AgentExecutor, create_openai_functions_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from models import PersonagemDnD, Atributos
from typing import Dict, Any
import json
from knowledge_base import DnDKnowledgeBase


class CharacterCreationAgent:
   def __init__(self, llm: ChatOpenAI):
       self.llm = llm
       self.knowledge_base = DnDKnowledgeBase(llm)
       self.tools = self._setup_tools()
       self.agent = self._setup_agent()
  
   def _setup_tools(self) -> list[Tool]:
       return[
           Tool(
               name="get_race_info",
               func=self.get_race_info,
               description="Obtém informações sobre raças"
           ),
           Tool(
               name="get_class_info",
               func=self.get_class_info,
               description="Obtém informações sobre classes"
           ),
           Tool(
               name="get_background_info",
               func=self.get_background_info,
               description="Obtém informações sobre antecedentes"
           ),
           Tool(
               name="get_alinhamento_info",
               func=self.get_alinhamento_info,
               description="Obtém informações sobre alinhamentos"
           )
       ]
  
   def _setup_agent(self) -> AgentExecutor:
       prompt = ChatPromptTemplate.from_messages([
           ("system", """Você é um assistente especializado em criar personagens de D&D.
           Guie o usuário pelo processo de criação, oferecendo sugestões e explicações.
           Use as ferramentas disponíveis para obter informações precisas do livro."""),
           ("human", "{input}"),
           MessagesPlaceholder(variable_name="agent_scratchpad"),
       ])
      
       agent = create_openai_functions_agent(self.llm, self.tools, prompt)
       return AgentExecutor(agent=agent, tools=self.tools)


   def get_race_info(self, race: str) -> str:
       query = f"Descreva detalhadamente a raça {race} em D&D 5e"
       result = self.knowledge_base.query(query)
       return result["resposta"]
  
   def get_class_info(self, class_name: str) -> str:
       query = f"Descreva detalhadamente a classe {class_name} em D&D 5e"
       result = self.knowledge_base.query(query)
       return result["resposta"]
  
   def get_background_info(self, background: str) -> str:
       query = f"Descreva detalhadamente o antecedente {background} em D&D 5e"
       result = self.knowledge_base.query(query)
       return result["resposta"]
  
   def get_alinhamento_info(self, alignment: str) -> str:
       query = f"Descreva detalhadamente o alinhamento {alignment} em D&D 5e"
       result = self.knowledge_base.query(query)
       return result["resposta"]
  
   def create_character(self, data: Dict[str, Any]) -> PersonagemDnD:
       # Cria um personagem com os dados fornecidos
       atributos = Atributos(
           forca=data["forca"],
           destreza=data["destreza"],
           constituicao=data["constituicao"],
           inteligencia=data["inteligencia"],
           sabedoria=data["sabedoria"],
           carisma=data["carisma"]
       )
      
       personagem = PersonagemDnD(
           nome=data["nome"],
           sexo=data["sexo"],
           raca=data["raca"],
           classe=data["classe"],
           antecedente=data["antecedente"],
           alinhamento=data["alinhamento"],
           atributos=atributos,
           historia="",  # Será preenchido pelo StorytellingAgent
           pericias=[],  # Será preenchido baseado na classe e antecedente
           equipamento=[],  # Será preenchido baseado na classe
           caracteristicas={}  # Será preenchido baseado na raça e classe
       )
      
       # Usa a base de conhecimento para enriquecer o personagem
       self._add_class_features(personagem)
       self._add_race_features(personagem)
       self._add_background_features(personagem)
      
       return personagem
  
   def _add_class_features(self, character: PersonagemDnD):
       query = f"Liste as características principais e equipamento inicial da classe {character.classe}"
       result = self.knowledge_base.query(query)
       # Processa o resultado e adiciona ao personagem
       # ...


   def _add_race_features(self, character: PersonagemDnD):
       query = f"Liste os traços raciais e características da raça {character.raca}"
       result = self.knowledge_base.query(query)
       # Processa o resultado e adiciona ao personagem
       # ...


   def _add_background_features(self, character: PersonagemDnD):
       query = f"Liste as características e proficiências do antecedente {character.antecedente}"
       result = self.knowledge_base.query(query)
       # Processa o resultado e adiciona ao personagem
       # ...


class StorytellingAgent:
   def __init__(self, llm: ChatOpenAI):
       self.llm = llm
  
   def generate_story(self, character: PersonagemDnD) -> str:
       prompt = f"""
       Crie uma história de origem envolvente para este personagem de D&D:
      
       Nome: {character.nome}
       Raça: {character.raca}
       Classe: {character.classe}
       Antecedente: {character.antecedente}
      
       A história deve:
       1. Explicar como o personagem escolheu sua classe
       2. Incorporar elementos do seu antecedente
       3. Refletir seu alinhamento ({character.alinhamento})
       4. Mencionar eventos formativos
       """
      
       response = self.llm.invoke(prompt)
       return response.content


class IllustrationAgent:
   def __init__(self, llm: ChatOpenAI):
       self.llm = llm
  
   def generate_illustration_prompt(self, character: PersonagemDnD) -> str:
       prompt = f"""
       Crie um prompt detalhado para gerar uma ilustração deste personagem:
      
       Nome: {character.nome}
       Raça: {character.raca}
       Classe: {character.classe}
      
       O prompt deve:
       1. Descrever aparência física
       2. Incluir vestimentas e equipamentos típicos da classe
       3. Sugerir pose e expressão que reflitam personalidade
       4. Especificar estilo artístico apropriado
       """
      
       response = self.llm.invoke(prompt)
       return response.content
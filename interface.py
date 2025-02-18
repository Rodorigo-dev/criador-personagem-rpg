import gradio as gr
from langchain_openai import ChatOpenAI
from agents import CharacterCreationAgent, StorytellingAgent, IllustrationAgent
from models import Atributos, PersonagemDnD, Raca, Classe
from utils import validar_pontos_atributos
import json
import os
from dotenv import load_dotenv
from openai import OpenAI  # Para geração de imagens


# Carrega variáveis de ambiente
load_dotenv()


# Inicializa os agentes
llm = ChatOpenAI(
   model="gpt-4o-mini",
   temperature=0.7,
   api_key=os.getenv("OPENAI_API_KEY")
)


character_agent = CharacterCreationAgent(llm)
story_agent = StorytellingAgent(llm)
illustration_agent = IllustrationAgent(llm)
client = OpenAI()  # Cliente para DALL-E


def get_info(conceito: str) -> str:
   """Obtém informações detalhadas sobre um conceito"""
   try:
       if not conceito:
           return "Por favor, selecione uma opção primeiro."
       return character_agent.knowledge_base.query(f"Descreva detalhadamente {conceito} em D&D 5e")["resposta"]
   except Exception as e:
       return f"Erro ao buscar informações: {str(e)}"


def gerar_imagem(prompt: str) -> str:
   """Gera uma imagem usando DALL-E"""
   try:
       response = client.images.generate(
           model="dall-e-3", #flux
           prompt=prompt,
           size="1024x1024",
           quality="standard",
           n=1,
       )
       return response.data[0].url
   except Exception as e:
       return f"Erro ao gerar imagem: {str(e)}"


def criar_personagem(nome, sexo, raca, classe, antecedente, alinhamento,
                   forca, destreza, constituicao, inteligencia, sabedoria, carisma) -> tuple[str, str, str]:
   """Função principal que coordena o fluxo de criação do personagem"""
  
   # Valida os pontos de atributo
   valido, pontos = validar_pontos_atributos(Atributos(
       forca=forca,
       destreza=destreza,
       constituicao=constituicao,
       inteligencia=inteligencia,
       sabedoria=sabedoria,
       carisma=carisma
   ))
  
   if not valido:
       return (
           f"⚠️ Erro: Total de pontos ({pontos}) excede o limite de 27 pontos.",
           None,
           None
       )
  
   # Cria o personagem base
   try:
       personagem = character_agent.create_character({
           "nome": nome,
           "sexo": sexo,
           "raca": raca,
           "classe": classe,
           "antecedente": antecedente,
           "alinhamento": alinhamento,
           "forca": forca,
           "destreza": destreza,
           "constituicao": constituicao,
           "inteligencia": inteligencia,
           "sabedoria": sabedoria,
           "carisma": carisma
       })
      
       # Gera a história
       historia = story_agent.generate_story(personagem)
       personagem.historia = historia
      
       # Gera o prompt para ilustração
       prompt_ilustracao = illustration_agent.generate_illustration_prompt(personagem)
      
       # Formata a saída em JSON
       json_output = json.dumps(personagem.model_dump(), indent=2, ensure_ascii=False)
      
       # Formata a visualização para o usuário
       markdown_output = f"""
## 🎭 Personagem Criado: {personagem.nome}


### 📝 Detalhes Básicos
- **Raça:** {personagem.raca}
- **Classe:** {personagem.classe}
- **Antecedente:** {personagem.antecedente}
- **Alinhamento:** {personagem.alinhamento}


### 💪 Atributos
- Força: {personagem.atributos.forca}
- Destreza: {personagem.atributos.destreza}
- Constituição: {personagem.atributos.constituicao}
- Inteligência: {personagem.atributos.inteligencia}
- Sabedoria: {personagem.atributos.sabedoria}
- Carisma: {personagem.atributos.carisma}


### ⚔️ Características
{chr(10).join([f"- {k}: {v}" for k,v in personagem.caracteristicas.items()])}


### 🎒 Equipamento
{chr(10).join([f"- {item}" for item in personagem.equipamento])}


### 🎯 Perícias
{chr(10).join([f"- {pericia}" for pericia in personagem.pericias])}


### 📖 História
{personagem.historia}
"""
      
       return markdown_output, json_output, prompt_ilustracao
      
   except Exception as e:
       return f"❌ Erro ao criar personagem: {str(e)}", None, None


def atualizar_pontos(forca, destreza, constituicao, inteligencia, sabedoria, carisma):
   """Calcula e formata os pontos gastos/restantes"""
   atributos = Atributos(
       forca=forca,
       destreza=destreza,
       constituicao=constituicao,
       inteligencia=inteligencia,
       sabedoria=sabedoria,
       carisma=carisma
   )
   _, pontos_gastos = validar_pontos_atributos(atributos)
   pontos_restantes = 27 - pontos_gastos
   return f"### Pontos de Habilidade\n- Pontos Gastos: {pontos_gastos}\n- Pontos Restantes: {pontos_restantes}"


def interface():
   with gr.Blocks(title="Criador de Personagem D&D 🎲") as app:
       tabs = gr.Tabs()  # Criando o container de tabs
      
       with tabs:  # Usando with para criar as tabs
           with gr.TabItem("Criação"):  # Usando TabItem em vez de Tab
               gr.Markdown("# 🐉 Criador de Personagem D&D 5e")
              
               with gr.Row():
                   with gr.Column(scale=2):
                       nome = gr.Textbox(label="Nome do Personagem")
                       sexo = gr.Radio(["Masculino", "Feminino"], label="Sexo")
                      
                       with gr.Row():
                           raca = gr.Dropdown(choices=[r.value for r in Raca], label="Raça", scale=9)
                           raca_info = gr.Button("❓", min_width=30, scale=1)
                      
                       with gr.Row():
                           classe = gr.Dropdown(choices=[c.value for c in Classe], label="Classe", scale=9)
                           classe_info = gr.Button("❓", min_width=30, scale=1)
                      
                       with gr.Row():
                           antecedente = gr.Dropdown(
                               choices=["Acólito", "Artesão", "Artista", "Charlatão", "Criminoso", "Eremita",
                                       "Forasteiro", "Herói do Povo", "Nobre", "Marinheiro", "órfão", "Sábio", "Soldado"],
                               label="Antecedente",
                               scale=9
                           )
                           antecedente_info = gr.Button("❓", min_width=30, scale=1)
                      
                       with gr.Row():
                           alinhamento = gr.Dropdown(
                               choices=["Leal e Bom", "Neutro e Bom", "Caótico e Bom",
                                       "Leal e Neutro", "Neutro", "Caótico e Neutro",
                                       "Leal e Mau", "Neutro e Mau", "Caótico e Mau"],
                               label="Alinhamento",
                               scale=9
                           )
                           alinhamento_info = gr.Button("❓", min_width=30, scale=1)
                  
                   with gr.Column(scale=1):
                       gr.Markdown("### Atributos")
                       forca = gr.Slider(8, 15, value=8, step=1, label="Força")
                       destreza = gr.Slider(8, 15, value=8, step=1, label="Destreza")
                       constituicao = gr.Slider(8, 15, value=8, step=1, label="Constituição")
                       inteligencia = gr.Slider(8, 15, value=8, step=1, label="Inteligência")
                       sabedoria = gr.Slider(8, 15, value=8, step=1, label="Sabedoria")
                       carisma = gr.Slider(8, 15, value=8, step=1, label="Carisma")
                       pontos_output = gr.Markdown("### Pontos de Habilidade\n- Pontos Gastos: 0\n- Pontos Restantes: 27")
              
               with gr.Row():
                   criar_btn = gr.Button("🎲 Criar Personagem", variant="primary", scale=2)
                   limpar_btn = gr.Button("🧹 Limpar", variant="secondary", scale=1)
              
               # Área de informações movida para baixo
               gr.Markdown("### 📚 Informações")
               info_output = gr.Markdown(
                   "Selecione uma opção e clique no botão ❓ para ver informações",
                   elem_id="info-box"
               )
              
               # CSS para estilizar a área de informações
               gr.Markdown("""
                   <style>
                   #info-box {
                       height: 200px;
                       overflow-y: auto;
                       margin: 10px;
                       padding: 15px;
                       border: 1px solid #ddd;
                       border-radius: 5px;
                       background-color: #f8f9fa;
                   }
                   </style>
               """)


           with gr.TabItem("Personagem"):  # Usando TabItem em vez de Tab
               with gr.Row():
                   with gr.Column(scale=3):
                       char_output = gr.Markdown("")
                   with gr.Column(scale=2):
                       imagem_output = gr.Image(type="filepath")
              
               with gr.Accordion("Detalhes Técnicos", open=False):
                   json_output = gr.Code(language="json")
                   prompt_ilustracao = gr.Textbox(label="Prompt para Ilustração")


       def mostrar_personagem(*args):
           resultado = criar_personagem(*args)
           if isinstance(resultado[0], str) and resultado[0].startswith("⚠️"):
               gr.Warning(resultado[0])
               return [
                   resultado[0],  # markdown
                   None,          # json
                   None,          # imagem
                   None           # prompt
               ]
          
           # Gera a imagem automaticamente
           imagem_url = gerar_imagem(resultado[2])
          
           return [
               resultado[0],  # markdown
               resultado[1],  # json
               imagem_url,    # imagem
               resultado[2]   # prompt
           ]
      
       # Eventos de atualização de pontos
       for slider in [forca, destreza, constituicao, inteligencia, sabedoria, carisma]:
           slider.change(
               atualizar_pontos,
               inputs=[forca, destreza, constituicao, inteligencia, sabedoria, carisma],
               outputs=[pontos_output]
           )
      
       # Eventos de informação
       raca_info.click(get_info, inputs=[raca], outputs=[info_output])
       classe_info.click(get_info, inputs=[classe], outputs=[info_output])
       antecedente_info.click(get_info, inputs=[antecedente], outputs=[info_output])
       alinhamento_info.click(get_info, inputs=[alinhamento], outputs=[info_output])
      
       # Eventos principais
       criar_btn.click(
           fn=mostrar_personagem,
           inputs=[nome, sexo, raca, classe, antecedente, alinhamento,
                  forca, destreza, constituicao, inteligencia, sabedoria, carisma],
           outputs=[char_output, json_output, imagem_output, prompt_ilustracao]
       ).then(
           lambda: 1,  # Retorna o índice da tab do personagem
           outputs=tabs
       )
      
       def limpar():
           return [gr.update(value=None) for _ in range(12)]
      
       limpar_btn.click(
           limpar,
           inputs=[],
           outputs=[nome, sexo, raca, classe, antecedente, alinhamento,
                   forca, destreza, constituicao, inteligencia, sabedoria, carisma]
       )
  
   return app


if __name__ == "__main__":
   app = interface()
   app.launch()
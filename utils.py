from models import Atributos

def calcular_custo(valor: int) -> int:
    custos = {
        8: 0, 9: 1, 10: 2, 11: 3,
        12: 4, 13: 5, 14: 7, 15: 9
    }
    return custos.get(valor, 0)

def validar_pontos_atributos(atributos: Atributos) -> tuple[bool, int]:
    valores = [
        atributos.forca, atributos.destreza, atributos.constituicao,
        atributos.inteligencia, atributos.sabedoria, atributos.carisma
    ]
    
    pontos_gastos = sum(calcular_custo(valor) for valor in valores)
    return pontos_gastos <= 27, pontos_gastos 
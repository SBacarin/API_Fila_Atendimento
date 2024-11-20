## Passo 1: importando a classe FastAPI e suas funcionalidades
from fastapi import FastAPI, status
##importando o pydantic dá propria biblioteca do python, é uma dependencia da FastAPI
from pydantic import BaseModel
## permite criação da variável com o preenchimento somente de N ou P , ou seja atendimento Normal ou Prioritário
from typing import Literal
## para mensagens de erro
from fastapi import HTTPException
## importando servidor web
import uvicorn

## Passo 2: criando para a variável "MyAPP" como uma instância da classe FastAPI
MyApp = FastAPI()

## criando uma estrutura para receber as vendas, semelhante a uma tabela 
class Fila(BaseModel):
    id: int     
    nome: str
    Dt_Entrada: str
    Atendido: bool = False
    Tp_Atendimento: Literal ['N', 'P']

## criando banco de dados das fila em memória
db_FilaClientes = [
    Fila(id=1, nome="Breno", Dt_Entrada='26/10/2024', Atendido=False, Tp_Atendimento='N'),
    Fila(id=2, nome="Larissa", Dt_Entrada='26/10/2024', Atendido=False, Tp_Atendimento='N'),
    Fila(id=3, nome="Karen", Dt_Entrada='26/10/2024', Atendido=False, Tp_Atendimento='N'),
    Fila(id=4, nome="Sérgio", Dt_Entrada='26/10/2024', Atendido=False, Tp_Atendimento='N'),
]

## criando endpoints,
#### Para Home 
@MyApp.get("/")
async def root():
    return {"message": "Bem vindo ao MyApp!!!, GERENCIADOR DE FILAS !!! "}

### 1.GET /fila OK
## a.Exibir a posição na fila, o nome e a data de chegada de cada cliente não atendido que está na fila.
## b.Caso não exista ninguém na fila o endpoint deve retornar um JSON vazio e o status 200.
@MyApp.get("/fila/", status_code=status.HTTP_200_OK)
async def exibir_fila():
    # filtra apenas os clientes não atendidos
    Fila_Atual = [fila_exibe for fila_exibe in db_FilaClientes if fila_exibe.Atendido == False]

    # caso não existam clientes na fila 
    if not Fila_Atual:
        return {} ## retorna um json vazio

    # ordenação da fila pela posição
    Fila_Atual = sorted(Fila_Atual, key=lambda x: x.id)

    # retorna somente os campos informados
    return [{"Posição": cliente.id, "Nome": cliente.nome, "Dt_Entrada": cliente.Dt_Entrada} for cliente in Fila_Atual]

### 2.GET /fila/:id OK
## a.Retornar os dados do cliente (posição na fila, o nome e a data de chegada) na posição (id) da fila.
## b.Se não tiver um pessoa na posição especificada no id da rota deve ser retornado o status 404 e uma mensagem informativa no JSON de retorno;
@MyApp.get("/fila/{id}", status_code=status.HTTP_200_OK)
async def mostra_cliente(id: int):
    # grava no dicionario o quando o cliente for localizado
    cliente_escolhido = [clt for clt in db_FilaClientes if clt.id == id]

    # se o cliente não for localizado
    if not cliente_escolhido:
        raise HTTPException(status_code=404, detail="Cliente não encontrado.")
    
    ## retorna o cliente localizado,o dicionario irá ter somente uma linha por isto a posição 0
    return {
        "Cliente": {
            "Posição": cliente_escolhido[0].id,
            "Nome": cliente_escolhido[0].nome,
            "Dt_Entrada": cliente_escolhido[0].Dt_Entrada
        }
    }

### 3.POST /fila
## a.adicionar um novo cliente na fila, informando seu nome e se o atendimento é normal (N) ou prioritário (P). Será identificada sua posição na fila, sua data de entrada e o campo atendido será setado como FALSE.
## b.O campo nome é obrigatório e deve ter no máximo 20 caracteres;
## c.O campo tipo de atendimento só aceita 1 caractere (N ou P);
@MyApp.post("/fila/", status_code=status.HTTP_201_CREATED)
# Função para adiconar novo cliente na fila com parametroo o parametro novo cliente
async def adiciona_cliente(novo_cliente: Fila):
    
    # confirmando tamanho do nome e gerando mensagem de erro caso for maior
    if len(novo_cliente.nome) > 20:
        raise HTTPException(status_code=400, detail="Nome deve ter no máximo 20 caracteres.")
    
    # Gerar automaticamente o próximo ID e inserindo novo cliente no BD Fila em memória
    novo_id = max([cliente.id for cliente in db_FilaClientes], default=0) + 1
    novo_cliente.id = novo_id
    db_FilaClientes.append(novo_cliente)

    return {"mensagem": "Cliente adicionado com sucesso!", "Posição": novo_id}


### 4.PUT /fila
## a.Será atualizada a posição de cada pessoa que está na fila (-1);
## b.Caso o cliente esteja na posição 1 ele será atualizado para a posição 0 e o campo atendido será setado para TRUE.
@MyApp.put("/fila/", status_code=status.HTTP_200_OK)
# cria função para atualizar fila
async def atualizar_fila():
    # se não encontrar nenhum cliente na fila retorna msgem 
    if not db_FilaClientes:
        raise HTTPException(status_code=404, detail="Fila vazia.")

    # atualiza a fila e quando encontrar o cliente na fila marca como atendido
    for cliente in db_FilaClientes:
        if cliente.id > 1:
            cliente.id -= 1
        else:
            cliente.Atendido = True

    return {"mensagem": "Fila atualizada com sucesso!"}


### 5.DELETE /fila/:id
## a.Remove o cliente indicado no id da fila e atualiza a posição dos demais clientes.
## b.Caso o cliente não seja localizado na posição especificada no id da rota deve ser retornado o status 404 e uma mensagem informativa no JSON de retorno;
@MyApp.delete("/fila/{id}", status_code=status.HTTP_200_OK)
#criando função para remover cliente
async def remover_cliente(id: int):
    cliente_removido = None
    # procura o cliente e remove
    for cliente in db_FilaClientes:
        if cliente.id == id:
            cliente_removido = cliente
            db_FilaClientes.remove(cliente)
            break

    # se não localizar gera msgem
    if not cliente_removido:
        raise HTTPException(status_code=404, detail="Cliente não encontrado.")

    # Atualizar as posições
    for cliente in db_FilaClientes:
        if cliente.id > id:
            cliente.id -= 1

    return {"mensagem": "Cliente removido e fila atualizada com sucesso!"}


## Passo 5: retorne o conteúdo(execute o servidor de desenvolvimento)
if __name__== "__main__":
    uvicorn.run(MyApp, port=8000)
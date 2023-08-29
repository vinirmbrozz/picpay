import fastapi
from header import *
from fastapi import HTTPException
import uvicorn # pip install uvicorn
import psycopg2 # pip install psycopg2-binary

app = fastapi.FastAPI()

@app.post("/usuarios")
def usuario(usuario: Usuario):
    try:
        #Verifica se existe um usuário com o mesmo CPF ou e-mail
        existeUsuario = jaExisteUsuario(usuario.cpf, usuario.email)
        if existeUsuario:
            raise HTTPException(status_code=400, detail="Usuário já existe")
        else:
            criarUsuario(usuario)
            return {"return": "Usuário criado"}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail="Erro ao criar usuário: " + e)


@app.post("/depositar")
def deposito(valor: Saldo):
    try:
        #Verifica se existe um usuário com o mesmo CPF ou e-mail
        existeUsuario = jaExisteUsuario(valor.cpf, "")
        if not existeUsuario:
            raise HTTPException(status_code=400, detail="Usuário não encontrado")
        else:
            depositar(valor)
            return {"return": "Depósito realizado"}
    except Exception as e:
        raise HTTPException(status_code=400, detail="Erro ao realizar depósito: " + e)
    
@app.post("/transferir")
def transferencia(valor: Transferencia):
    try:
        #Verifica se existe um usuário com o mesmo CPF ou e-mail
        usuarioOrigem = jaExisteUsuario(valor.cpf_origem, "")
        usuarioDestino = jaExisteUsuario(valor.cpf_destino, "")
        if not usuarioOrigem:
            raise HTTPException(status_code=400, detail="Usuário de origem não encontrado")
        if not usuarioDestino:
            raise HTTPException(status_code=400, detail="Usuário de destino não encontrado")
        else:
            transferir(valor)
            return {"return": "Transferência realizada"}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail="Erro ao realizar transferência: " + str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)



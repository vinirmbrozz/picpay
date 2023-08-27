import fastapi
from fastapi import HTTPException
from typing import ClassVar
from pydantic import BaseModel, EmailStr
import uvicorn # pip install uvicorn
import psycopg2 # pip install psycopg2-binary

app = fastapi.FastAPI()

def conectarBanco():
    conexao = psycopg2.connect(
        host="localhost",
        database="picpay",
        port = 5432,
        user = "postgres",
        password = "postgres"
    )
    return conexao

#Classe para receber os dados do usuário.
class Usuario(BaseModel):
    nome: str
    cpf: str
    email: str
    senha: str
    lojista: bool

@app.post("/usuarios")
def usuario(usuario: Usuario):
    conexao = conectarBanco()
    cur = conexao.cursor()
    
    cur.execute("select * from usuarios where cpf_cnpj = %s or email = %s", (usuario.cpf, usuario.email))
    existeUsuario = cur.fetchone()
    #Verifica se existe um usuário com o mesmo CPF ou e-mail
    if existeUsuario:
        cur.close()
        conexao.close()
        raise HTTPException(status_code=400, detail="CPF ou e-mail já cadastrado")
    
    #Criar usuário
    cur.execute("insert into usuarios (nome, cpf_cnpj, email, senha, lojista) values (%s, %s, %s, %s, %s)", (usuario.nome, usuario.cpf, usuario.email, usuario.senha, usuario.lojista))
    
    # Comitar a inserção de usuário e fechar a conexão
    conexao.commit()    

    
    cur.close()
    conexao.close()
    
    return {"return": "Usuário criado"}


@app.post("/depositar")
def deposito(valor: float, cpf: str):
    conexao = conectarBanco()
    cur = conexao.cursor()
    
    cur.execute("select * from usuarios where cpf_cnpj = %s", (cpf,))
    usuario = cur.fetchone()
    #Verifica se existe um usuário com o mesmo CPF ou e-mail
    if not usuario:
        cur.close()
        conexao.close()
        raise HTTPException(status_code=400, detail="Usuário não encontrado")
    
    #Realizar deposito
    cur.execute("select * from saldo where id_usuario = %s", (cpf,))
    saldo = cur.fetchone()
    if saldo:
        cur.execute("update saldo set saldo = saldo + %s where id_usuario = %s", (valor, cpf))
    else:
        cur.execute("insert into saldo (id_usuario, saldo) values (%s, %s)", (cpf, valor))
    
    
    # Comitar a inserção de usuário e fechar a conexão
    conexao.commit()    

    
    cur.close()
    conexao.close()
    
    return {"return": "Depósito realizado com sucesso"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)



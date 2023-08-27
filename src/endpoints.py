import fastapi

app = fastapi.FastAPI()

class Usuario:
    def __init__(self, nome, cpf, email, senha):
        self.nome = nome
        self.cpf = cpf
        self.email = email
        self.senha = senha

app.post("/usuarios")
def usuario(usuario: Usuario):
    
    return {"return": "Usuário criado"}


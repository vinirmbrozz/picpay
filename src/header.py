from pydantic import BaseModel, EmailStr
import psycopg2

#Classe para receber os dados do usuário.
class Usuario(BaseModel):
    nome: str
    cpf: str
    email: str
    senha: str
    lojista: bool
    
class Saldo(BaseModel):
    cpf: str
    saldo: float
    
class Transferencia(BaseModel):
    cpf_origem: str
    cpf_destino: str
    valor: float
    
def conectarBanco():
    conexao = psycopg2.connect(
        host="localhost",
        database="picpay",
        port = 5432,
        user = "postgres",
        password = "postgres"
    )
    return conexao

def criarUsuario(usuario):
    conexao = conectarBanco()
    cur = conexao.cursor()
    
    cur.execute("insert into usuarios (nome, cpf_cnpj, email, senha, lojista) values (%s, %s, %s, %s, %s)", (usuario.nome, usuario.cpf, usuario.email, usuario.senha, usuario.lojista))
    
    # Comitar a inserção de usuário e fechar a conexão
    conexao.commit()    
    cur.close()
    conexao.close()

def jaExisteUsuario(cpf, email):
    conexao = conectarBanco()
    cur = conexao.cursor()
    
    cur.execute("select * from usuarios where cpf_cnpj = %s or email = %s", (cpf, email))
    existeUsuario = cur.fetchone()
    #Verifica se existe um usuário com o mesmo CPF ou e-mail
    if existeUsuario:
        cur.close()
        conexao.close()
        return True
    else:
        cur.close()
        conexao.close()
        return False

def depositar(valor):
    conexao = conectarBanco()
    cur = conexao.cursor()
    
    cur.execute("select * from usuarios where cpf_cnpj = %s", (valor.cpf,))
    usuario = cur.fetchone()
    #Verifica se existe um usuário com o mesmo CPF ou e-mail
    if not usuario:
        cur.close()
        conexao.close()
        return {"return": "Usuário não encontrado"}
    
    #Realizar deposito
    cur.execute("select * from saldo where id_usuario = %s", (valor.cpf,))
    saldo = cur.fetchone()
    if saldo:
        cur.execute("update saldo set saldo = saldo + %s where id_usuario = %s", (valor.saldo, valor.cpf))
    else:
        cur.execute("insert into saldo (id_usuario, saldo) values (%s, %s)", (valor.cpf, valor.saldo))
    
    
    # Comitar a inserção de usuário e fechar a conexão
    conexao.commit()    

    
    cur.close()
    conexao.close()
    
    return {"return": "Depósito realizado com sucesso"}

def transferir(valor):
    try:
        #Verifica se existe um usuário com o mesmo CPF ou e-mail
        usuarioOrigem = jaExisteUsuario(valor.cpf_origem, "")
        usuarioDestino = jaExisteUsuario(valor.cpf_destino, "")
        if not usuarioOrigem:
            raise Exception("Usuário de origem não encontrado")
        if not usuarioDestino:
            raise Exception("Usuário de destino não encontrado")
        
        
        conexao = conectarBanco()
        cur = conexao.cursor()
        
        #Realizar transferencia
        cur.execute("select * from saldo where id_usuario = %s", (valor.cpf_origem,))
        saldo = cur.fetchone()
        if saldo:
            if saldo[1] < valor.valor:
                cur.close()
                conexao.close()
                return {"return": "Saldo insuficiente"}
            else:
                cur.execute("update saldo set saldo = saldo - %s where id_usuario = %s", (valor.valor, valor.cpf_origem))
                cur.execute("select * from saldo where id_usuario = %s", (valor.cpf_destino,))
                saldo = cur.fetchone()
                if saldo:
                    cur.execute("update saldo set saldo = saldo + %s where id_usuario = %s", (valor.valor, valor.cpf_destino))
                    cur.execute("insert into transferencias (log_transferencia) values (%s)", ("Transferência de " + valor.cpf_origem + " para " + valor.cpf_destino + " no valor de " + str(valor.valor),))
                else:
                    cur.execute("insert into saldo (id_usuario, saldo) values (%s, %s)", (valor.cpf_destino, valor.valor))
                    cur.execute("insert into transferencias (log_transferencia) values (%s)", ("Transferência de " + valor.cpf_origem + " para " + valor.cpf_destino + " no valor de " + str(valor.valor),))
        else:
            cur.close()
            conexao.close()
            return {"return": "Saldo insuficiente"}
        
        
        # Comitar a inserção de usuário e fechar a conexão
        conexao.commit()    

        
        cur.close()
        conexao.close()
    
        return {"return": "Transferência realizada com sucesso"}
    
    except Exception as e:
        raise Exception("Erro ao realizar transferência: " + str(e))

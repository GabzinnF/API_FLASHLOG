import datetime

from flask_login import UserMixin
from sqlalchemy import create_engine, String, Integer, func, Column, DateTime, Float
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base

# TENTE ESTA STRING PRIMEIRO (SEM SENHA):
engine = create_engine('mysql+pymysql://root@localhost:3306/flashlog')

# SE NÃO FUNCIONAR, COMENTE A DE CIMA E DESCOMENTE A DE BAIXO (COM SENHA 'root'):
# engine = create_engine('mysql+pymysql://root:root@localhost:3306/flashlog')

# SE VOCÊ USA XAMPP/WAMP, TENTE ESTA:
# engine = create_engine('mysql+pymysql://root:@localhost:3306/flashlog')

session_factory = sessionmaker(bind=engine)
db_session = scoped_session(session_factory)

Base = declarative_base()
Base.query = db_session.query_property()

class Movimentacao(Base):
    __tablename__ = 'movimentacao'
    id = Column(Integer, primary_key=True)
    hora = Column(DateTime, default=func.now)
    tipo = Column(String(70), nullable=False)

class Centro_distribuicao(Base):
    __tablename__ = 'centro_distribuicao'
    id = Column(Integer, primary_key=True)
    destinatario = Column(String(70), nullable=False)
    local_ = Column(String(100), nullable=False)

class Usuario(Base):
    __tablename__ = 'usuarios'
    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    senha_hash = Column(String(255), nullable=False)
    papel = Column(String(50), default='usuario')
    criado_em = Column(DateTime, default=func.now)

class Operador(Base):
    __tablename__ = 'operador'
    id = Column(Integer, primary_key=True)
    nome = Column(String(70), nullable=False)
    cep = Column(String(20), nullable=False)
    rua = Column(String(70), nullable=False)
    bairro = Column(String(70), nullable=False)
    cidade = Column(String(70), nullable=False)
    estado = Column(String(70), nullable=False)
    numero_casa = Column(Integer, nullable=False)
    complemento = Column(String(70))

class Pacote(Base):
    __tablename__ = 'pacotes'
    id = Column(Integer, primary_key=True)
    nome = Column(String(70), nullable=False)
    codigo = Column(String(20), nullable=False)
    cpf = Column(String(14), nullable=False)

class Destinatario(Base):
    __tablename__ = 'destinatarios'
    id = Column(Integer, primary_key=True)
    proprietario_enco = Column(String(70), nullable=False)

class Funcionario(Base, UserMixin):
    __tablename__ = 'funcionarios'
    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    data_nascimento = Column(DateTime, nullable=False)
    cpf = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    senha = Column(String(255), nullable=False)
    cargo = Column(String, nullable=False)
    salario = Column(Float, nullable=False)

# Criar tabelas dentro de um bloco try para identificar o erro de conexão exato
if __name__ == "__main__":
    try:
        Base.metadata.create_all(engine)
        print("Conexão bem sucedida e tabelas criadas!")
    except Exception as e:
        print(f"ERRO DE CONEXÃO: Verifique se o banco 'flashlog' existe e se a senha está correta.")
        print(f"Detalhe do erro: {e}")
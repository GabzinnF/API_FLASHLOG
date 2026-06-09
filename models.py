import datetime

from flask_login import UserMixin
from sqlalchemy import create_engine, String, Integer, func, Column, DateTime, Float, ForeignKey
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base
from werkzeug.security import generate_password_hash, check_password_hash

engine = create_engine('mysql+pymysql://root:senaisp@localhost:3306/flashlog')



session_factory = sessionmaker(bind=engine)
db_session = scoped_session(session_factory)

Base = declarative_base()
Base.query = db_session.query_property()

class Movimentacao(Base):
    __tablename__ = 'movimentacoes'
    id = Column(Integer, primary_key=True)
    encomenda_id = Column(Integer, ForeignKey('encomendas.id'),nullable=False)
    criado_em = Column(DateTime, server_default=func.now())
    tipo = Column(String(70), nullable=False)
    centro_id = Column(Integer, ForeignKey('centro_distribuicaos.id'), nullable=False)

    def serialize(self, centro):
        dados={
            'id':self.id,
            'id_encomenda':self.encomenda_id,
            'tipo':self.tipo,
            'localizacao':centro.serialize(),
            'criado_em' : self.criado_em,
        }
        return dados

class Centro_distribuicao(Base):
    __tablename__ = 'centro_distribuicaos'
    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)
    cidade = Column(String(100), nullable=False)
    estado = Column(String(100), nullable=False)

    def serialize(self):
        dados={
            'id':self.id,
            'nome':self.nome,
            'cidade':self.cidade,
            "estado":self.estado
        }
        return dados


class Cliente(Base):
    __tablename__ = 'clientes'
    id = Column(Integer, primary_key=True)
    nome = Column(String(70), nullable=False)
    cep = Column(Integer, nullable=False)
    rua = Column(String(70), nullable=False)
    bairro = Column(String(70), nullable=False)
    cidade = Column(String(70), nullable=False)
    estado = Column(String(70), nullable=False)
    numero_casa = Column(Integer, nullable=False)
    complemento = Column(String(70))
    email = Column(String(100), nullable=False, unique=True)

    def serialize(self):
        dados={
            'id':self.id,
            'nome':self.nome,
            'email':self.email,
            'cep':self.cep,
            'rua':self.rua,
            'bairro':self.bairro,
            'cidade':self.cidade,
            'estado':self.estado,
            'numero_casa':self.numero_casa,
            'complemento':self.complemento,
        }
        return dados

class Emcomenda(Base):
    __tablename__ = 'encomendas'
    id = Column(Integer, primary_key=True)
    nome = Column(String(70), nullable=False)
    codigo_rastreio = Column(String(100), nullable=False)
    fragilidade = Column(String(100), nullable=False)
    tipo = Column(String(100), nullable=False)
    cliente_id = Column(String ,ForeignKey('clientes.id'), nullable=False)
    remetente_id = Column(String ,ForeignKey('remetentes.id'), nullable=False)

    def serialize(self, cliente=None, remetente=None):
        dados={
            'id':self.id,
            'nome':self.nome,
            'codigo_rastreio':self.codigo_rastreio,
            'fragilidade':self.fragilidade,
            'tipo':self.tipo,
            'remetente':remetente.serialize() if remetente else self.remetente_id,
            'destinatario':cliente.serialize() if cliente else self.cliente_id


        }
        return dados

    def set_senha_hash(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def check_password_hash(self, senha):
        return check_password_hash(self.senha_hash, senha)

    def __repr__(self):
        return f'<Emcomenda: {self.nome}>'

    def set_password(self, password):
        self.senha = generate_password_hash(password)

class Remetente(Base):
    __tablename__ = 'remetentes'
    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)
    cidade = Column(String(100), nullable=False)
    estado = Column(String(100), nullable=False)


    def serialize(self):
        dados = {
            'id': self.id,
            'nome': self.nome,
            'cidade': self.cidade,
            "estado": self.estado
        }
        return dados

class Funcionario(Base, UserMixin):
    __tablename__ = 'funcionarios'
    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    cpf = Column(String(13), nullable=False)
    email = Column(String, nullable=False, unique=True)
    senha = Column(String(255), nullable=False)

    def serialize(self):
        dados={
            'id':self.id,
            'nome':self.nome,
            'email':self.email,
            'cpf':self.cpf,
        }
        return dados

    def set_senha_hash(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def check_password_hash(self, senha):
        return check_password_hash(self.senha_hash, senha)

    def __repr__(self):
        return f'<Funcionario: {self.nome}>'

    def set_password(self, password):
        self.senha = generate_password_hash(password)


# Criar tabelas dentro de um bloco try para identificar o erro de conexão exato
if __name__ == "__main__":
    try:
        Base.metadata.create_all(engine)
        print("Conexão bem sucedida e tabelas criadas!")
    except Exception as e:
        print(f"ERRO DE CONEXÃO: Verifique se o banco 'flashlog' existe e se a senha está correta.")
        print(f"Detalhe do erro: {e}")
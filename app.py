import datetime
import random
import string

from flask import Flask, jsonify, request, render_template, url_for
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, JWTManager
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from models import db_session, Funcionario, Emcomenda, \
    Movimentacao, Cliente, Centro_distribuicao, Remetente  # Certifique-se que o database.py está na mesma pasta

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'batata'  # Mude para algo seguro em produção
jwt = JWTManager(app)


# --- ROTAS PARA SERVIR AS PÁGINAS (FRONTEND) ---

@app.route('/')
def home():
    return render_template('home.html')


@app.route('/login')
def tela_login():
    return render_template('login.html')


@app.route('/cadastro')
def tela_cadastro():
    return render_template('cadastro.html')

@app.route('/movimentacao')
def lista_movimentacao():
    # Rota que estava faltando e causava o BuildError
    db = db_session()
    try:
        api_movimentacao = select(Movimentacao)
        result = db_session.execute(api_movimentacao).scalars().all()
        movimentacoes = []
        for movimentacao in result:
            sql_centro = select(Centro_distribuicao).where(Centro_distribuicao.id == movimentacao.centro_id)
            centro = db_session.execute(sql_centro).scalars().one_or_none()
            movimentacoes.append(movimentacao.serialize(centro))



        print(result)
        return jsonify({"movimentacoes": movimentacoes}), 200
    finally:
        db.close()

@app.route('/funcionarios')
def funcionarios():
    # Rota que estava faltando e causava o BuildError
    db = db_session()
    try:
        api_funcionario = select(Funcionario)
        result = db_session.execute(api_funcionario).scalars().all()
        funcionarios = []
        for funcionario in result:
            funcionarios.append(funcionario.serialize())
        print(result)
        return jsonify({"funcionarios": funcionarios}), 200
    finally:
        db.close()


@app.route('/clientes')
def clientes():
    # Rota que estava faltando e causava o BuildError
    db = db_session()
    try:
        api_cliente = select(Cliente)
        result = db_session.execute(api_cliente).scalars().all()
        clientes = []
        for cliente in result:
            clientes.append(cliente.serialize())
        print(result)
        return jsonify({"clientes": clientes}), 200
    finally:
        db.close()


@app.route('/remetente')
def lista_remetente():
    db = db_session()
    try:
        api_remetente = select(Remetente)
        result = db_session.execute(api_remetente).scalars().all()
        remetente = []
        for remetentes in result:
            remetente.append(remetentes.serialize())
        print(result)
        return jsonify({"remetentes": remetente}), 200
    finally:
        db.close()
@app.route('/unidades')
def unidades_centro():
    # Rota que estava faltando e causava o BuildError
    db = db_session()
    try:
        api_centro = select(Centro_distribuicao)
        result = db_session.execute(api_centro).scalars().all()
        centros = []
        for centro_distribuicao in result:
            centros.append(centro_distribuicao.serialize())
        print(result)
        return jsonify({"centro_distribuicao": centros}), 200
    finally:
        db.close()
@app.route('/encomendas')
def encomendas():
    # Rota que estava faltando e causava o BuildError
    db = db_session()
    try:
        api_encomenda = select(Emcomenda)
        result = db_session.execute(api_encomenda).scalars().all()
        print(result)

        encomendas = []
        for encomenda in result:
            sql_cliente = select(Cliente).where(Cliente.id == encomenda.cliente_id)
            sql_remetente = select(Remetente).where(Remetente.id == encomenda.remetente_id)
            cliente = db_session.execute(sql_cliente).scalars().one_or_none()
            remetente = db_session.execute(sql_remetente).scalars().one_or_none()
            encomendas.append(encomenda.serialize(cliente, remetente))



        return jsonify({"encomendas": encomendas}), 200
    finally:
        db.close()

# --- ROTAS DE API (BACKEND) ---

@app.route('/api/login', methods=['POST'])
def login():
    try:
        dados = request.get_json()
        email = dados.get('email')
        senha = dados.get('senha')


        db = db_session()
        sql = select(Funcionario).where(Funcionario.email == email)
        usuario = db.execute(sql).scalar()

        # Importante: No database.py, a classe Usuario precisa do método check_password_hash
        if usuario and usuario.check_password_hash(senha):
            access_token = create_access_token(identity=str(usuario.email))
            texto = "Login realizado com sucesso"
            return jsonify({
                "Sistema": texto,
                "access_token": access_token,
                "Bem Vindo": usuario.nome,


            }), 200

        return jsonify({"msg": "E-mail ou senha incorretos"}), 401
    except Exception as e:
        return jsonify({"msg": str(e)}), 500
    finally:
        db.close()


@app.route('/api/cadastro', methods=['POST'])
def cadastro():
    dados = request.get_json()
    nome = dados.get('nome')
    email = dados.get('email')
    cep = dados.get('cep')
    rua = dados.get('rua')
    bairro = dados.get('bairro')
    cidade = dados.get('cidade')
    estado = dados.get('estado')
    numero_casa = dados.get('numero_casa')
    complemento = dados.get('complemento')

    if not nome or not email:
        return jsonify({"msg": "Preencha todos os campos"}), 400

    db = db_session()
    try:
        # Verifica se email já existe
        check = select(Cliente).where(Cliente.email == email)
        if db.execute(check).scalar():
            return jsonify({"msg": "Email já cadastrado"}), 409

        novo_cliente = Cliente(nome=nome, email=email ,cep=cep, rua=rua,bairro=bairro,cidade=cidade,estado=estado,numero_casa=numero_casa,complemento=complemento)
         # Método que deve estar no database.py

        db.add(novo_cliente)
        db.commit()
        return jsonify({"msg": "Cadastrado com sucesso"}), 201
    except Exception as e:
        db.rollback()
        return jsonify({"msg": str(e)}), 500
    finally:
        db.close()

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro_funcionario():
    db = db_session()
    dados = request.get_json()
    try:
        if request.method == 'POST':
            json_funcionario = request.get_json()
            nome = json_funcionario.get('nome')
            cpf = json_funcionario.get('cpf')
            email = json_funcionario.get('email')
            senha = json_funcionario.get('senha')

            # data_convertida = datetime.strptime(data_nascimento, '%Y-%m-%d')
            # data_brasil = datetime.strftime(data_convertida, '%d-%m-%Y')

            if not nome or not email or not senha or not cpf:
                return jsonify({"msg": "Preencher todos os campos"})
            verifica_email = select(Funcionario).where(Funcionario.email == email)
            verifica_cpf = select(Funcionario).where(Funcionario.cpf == cpf)
            existe_email = db.execute(verifica_email, ).scalar_one_or_none()
            existe_cpf = db.execute(verifica_cpf, ).scalar_one_or_none()
            if existe_email:
                return jsonify({"msg": "Email ja existente"})

            if len(cpf) > 13 or len(cpf) < 13:
                return jsonify({"msg": "cpf invalido"})

            if existe_cpf:
                return jsonify({"msg": "cpf ja existente"})


            novo_funcionario = Funcionario(nome=nome, email=email, cpf=cpf)
            novo_funcionario.set_password(senha)
            db.add(novo_funcionario)
            db.commit()
            funcionario_id = novo_funcionario.id

            return jsonify({"msg": "Funcionario cadastrado com sucesso", "funcionario_id": funcionario_id}), 201
    except SQLAlchemyError as e:
        return jsonify({"msg": f"Erro na base de dados ao cadastrar funcionario: {str(e)}"})
    except Exception as e:
        return jsonify({"msg": f"Erro ao cadastrar funcionario: {str(e)}"}), 500
    return jsonify(dados)


@app.route('/cadastro_encomenda', methods=['POST'])
def cadastro_encomenda():


    json_encomenda = request.get_json()
    nome = json_encomenda.get('nome')
    fragilidade = json_encomenda.get('fragilidade')
    tipo = json_encomenda.get('tipo')
    remetente_id = json_encomenda.get('remetente_id')
    cliente_id = json_encomenda.get('cliente_id')

    if not nome or not fragilidade or not tipo:
        return jsonify({"msg": "Os campos nome, fragilidade e tipo são obrigatórios"}), 400
    db = db_session()
    try:
        codigo_gerado = gerar_codigo_unico(db)

        nova_encomenda = Emcomenda(
            codigo_rastreio=codigo_gerado,
            nome=nome,
            fragilidade=fragilidade,
            tipo=tipo,
            remetente_id=remetente_id,
            cliente_id=cliente_id
        )


        db.add(nova_encomenda)
        db.commit()


        return jsonify({"msg": "Encomenda cadastrada com sucesso",
                        "encomenda_id": nova_encomenda.id,
                        "codigo_rastreio" : nova_encomenda.codigo_rastreio,
                        "nome" : nova_encomenda.nome,
                        "fragilidade" : nova_encomenda.fragilidade,
                        "tipo" : nova_encomenda.tipo,
                        "cliente_id" : nova_encomenda.cliente_id,
                        "rementente_id" : nova_encomenda.remetente_id
                     }), 201

    except Exception as e:
        db.rollback()
        return jsonify({"msg": f"Erro ao cadastrar encomenda: {str(e)}"}), 500
    finally:
        db.close()

@app.route('/centro_distribuicao',methods=['POST'])
def centro_distribuicao():
    db = db_session()
    dados = request.get_json()
    try:
        if request.method == 'POST':
            json_distribuicao = request.get_json()
            nome = json_distribuicao.get('nome')
            cidade = json_distribuicao.get('cidade')
            estado = json_distribuicao.get('estado')

            if not cidade or not estado:
                return jsonify({"msg": "Preencher todos os campos"})

            novo_centro_distribuicao=Centro_distribuicao(
                nome=nome, cidade=cidade, estado=estado)
            db.add(novo_centro_distribuicao)
            db.commit()
            return jsonify({
                "msg": "Movimentacao feita com sucesso",
                'unidades': {
                    "id": novo_centro_distribuicao.id,
                    'nome' : novo_centro_distribuicao.nome,
                    'cidade' : novo_centro_distribuicao.cidade,
                    'estado' : novo_centro_distribuicao.estado
                }

            }), 201

    except Exception as e:
        db.rollback()
        return jsonify({"Erro": str(e)}), 500


    return jsonify(dados)

@app.route('/cadastro_movimentacao', methods=['GET', 'POST'])
def cadastro_movimentacao():
    db = db_session()
    dados = request.get_json()
    try:
        if request.method == 'POST':
            json_movimentacao = request.get_json()
            encomenda_id = json_movimentacao.get('encomenda_id')
            centro_id = json_movimentacao.get('centro_id')
            if not encomenda_id or not centro_id:
                return jsonify({"msg": "Preencher todos os campos"})
            # Verificar a ultima movimentação da encomenda
            # Fazer um select para trazer essa movimentação
            sql_movimentacao = select(Movimentacao).where(Movimentacao.encomenda_id == encomenda_id).order_by(Movimentacao.criado_em.desc()).limit(1)
            ultima_movimentacao = db_session.execute(sql_movimentacao).scalars().one_or_none()

            if ultima_movimentacao is None:
                tipo = 'saida'
            else:
                if ultima_movimentacao.tipo == 'saida':
                    tipo = 'chegada'
                    if ultima_movimentacao.centro_id == centro_id:
                        return jsonify({
                            "msg": "Não pode chegar no mesmo lugar que saiu",
                        })
                else:
                    tipo = 'saida'



            nova_movimentacao=Movimentacao(
               tipo=tipo,encomenda_id=encomenda_id,centro_id=centro_id
            )
            db.add(nova_movimentacao)
            db.commit()

            return jsonify({
                "msg": "Movimentacao feita com sucesso",
                'movimentacao': {
                    "id": nova_movimentacao.id,
                    'criado_em': nova_movimentacao.criado_em.strftime('%d/%m/%Y'),
                    'tipo': nova_movimentacao.tipo
                }

            }), 201

    except Exception as e:
        db.rollback()
        return jsonify({"Erro": str(e)}), 500
    return jsonify(dados)
@app.route('/cadastro_remetente',methods=['POST'])
def cadastro_remetente():
    db = db_session()
    dados = request.get_json()
    try:
        if request.method == 'POST':
            json_remetente = request.get_json()
            nome = json_remetente.get('nome')
            cidade = json_remetente.get('cidade')
            estado = json_remetente.get('estado')

            if not cidade or not estado:
                return jsonify({"msg": "Preencher todos os campos"})

            novo_remetente = Remetente(
                nome=nome, cidade=cidade, estado=estado)
            db.add(novo_remetente)
            db.commit()
            return jsonify({
                "msg": "Remetente cadastrado com sucesso",
                'remetente': {
                    "id": novo_remetente.id,
                    'nome': novo_remetente.nome,
                    'cidade': novo_remetente.cidade,
                    'estado': novo_remetente.estado
                }

            }), 201

    except Exception as e:
        db.rollback()
        return jsonify({"Erro": str(e)}), 500

    return jsonify(dados)
@app.route('/rastreio',methods=['POST'])
def rastreio_encomenda():
    db = db_session()
    try:
        json_rastreio = request.get_json()
        codigo = json_rastreio.get('codigo')

        #traz a encomenda de acordo com o codigo
        rastrear_encomenda = select(Emcomenda).where(Emcomenda.codigo_rastreio == codigo)
        encomenda = db_session.execute(rastrear_encomenda).scalars().one_or_none()

        #traz as movimentacoes da encomenda de acordo com seu id
        rastrear_id_encomenda = select(Movimentacao).where(Movimentacao.encomenda_id == encomenda.id)
        movimentacao_encomenda = db_session.execute(rastrear_id_encomenda).scalars().all()

        movimentacoes = []
        for movimentacao in movimentacao_encomenda:
            sql_centro = select(Centro_distribuicao).where(Centro_distribuicao.id == movimentacao.centro_id)
            centro = db_session.execute(sql_centro).scalars().one_or_none()
            movimentacoes.append(movimentacao.serialize(centro))




        print(encomenda)
        return jsonify({"encomenda" : encomenda.serialize(),
                        "movimentacoes" : movimentacoes
                        })
    except Exception as e:
        db.rollback()
        return jsonify({"Erro": str(e)}), 500



def gerar_codigo_unico(db):
    data = datetime.datetime.now()
    alfabeto = ["a", "b", "c", "d", "e", "f", "g", "h",
                "i","j","k", "l", "m", "n", "o", "p",
                "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]

    codigo_1 = random.choice(alfabeto).upper()
    codigo_2 = random.choice(alfabeto).upper()
    codigo_3 = random.choice(alfabeto).upper()
    codigo_unico = str(data.timestamp()).replace(".", "")
    codigo_final = str(codigo_1 + codigo_2 + codigo_3) + codigo_unico

    consulta = select(Emcomenda).where(Emcomenda.codigo_rastreio == codigo_final)
    resultado = db.execute(consulta).scalars().first()

    if resultado:
        return gerar_codigo_unico(db)

    return codigo_final

@app.route('/api/dados_protegidos', methods=['GET'])
@jwt_required()
def protegido():
    usuario_atual = get_jwt_identity()
    return jsonify({"msg": f"Olá {usuario_atual}, você acessou dados protegidos"}), 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
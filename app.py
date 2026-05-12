import datetime
from flask import Flask, jsonify, request, render_template, url_for
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, JWTManager
from sqlalchemy import select
from database import db_session, Usuario, Pacote  # Certifique-se que o database.py está na mesma pasta

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


@app.route('/funcionarios')
def funcionarios():
    # Rota que estava faltando e causava o BuildError
    return render_template('funcionarios.html')


# --- ROTAS DE API (BACKEND) ---

@app.route('/api/login', methods=['POST'])
def login():
    try:
        dados = request.get_json()
        email = dados.get('email')
        senha = dados.get('senha')

        db = db_session()
        sql = select(Usuario).where(Usuario.email == email)
        usuario = db.execute(sql).scalar()

        # Importante: No database.py, a classe Usuario precisa do método check_password_hash
        if usuario and usuario.check_password_hash(senha):
            access_token = create_access_token(identity=str(usuario.email))
            return jsonify({
                "access_token": access_token,
                "nome": usuario.nome,
                "papel": usuario.papel
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
    senha = dados.get('senha')

    if not nome or not email or not senha:
        return jsonify({"msg": "Preencha todos os campos"}), 400

    db = db_session()
    try:
        # Verifica se email já existe
        check = select(Usuario).where(Usuario.email == email)
        if db.execute(check).scalar():
            return jsonify({"msg": "Email já cadastrado"}), 409

        novo_usuario = Usuario(nome=nome, email=email)
        novo_usuario.set_senha_hash(senha)  # Método que deve estar no database.py

        db.add(novo_usuario)
        db.commit()
        return jsonify({"msg": "Cadastrado com sucesso"}), 201
    except Exception as e:
        db.rollback()
        return jsonify({"msg": str(e)}), 500
    finally:
        db.close()


# Exemplo de rota protegida por Token
@app.route('/api/dados_protegidos', methods=['GET'])
@jwt_required()
def protegido():
    usuario_atual = get_jwt_identity()
    return jsonify({"msg": f"Olá {usuario_atual}, você acessou dados protegidos"}), 200


if __name__ == '__main__':
    app.run(debug=True)
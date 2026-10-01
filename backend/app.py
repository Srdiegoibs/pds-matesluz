from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configuração do banco de dados no diretório instance/
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///petshop.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# ---------------------------------------------------------------
# MODELOS (CLASSES DO BANCO DE DADOS)
# ---------------------------------------------------------------

class Dono(db.Model):
    __tablename__ = "donos"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)

    # Relacionamento que permite acessar dono.pets e pet.dono
    pets = db.relationship("Pet", backref="dono")

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "telefone": self.telefone
        }


class Pet(db.Model):
    __tablename__ = "pets"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    especie = db.Column(db.String(50), nullable=False)
    idade = db.Column(db.Integer, nullable=False)
    dono_id = db.Column(db.Integer, db.ForeignKey("donos.id"), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "especie": self.especie,
            "idade": self.idade,
            "dono_id": self.dono_id,
            "dono_nome": self.dono.nome if self.dono else None
        }


# ---------------------------------------------------------------
# ROTAS DE DONOS - CÓDIGO DE REFERÊNCIA (ORM)
# ---------------------------------------------------------------

@app.route("/donos", methods=["GET"])
def listar_donos():
    donos = Dono.query.all()
    return jsonify([dono.to_dict() for dono in donos])


@app.route("/donos/<int:dono_id>", methods=["GET"])
def buscar_dono(dono_id):
    dono = db.session.get(Dono, dono_id)

    if dono is None:
        return jsonify({"erro": "Dono nao encontrado"}), 404

    return jsonify(dono.to_dict())


@app.route("/donos", methods=["POST"])
def criar_dono():
    dados = request.json

    if not dados or "nome" not in dados or "telefone" not in dados:
        return jsonify({"erro": "Informe nome e telefone"}), 400

    novo_dono = Dono(nome=dados["nome"], telefone=dados["telefone"])
    db.session.add(novo_dono)
    db.session.commit()

    return jsonify(novo_dono.to_dict()), 201


@app.route("/donos/<int:dono_id>", methods=["PUT"])
def atualizar_dono(dono_id):
    dados = request.json

    if not dados or "nome" not in dados or "telefone" not in dados:
        return jsonify({"erro": "Informe nome e telefone"}), 400

    dono = db.session.get(Dono, dono_id)

    if dono is None:
        return jsonify({"erro": "Dono nao encontrado"}), 404

    dono.nome = dados["nome"]
    dono.telefone = dados["telefone"]
    db.session.commit()

    return jsonify(dono.to_dict())


@app.route("/donos/<int:dono_id>", methods=["DELETE"])
def remover_dono(dono_id):
    dono = db.session.get(Dono, dono_id)

    if dono is None:
        return jsonify({"erro": "Dono nao encontrado"}), 404

    db.session.delete(dono)
    db.session.commit()

    return jsonify({"mensagem": "Dono removido com sucesso"})


# ---------------------------------------------------------------
# ROTAS DE PETS - REESCRITAS COM ORM
# ---------------------------------------------------------------

@app.route("/pets", methods=["GET"])
def listar_pets():
    dono_id = request.args.get("dono_id")

    if dono_id is None:
        pets = Pet.query.all()
    else:
        # Converter para inteiro conforme orientado na aula
        pets = Pet.query.filter_by(dono_id=int(dono_id)).all()

    return jsonify([pet.to_dict() for pet in pets])


@app.route("/pets/<int:id>", methods=["GET"])
def buscar_pet(id):
    pet = db.session.get(Pet, id)

    if pet is None:
        return jsonify({"erro": "Pet nao encontrado"}), 404

    return jsonify(pet.to_dict())


@app.route("/pets", methods=["POST"])
def criar_pet():
    dados = request.get_json()

    if not dados or not all(
        campo in dados for campo in ["nome", "especie", "idade", "dono_id"]
    ):
        return jsonify({
            "erro": "Informe nome, especie, idade e dono_id"
        }), 400

    # Desafio: Verificar se o dono_id fornecido existe no banco de dados
    dono = db.session.get(Dono, dados["dono_id"])
    if dono is None:
        return jsonify({"erro": "Dono nao encontrado"}), 404

    novo_pet = Pet(
        nome=dados["nome"],
        especie=dados["especie"],
        idade=dados["idade"],
        dono_id=dados["dono_id"]
    )

    db.session.add(novo_pet)
    db.session.commit()

    return jsonify(novo_pet.to_dict()), 201


@app.route("/pets/<int:id>", methods=["PUT"])
def atualizar_pet(id):
    dados = request.get_json()

    if not dados or not all(
        campo in dados for campo in ["nome", "especie", "idade", "dono_id"]
    ):
        return jsonify({
            "erro": "Informe nome, especie, idade e dono_id"
        }), 400

    pet = db.session.get(Pet, id)

    if pet is None:
        return jsonify({"erro": "Pet nao encontrado"}), 404

    # Verifica se o dono_id informado existe
    dono = db.session.get(Dono, dados["dono_id"])
    if dono is None:
        return jsonify({"erro": "Dono nao encontrado"}), 404

    pet.nome = dados["nome"]
    pet.especie = dados["especie"]
    pet.idade = dados["idade"]
    pet.dono_id = dados["dono_id"]

    db.session.commit()

    return jsonify(pet.to_dict())


@app.route("/pets/<int:id>", methods=["DELETE"])
def remover_pet(id):
    pet = db.session.get(Pet, id)

    if pet is None:
        return jsonify({"erro": "Pet nao encontrado"}), 404

    db.session.delete(pet)
    db.session.commit()

    return jsonify({
        "mensagem": "Pet removido com sucesso"
    })


if __name__ == "__main__":
    app.run(debug=True)
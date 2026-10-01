from app import app, db, Dono, Pet

with app.app_context():
    # Cria todas as tabelas (donos e pets) se elas não existirem
    db.create_all()

    # Só insere os dados de exemplo se o banco estiver vazio
    if Dono.query.first() is None:
        # 1. Instanciando os donos
        ana = Dono(nome="Ana Paula Ribeiro", telefone="45999110001")
        bruno = Dono(nome="Bruno Cardoso", telefone="45999110002")
        carla = Dono(nome="Carla Meneghel", telefone="45999110003")

        # Adiciona os donos na sessão e salva no banco
        db.session.add_all([ana, bruno, carla])
        db.session.commit()

        # 2. Instanciando os pets vinculados aos IDs dos donos
        rex = Pet(nome="Rex", especie="cachorro", idade=4, dono_id=ana.id)
        mimi = Pet(nome="Mimi", especie="gato", idade=2, dono_id=ana.id)
        thor = Pet(nome="Thor", especie="cachorro", idade=7, dono_id=bruno.id)
        nina = Pet(nome="Nina", especie="gato", idade=1, dono_id=carla.id)
        pingo = Pet(nome="Pingo", especie="passaro", idade=3, dono_id=carla.id)

        # Adiciona os pets na sessão e salva no banco
        db.session.add_all([rex, mimi, thor, nina, pingo])
        db.session.commit()

        print("Banco criado com sucesso via ORM!")
        print("Foram inseridos 3 donos e 5 pets.")
    else:
        print("O banco de dados já contém registros.")
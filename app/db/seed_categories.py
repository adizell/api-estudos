# app/db/seed_pet_categories.py

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from decouple import config
from slugify import slugify
from app.db.base import Base
from app.db.models.pet_category_model import (
    PetCategoryEnvironment,
    PetCategoryCondition,
    PetCategoryPurpose,
    PetCategoryHabitat,
    PetCategoryOrigin,
    PetCategorySize,
    PetCategoryAge,
)

# Configurações do banco
test_mode = config("TEST_MODE", default=False, cast=bool)
db_url = config("DB_URL_TEST") if test_mode else config("DB_URL")
engine = create_engine(db_url)
SessionLocal = sessionmaker(bind=engine)

# Categorias por tipo
seed_data = {
    PetCategoryEnvironment: ["Doméstico", "Rural", "Silvestre"],
    PetCategoryCondition: ["Perdido", "Saudável", "Resgatado", "Deficiente", "Em tratamento"],
    PetCategoryPurpose: ["Companhia", "Guarda", "Guia", "Caça", "Trabalho", "Reprodução", "Competição"],
    PetCategoryHabitat: ["Terrestre", "Aquático", "Floresta", "Savana", "Montanha"],
    PetCategoryOrigin: ["Adotado", "Comprado", "Nativo", "Exótico", "Importado"],
    PetCategorySize: ["Pequeno", "Médio", "Grande", "Gigante"],
    PetCategoryAge: ["Filhote", "Jovem", "Adulto", "Idoso"]
}


def run_seed():
    session = SessionLocal()
    try:
        for model, items in seed_data.items():
            for name in items:
                exists = session.query(model).filter_by(name=name).first()
                if exists:
                    print(f"🟡 {model.__tablename__}: '{name}' já existe.")
                else:
                    obj = model(name=name, slug=slugify(name))
                    session.add(obj)
                    print(f"🟢 {model.__tablename__}: '{name}' criada.")
        session.commit()
        print("\n✅ Seed de categorias executado com sucesso.")
    except Exception as e:
        session.rollback()
        print(f"🔴 Erro ao executar seed: {e}")
    finally:
        session.close()


if __name__ == "__main__":
    run_seed()

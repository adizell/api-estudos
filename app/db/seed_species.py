# app/db/seed_species.py

from slugify import slugify
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from decouple import config

from app.db.models.specie_model import Specie
from app.db.base import Base

# Configuração do banco
TEST_MODE = config("TEST_MODE", default=False, cast=bool)
DB_URL = config("DB_URL_TEST") if TEST_MODE else config("DB_URL")
engine = create_engine(DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Espécies padrão com status
# Formato: (nome, status_ativo)
default_species = [
    ("Cachorro", True),
    ("Gato", True),
    ("Ave", True),
    ("Peixe", True),
    ("Coelho", True),
    ("Réptil", True),
    ("Anfíbio", True),
    ("Outro", True)
]


def run_specie_seed():
    session = SessionLocal()
    try:
        for specie_data in default_species:
            name, is_active = specie_data
            slug = slugify(name)
            existing = session.query(Specie).filter_by(slug=slug).first()

            if existing:
                # Atualiza o status se a espécie já existir
                if existing.is_active != is_active:
                    existing.is_active = is_active
                    status_text = "ativada" if is_active else "desativada"
                    print(f"🔄 Espécie '{name}' atualizada: {status_text}")
                else:
                    print(f"🟡 Espécie '{name}' já cadastrada (slug: {slug})")
            else:
                # Cria nova espécie com o status especificado
                specie = Specie(name=name, slug=slug, is_active=is_active)
                session.add(specie)
                status_text = "ativa" if is_active else "inativa"
                print(f"🟢 Espécie '{name}' adicionada com sucesso (slug: {slug}, status: {status_text})")

        session.commit()
        print("✅ Seed de espécies concluído com sucesso")
    except Exception as e:
        session.rollback()
        print(f"🔴 Erro ao cadastrar espécies: {e}")
    finally:
        session.close()


if __name__ == "__main__":
    run_specie_seed()

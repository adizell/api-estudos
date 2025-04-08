# app/db/connection.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import SQLAlchemyError
import logging

from app.core.config import settings

# Configurar logging
logger = logging.getLogger(__name__)

try:
    # Usa URL apropriada de acordo com o modo de teste
    database_url = str(settings.DB_URL_TEST if settings.TEST_MODE else settings.DATABASE_URL)

    # Cria o engine com configurações robustas de pool
    engine = create_engine(
        database_url,
        pool_pre_ping=True,  # Verificação automática de conexões quebradas
        pool_size=20,  # Número de conexões no pool
        max_overflow=5,  # Número extra de conexões além do pool
        pool_timeout=30,  # Tempo máximo para esperar por uma conexão disponível
    )

    # Session configurada com scoped_session para segurança em múltiplas threads
    Session = scoped_session(
        sessionmaker(
            autocommit=False,  # Não confirma automaticamente as transações
            autoflush=False,  # Não realiza flush automaticamente em cada query
            bind=engine,  # Define a conexão (engine) utilizada nas sessões
        )
    )

    logger.info(f"Conexão com o banco de dados estabelecida com sucesso")

except SQLAlchemyError as e:
    logger.error(f"Erro ao conectar ao banco de dados: {str(e)}")
    raise

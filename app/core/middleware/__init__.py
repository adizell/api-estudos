# Passo 1: Criar estrutura de arquivos correta:

# app/core/middleware/__init__.py
from app.core.middleware.exception_middleware import ExceptionMiddleware
from app.core.middleware.logging_middleware import RequestLoggingMiddleware
from app.core.middleware.csrf_middleware import CSRFProtectionMiddleware
from app.core.middleware.rate_limiting_middleware import RateLimitingMiddleware
from app.core.middleware.security_headers_middleware import SecurityHeadersMiddleware

# Exportar todos para facilitar importações
__all__ = [
    "ExceptionMiddleware",
    "RequestLoggingMiddleware",
    "CSRFProtectionMiddleware",
    "RateLimitingMiddleware",
    "SecurityHeadersMiddleware"
]

# app/core/middleware/exception_middleware.py
# Movido do atual arquivo exceptions.py
# Manter apenas o middleware, mover as definições de exceção para exceptions.py

# app/core/middleware/logging_middleware.py
# Movido do atual arquivo exceptions.py (contendo RequestLoggingMiddleware)

# app/core/middleware/csrf_middleware.py
# Renomear o arquivo csrf.py para csrf_middleware.py

# app/core/middleware/rate_limiting_middleware.py
# Renomear o arquivo rate_limiting.py para rate_limiting_middleware.py 

# app/core/middleware/security_headers_middleware.py
# Renomear o arquivo security_headers.py para security_headers_middleware.py
# Remover o arquivo security_headers_bkp

# app/core/exceptions.py
# Mover todas as definições de exceção que atualmente estão em app/core/middleware/logging.py para cá
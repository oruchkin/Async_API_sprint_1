import os

PROD_MODE = os.getenv('PROD_MODE').lower() in ('true', '1', 't', 'y', 'yes')

base_path = "functional.fixtures" if PROD_MODE else "src.fixtures"

pytest_plugins = [
    f"{base_path}.redis_fixtures",
    f"{base_path}.elasticsearch_fixtures",
    f"{base_path}.http_fixtures",
]

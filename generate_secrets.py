import secrets

# Gera uma chave secreta segura
secret_key = secrets.token_hex(32)
print(f"Sua chave secreta: {secret_key}")

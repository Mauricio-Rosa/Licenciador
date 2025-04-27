from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

# Gerar chave privada RSA (2048 bits)
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048
)

# Derivar a chave pública
public_key = private_key.public_key()

# Salvar a chave privada em um arquivo PEM
with open("chave_privada.pem", "wb") as f:
    f.write(private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ))

# Salvar a chave pública em um arquivo PEM
with open("chave_publica.pem", "wb") as f:
    f.write(public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ))

print("✅ Chaves RSA geradas com sucesso!")

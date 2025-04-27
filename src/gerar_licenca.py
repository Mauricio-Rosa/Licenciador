# gerar_licenca.py
import json
import base64
from datetime import datetime, timedelta
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

# Carregar a chave privada
with open("chave_privada.pem", "rb") as f:
    private_key = serialization.load_pem_private_key(f.read(), password=None)

# Dados da licença
licenca = {
    "cliente": "Empresa XYZ",
    "validade": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
}
licenca_str = json.dumps(licenca)

# Assinar a licença
assinatura = private_key.sign(
    licenca_str.encode(),
    padding.PSS(
        mgf=padding.MGF1(hashes.SHA256()),
        salt_length=padding.PSS.MAX_LENGTH
    ),
    hashes.SHA256()
)

# Gerar licença final (com assinatura)
pacote = {
    "licenca": licenca,
    "assinatura": base64.b64encode(assinatura).decode()
}

# Salvar em um arquivo
with open("licenca.lic", "w") as f:
    json.dump(pacote, f)

print("Licença gerada com sucesso!")

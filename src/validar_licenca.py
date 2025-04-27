import os
import json
import base64
from datetime import datetime
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

def validar_licenca(caminho_licenca: str, caminho_chave_publica: str) -> bool:
    """
    Valida a licença do software verificando assinatura e data de validade.

    Args:
        caminho_licenca (str): Caminho para o arquivo de licença
        caminho_chave_publica (str): Caminho para a chave pública

    Returns:
        bool: True se a licença for válida, False caso contrário
    """
    try:
        # Carrega a chave pública
        with open(os.path.abspath(caminho_chave_publica), "rb") as f:
            public_key = serialization.load_pem_public_key(f.read())

        # Lê o arquivo da licença
        with open(os.path.abspath(caminho_licenca), "r") as f:
            pacote = json.load(f)

        # Extrai conteúdo e assinatura
        licenca_str = json.dumps(pacote["licenca"])
        assinatura = base64.b64decode(pacote["assinatura"])

        # Verifica a assinatura
        public_key.verify(
            assinatura,
            licenca_str.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

        # Verifica a data de validade
        data_atual = datetime.now()
        data_expiracao = datetime.strptime(pacote["licenca"]["validade"], "%Y-%m-%d")
        print("✅ Licença válida.")
        return data_atual <= data_expiracao

    except Exception as e:
        print(f"❌ Erro na validação da licença: {e}")
        return False

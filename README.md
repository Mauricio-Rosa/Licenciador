# 🔐 Sistema de Licenciamento de Software

## 📝 Descrição

Um sistema robusto de geração e validação de licenças para proteger aplicativos, utilizando criptografia RSA para assinatura digital.

## ✨ Recursos Principais

- Geração de chaves RSA
- Criação de licenças com validade temporária
- Validação de assinatura digital
- Proteção contra adulteração de licenças

## 🛠 Componentes do Sistema

### Arquivos Principais

| Arquivo                | Função                                         | Detalhes Técnicos                                                                                                    |
| ---------------------- | ------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------- |
| `gerar_chaves.py`    | Gera par de chaves RSA                           | - Chave de 2048 bits `<br>`- Usa algoritmo RSA `<br>`- Exporta chaves em formato PEM                              |
| `gerar_licenca.py`   | Cria licença assinada digitalmente              | - Assina licença com chave privada `<br>`- Gera licença com validade de 30 dias `<br>`- Serializa dados em JSON |
| `validar_licenca.py` | Valida licença gerada                           | - Verifica assinatura digital `<br>`- Checa data de validade `<br>`- Retorna booleano de validação              |
| `licenca.lic`        | Arquivo de licença com dados e assinatura       | - Contém dados do cliente `<br>`- Inclui assinatura digital                                                        |
| `chave_privada.pem`  | Chave para geração de licenças (CONFIDENCIAL) | - Chave privada RSA `<br>`- Deve ser mantida em segredo                                                             |
| `chave_publica.pem`  | Chave para validação de licenças              | - Chave pública correspondente `<br>`- Pode ser distribuída                                                       |

## 🚀 Instalação e Uso

### Gerenciador de Dependências UV

#### 📦 Sobre o UV

Este projeto utiliza o UV, um gerenciador de dependências e ambiente virtual extremamente rápido para Python. O UV oferece:

- Instalação ultra-rápida de dependências
- Resolução eficiente de pacotes
- Criação e gerenciamento de ambientes virtuais

#### 🛠 Comandos Principais do UV

| Comando                                | Descrição                                |
| -------------------------------------- | ------------------------------------------ |
| `uv venv`                            | Cria um novo ambiente virtual              |
| `uv pip install -r requirements.txt` | Instala dependências do projeto           |
| `uv pip freeze`                      | Lista pacotes instalados no ambiente atual |
| `uv pip install <pacote>`            | Instala um pacote específico              |

#### 📋 Preparando o Ambiente

```bash
# Criar ambiente virtual
uv venv

# Ativar ambiente virtual
# No Windows
.venv\Scripts\activate

# No Linux/macOS
source .venv/bin/activate

# Instalar dependências
uv pip install -r requirements.txt
```

### Pré-requisitos

- Python 3.13 ou superior
- UV (Instalável via `pip install uv`)
- Biblioteca `cryptography`

### Passos de Configuração

1. Instale a dependência:

   ```bash
   pip install cryptography
   ```
2. Gere o par de chaves:

   ```bash
   python gerar_chaves.py
   ```
3. Crie uma licença:

   ```bash
   python gerar_licenca.py
   ```
4. Valide a licença:

   ```bash
   python validar_licenca.py
   ```

## 🔒 Segurança

### Chave Privada

- **Função**: Assinar digitalmente as licenças
- **Características**:
  - Garante autenticidade
  - Comprova integridade dos dados
  - **NUNCA** deve ser compartilhada

### Chave Pública

- **Função**: Validar licenças no aplicativo cliente
- **Características**:
  - Pode ser distribuída
  - Não permite geração de novas licenças
  - Verifica assinatura e validade

## ⚠️ Boas Práticas

- Mantenha a chave privada em local seguro
- Distribua apenas a chave pública
- Proteja o processo de geração de licenças

## 📄 Fluxo de Licenciamento

```
[ Gerador de Licenças ]
    Chave Privada 
        ↓
Assina Licença → Gera licenca.lic
        ↓
[ Aplicativo Cliente ]
    Chave Pública
        ↓
Valida Assinatura e Validade
```

## 🚫 Riscos

- Vazamento da chave privada permite geração de licenças falsas
- Licenças expiradas bloqueiam o uso do aplicativo

## 📋 Resumo de Arquivos

| Arquivo               | Destino       | Função             |
| --------------------- | ------------- | -------------------- |
| `chave_privada.pem` | Desenvolvedor | Gerar licenças      |
| `chave_publica.pem` | Cliente       | Validar licenças    |
| `licenca.lic`       | Cliente       | Autorização de uso |

## 📅 Última Atualização

Versão 0.1.0 - Data: 16/04/2025

## 📜 Licença

[Especifique aqui a licença do seu projeto]

## 🤝 Contribuições

[Diretrizes para contribuição, se aplicável]

## 🔧 Como inserir a licença no seu projeto

1. **Inclua os arquivos `chave_publica.pem` e `licenca.lic` no seu projeto.**

- Coloque em uma pasta protegida do lado do cliente (por exemplo: `./licenciamento/`).

2. **Adicione o código de validação no início do seu programa.**
   Exemplo:

```python
from validar_licenca import validar_licenca

if not validar_licenca("licenciamento/licenca.lic", "licenciamento/chave_publica.pem"):
    print("Licença inválida ou expirada. Encerrando o programa.")
    exit()
```

**Ajuste o `validar_licenca.py` para funcionar como módulo:**
Adicione essa função ao final do arquivo:

```
def validar_licenca(caminho_licenca, caminho_chave_publica):
    import json, base64
    from datetime import datetime
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import padding

    with open(caminho_chave_publica, "rb") as f:
        public_key = serialization.load_pem_public_key(f.read())

    with open(caminho_licenca, "r") as f:
        pacote = json.load(f)

    licenca_str = json.dumps(pacote["licenca"])
    assinatura = base64.b64decode(pacote["assinatura"])

    try:
        public_key.verify(
            assinatura,
            licenca_str.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

        validade = datetime.strptime(pacote["licenca"]["validade"], "%Y-%m-%d")
        return validade >= datetime.now()

    except Exception:
        return False

```

## Compilação

pyinstaller --onefile --windowed --add-data "chaves;chaves" --add-data "licencas;licencas" --add-data "logs;logs" --icon=icone.ico main.py

### Explicando:

icone.ico e main.py devem estar na raiz do projeto

* --onefile - compila tudo em um unico arquivo
* --windowed = Nao mostra o terminal ao executar o app pelo .exe
* --add-data - Adiciona as pastas necessarias parte do projeto
* --icon - adicione o icone do projeto

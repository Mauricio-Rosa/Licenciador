import os
import sys
import json
import base64
from datetime import datetime, timedelta
from typing import TYPE_CHECKING
import tkinter as tk
from tkinter import filedialog

# Adicionar o diretório src ao path para importações
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from src.backend.logger import logger

# Importações para geração de chaves e licenças
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

# Importação condicional para evitar erro de importação circular
if TYPE_CHECKING:
    from src.frontend.views.main_view import MainView

class LicenceController:
    """
    Controlador responsável pela lógica de geração de licenças.
    
    Attributes:
        view (MainView): Referência para a view principal.
    """
    
    def __init__(self, view):
        """
        Inicializa o controlador com a view principal.
        
        Args:
            view (MainView): View principal da aplicação.
        """
        self.view = view
    
    def gerar_licenca(self):
        """
        Método para gerar a licença com base nos dados inseridos.
        Valida os campos de entrada e gera o arquivo de licença.
        Permite ao usuário escolher onde salvar o arquivo de licença.
        """
        try:
            # Obter dados dos campos
            nome = self.view.entry_nome.get().strip()

            # Validar campos
            if not nome:
                raise ValueError("Nome do cliente é obrigatório")

            # Obter validade
            dias_validade = 30  # Padrão
            validade_input = self.view.entry_validade.get().strip()
            if validade_input:
                try:
                    dias_validade = int(validade_input)
                    if dias_validade <= 0:
                        raise ValueError("Validade deve ser um número positivo")
                except ValueError:
                    raise ValueError("Validade deve ser um número inteiro")

            # Gerar licença
            licenca = self._criar_licenca(nome, dias_validade)

            # Sugerir nome padrão para o arquivo
            nome_cliente = licenca['licenca']['cliente'].upper()
            data_atual = datetime.now().strftime('%Y%m%d_%H%M%S')
            nome_arquivo = f"{nome_cliente}_{data_atual}.lic"

            # Abrir janela para o usuário escolher onde salvar
            root = tk.Tk()
            root.withdraw()  # Não mostrar a janela principal
            caminho_salvar = filedialog.asksaveasfilename(
                defaultextension=".lic",
                filetypes=[("Arquivos de Licença", "*.lic"), ("Todos os arquivos", "*.*")],
                initialfile=nome_arquivo,
                title="Salvar licença como..."
            )
            root.destroy()

            if not caminho_salvar:
                self.view.atualizar_status("Operação de salvar cancelada pelo usuário.", sucesso=False)
                return

            # Salvar licença como JSON
            with open(caminho_salvar, 'w') as f:
                json.dump(licenca, f, indent=4)

            # Atualizar histórico de licenças normalmente
            self._atualizar_historico_licencas(caminho_salvar)

            # Atualizar status
            self.view.atualizar_status(f"Licença gerada com sucesso: {caminho_salvar}")

            # Registrar log
            logger.info(f"Licença gerada para {nome} com validade de {dias_validade} dias. Salva em {caminho_salvar}")

        except ValueError as e:
            # Tratar erros de validação
            self.view.atualizar_status(str(e), sucesso=False)
            logger.error(f"Erro na geração de licença: {e}")

        except Exception as e:
            # Tratar outros erros inesperados
            self.view.atualizar_status("Erro ao gerar licença", sucesso=False)
            logger.error(f"Erro inesperado na geração de licença: {e}")
    
    def gerar_chaves(self) -> tuple:
        """
        Gera um par de chaves RSA e permite ao usuário escolher onde salvar os arquivos.
        
        Returns:
            tuple: Caminhos para chave privada e pública.
        """
        try:
            # Gerar chave privada RSA
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048
            )
            public_key = private_key.public_key()

            # Abrir diálogo para salvar chave privada
            root = tk.Tk()
            root.withdraw()
            caminho_privada = filedialog.asksaveasfilename(
                defaultextension='.pem',
                filetypes=[('Chave Privada PEM', '*.pem'), ('Todos os arquivos', '*.*')],
                initialfile='chave_privada.pem',
                title='Salvar chave privada como...'
            )
            if not caminho_privada:
                self.view.atualizar_status("Operação de salvar chave privada cancelada pelo usuário.", sucesso=False)
                root.destroy()
                return None, None
            # Salvar chave privada
            with open(caminho_privada, 'wb') as f:
                f.write(private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                ))

            # Abrir diálogo para salvar chave pública
            caminho_publica = filedialog.asksaveasfilename(
                defaultextension='.pem',
                filetypes=[('Chave Pública PEM', '*.pem'), ('Todos os arquivos', '*.*')],
                initialfile='chave_publica.pem',
                title='Salvar chave pública como...'
            )
            if not caminho_publica:
                self.view.atualizar_status("Operação de salvar chave pública cancelada pelo usuário.", sucesso=False)
                root.destroy()
                return caminho_privada, None
            # Salvar chave pública
            with open(caminho_publica, 'wb') as f:
                f.write(public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                ))
            root.destroy()
            logger.info("Chaves RSA geradas com sucesso")
            return caminho_privada, caminho_publica
        except Exception as e:
            logger.error(f"Erro ao gerar chaves: {e}")
            raise
    
    def _criar_licenca(self, nome: str, dias_validade: int = 30) -> dict:
        """
        Cria uma licença assinada digitalmente.
        
        Args:
            nome (str): Nome do cliente.
            dias_validade (int, optional): Número de dias de validade. Padrão é 30.
        
        Returns:
            dict: Dicionário com detalhes da licença.
        """
        try:
            # Definir caminho para chave privada
            base_dir = os.path.join(
                os.path.dirname(__file__), 
                '..', '..', '..')
            dir_chaves = os.path.join(base_dir, 'chaves')
            caminho_privada = os.path.join(dir_chaves, 'chave_privada.pem')
            
            # Verificar se a chave existe, se não, gerar
            if not os.path.exists(caminho_privada):
                self.gerar_chaves()
            
            # Carregar chave privada
            with open(caminho_privada, 'rb') as f:
                private_key = serialization.load_pem_private_key(f.read(), password=None)
            
            # Calcular data de validade
            data_validade = (datetime.now() + timedelta(days=dias_validade)).strftime("%Y-%m-%d")
            
            # Dados da licença
            licenca = {
                "cliente": nome,
                "validade": data_validade
            }
            
            # Converter a licença em JSON
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
            
            # Empacotar licença + assinatura
            pacote = {
                "licenca": licenca,
                "assinatura": base64.b64encode(assinatura).decode()
            }
            
            return pacote
        
        except Exception as e:
            logger.error(f"Erro ao criar licença: {e}")
            raise
    
    def _salvar_licenca(self, licenca: dict) -> str:
        """
        Salva a licença em um arquivo .lic no diretório de licenças.
        
        Args:
            licenca (dict): Dicionário contendo os detalhes da licença.
        
        Returns:
            str: Caminho completo do arquivo de licença salvo.
        """
        try:
            # Definir caminho base para licenças
            base_dir = os.path.join(
                os.path.dirname(__file__), 
                '..', '..', '..')
            dir_licencas = os.path.join(base_dir, 'licencas')
            
            # Criar diretório se não existir
            os.makedirs(dir_licencas, exist_ok=True)
            
            # Nome do arquivo baseado no nome do cliente
            nome_cliente = licenca['licenca']['cliente'].upper()
            data_atual = datetime.now().strftime('%Y%m%d_%H%M%S')
            caminho_licenca = os.path.join(dir_licencas, f"{nome_cliente}_{data_atual}.lic")
            
            # Salvar licença como JSON
            with open(caminho_licenca, 'w') as f:
                json.dump(licenca, f, indent=4)
            
            # Atualizar histórico de licenças
            self._atualizar_historico_licencas(caminho_licenca)
            
            return caminho_licenca
        
        except Exception as e:
            logger.error(f"Erro ao salvar licença: {e}")
            raise
    
    def _atualizar_historico_licencas(self, novo_arquivo: str):
        """
        Atualiza o histórico de licenças, mantendo apenas os 5 arquivos mais recentes.
        
        Args:
            novo_arquivo (str): Caminho do novo arquivo de licença.
        """
        try:
            base_dir = os.path.join(
                os.path.dirname(__file__), 
                '..', '..', '..')
            dir_licencas = os.path.join(base_dir, 'licencas')
            
            # Listar todos os arquivos .lic
            arquivos_licenca = [f for f in os.listdir(dir_licencas) if f.endswith('.lic')]
            
            # Ordenar por data de modificação (mais recentes primeiro)
            arquivos_licenca.sort(
                key=lambda x: os.path.getmtime(os.path.join(dir_licencas, x)), 
                reverse=True
            )
            
            # Manter apenas os 5 arquivos mais recentes
            for arquivo in arquivos_licenca[5:]:
                caminho_arquivo = os.path.join(dir_licencas, arquivo)
                os.remove(caminho_arquivo)
                logger.info(f"Removido arquivo antigo de licença: {arquivo}")
        
        except Exception as e:
            logger.error(f"Erro ao atualizar histórico de licenças: {e}")
    
    def listar_licencas(self):
        """
        Lista os arquivos de licença disponíveis.
        
        Returns:
            list: Lista de caminhos de arquivos de licença.
        """
        try:
            base_dir = os.path.join(
                os.path.dirname(__file__), 
                '..', '..', '..')
            dir_licencas = os.path.join(base_dir, 'licencas')
            
            # Listar todos os arquivos .lic
            arquivos_licenca = [os.path.join(dir_licencas, f) for f in os.listdir(dir_licencas) if f.endswith('.lic')]
            
            # Ordenar por data de modificação (mais recentes primeiro)
            arquivos_licenca.sort(
                key=lambda x: os.path.getmtime(x), 
                reverse=True
            )
            
            return arquivos_licenca
        
        except Exception as e:
            logger.error(f"Erro ao listar licenças: {e}")
            return []

import customtkinter as ctk
import os
import sys
from PIL import Image, ImageTk

# Adicionar o diretório src ao path para importações
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from src.backend.logger import logger
from src.frontend.controllers.licence_controller import LicenceController

class MainView(ctk.CTk):
    """
    Classe principal da interface gráfica para geração de licenças.
    
    Attributes:
        controller (LicenceController): Controlador para lógica de geração de licenças.
    """
    
    def __init__(self):
        """
        Inicializa a janela principal da aplicação.
        """
        super().__init__()
        
        # Configurações da janela
        self.title("Gerador de Licenças")
        self.geometry("600x500")

        # Adicionar ícone do app
        try:
            
            icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'assets', 'icone.png'))
            if os.path.exists(icon_path):
                # Converter PNG para PhotoImage
                img = Image.open(icon_path)
                icon = ImageTk.PhotoImage(img)
                self.iconphoto(False, icon)
                self._icon_img_ref = icon  # Referência para não ser coletado pelo GC
        except Exception as e:
            print(f"[AVISO] Não foi possível definir o ícone: {e}")

        # Configurar tema
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")
        
        # Inicializar controlador
        self.controller = LicenceController(self)
        
        # Criar interface
        self._criar_interface()
        
        # Registrar log de inicialização
        logger.info("Aplicação iniciada")
    
    def _criar_interface(self):
        """
        Cria os elementos da interface gráfica.
        """
        # Frame principal
        self.frame_principal = ctk.CTkFrame(self)
        self.frame_principal.pack(pady=20, padx=20, fill="both", expand=True)
        
        # Título
        self.label_titulo = ctk.CTkLabel(
            self.frame_principal, 
            text="Gerador de Licenças", 
            font=("Roboto", 24)
        )
        self.label_titulo.pack(pady=20)
        
        # Campos de entrada
        self._criar_campos_entrada()
        
        # Botões
        self._criar_botoes()
    
    def _criar_campos_entrada(self):
        """
        Cria os campos de entrada para informações da licença.
        """
        # Nome do cliente
        self.label_nome = ctk.CTkLabel(self.frame_principal, text="Nome do Cliente:")
        self.label_nome.pack(pady=(10, 5), anchor="w", padx=20)
        self.entry_nome = ctk.CTkEntry(self.frame_principal, width=400)
        self.entry_nome.pack(pady=(0, 10), padx=20)
        
        # Validade da licença
        self.label_validade = ctk.CTkLabel(self.frame_principal, text="Validade da Licença (dias):")
        self.label_validade.pack(pady=(10, 5), anchor="w", padx=20)
        self.entry_validade = ctk.CTkEntry(self.frame_principal, width=400, placeholder_text="Padrão: 30 dias")
        self.entry_validade.pack(pady=(0, 10), padx=20)
    
    def _criar_botoes(self):
        """
        Cria os botões de ação da interface.
        """
        # Botão para gerar chaves
        self.botao_gerar_chaves = ctk.CTkButton(
            self.frame_principal, 
            text="Gerar Chaves", 
            command=self._gerar_chaves
        )
        self.botao_gerar_chaves.pack(pady=10, padx=20, fill="x")
        
        # Botão para gerar licença
        self.botao_gerar_licenca = ctk.CTkButton(
            self.frame_principal, 
            text="Gerar Licença", 
            command=self.controller.gerar_licenca
        )
        self.botao_gerar_licenca.pack(pady=10, padx=20, fill="x")
        
        # Botão para listar licenças
        self.botao_listar_licencas = ctk.CTkButton(
            self.frame_principal, 
            text="Listar Licenças", 
            command=self._listar_licencas
        )
        self.botao_listar_licencas.pack(pady=10, padx=20, fill="x")
        
        # Label para status
        self.label_status = ctk.CTkLabel(
            self.frame_principal, 
            text="", 
            text_color="green"
        )
        self.label_status.pack(pady=10, padx=20)
    
    def _listar_licencas(self):
        """
        Lista as licenças geradas.
        """
        try:
            licencas = self.controller.listar_licencas()
            if not licencas:
                self.atualizar_status("Nenhuma licença encontrada", sucesso=False)
                return
            
            # Criar janela para mostrar licenças
            janela_licencas = ctk.CTkToplevel(self)
            janela_licencas.title("Licenças Geradas")
            janela_licencas.geometry("600x400")
            
            # Criar lista de licenças
            lista_licencas = ctk.CTkTextbox(janela_licencas, width=550, height=350)
            lista_licencas.pack(padx=10, pady=10)
            
            # Adicionar licenças à lista
            for licenca in licencas:
                lista_licencas.insert("end", f"{licenca}\n")
            
            lista_licencas.configure(state="disabled")
        
        except Exception as e:
            self.atualizar_status(f"Erro ao listar licenças: {e}", sucesso=False)
    
    def _gerar_chaves(self):
        """
        Chama o método de geração de chaves do controlador.
        """
        try:
            chave_privada, chave_publica = self.controller.gerar_chaves()
            self.atualizar_status(f"Chaves geradas com sucesso:\nPrivada: {chave_privada}\nPública: {chave_publica}")
        except Exception as e:
            self.atualizar_status(str(e), sucesso=False)
    
    def atualizar_status(self, mensagem: str, sucesso: bool = True):
        """
        Atualiza a mensagem de status na interface.
        
        Args:
            mensagem (str): Mensagem a ser exibida.
            sucesso (bool, optional): Indica se a mensagem é de sucesso. Defaults to True.
        """
        cor = "green" if sucesso else "red"
        self.label_status.configure(text=mensagem, text_color=cor)
        logger.info(f"Status atualizado: {mensagem}")

def main():
    """
    Função principal para iniciar a aplicação.
    """
    app = MainView()
    app.mainloop()

if __name__ == "__main__":
    main()

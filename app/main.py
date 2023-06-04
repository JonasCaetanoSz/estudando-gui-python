from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.QtCore import QUrl, pyqtSignal, QObject
from PyQt5.QtCore import QCoreApplication
from prospex import Prospex
from tkinter import messagebox
from PyQt5.QtGui import QIcon
import threading
import requests
import time
import sys
import api

class SignalHandler(QObject):
    resize_signal = pyqtSignal(int, int)
    set_size = pyqtSignal(int, int)
    get_page = pyqtSignal(QUrl)
    start_account_create = pyqtSignal(dict, list, list)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.LOCAL_WEBSITE_URL = "http://127.0.0.1:7845"
        self.setMaximumSize(520, 590)
        self.resize(520, 590)
        self.setWindowTitle("prospex.com - Criar Multiplas Contas")
        self.setWindowIcon(QIcon("icons/prospex.ico"))
        self.webview = QWebEngineView()
        self.setCentralWidget(self.webview)
        self.webview.load(QUrl(self.LOCAL_WEBSITE_URL))
        self.accounts = []

        # desativa algumas ações na pagina

        page = self.webview.page()
        page.action(QWebEnginePage.Back).setVisible(False)
        page.action(QWebEnginePage.Forward).setVisible(False)
        page.action(QWebEnginePage.Reload).setVisible(False)
        page.action(QWebEnginePage.WebAction.SavePage).setVisible(False)
        page.action(QWebEnginePage.WebAction.CopyImageToClipboard).setVisible(False)
        page.action(QWebEnginePage.WebAction.CopyImageUrlToClipboard).setVisible(False)


        # recebe sinal para mudar de pagina ou mudar o tamanho da mesma e também iniciar a criação de contas

        self.signal_handler = SignalHandler()
        self.signal_handler.resize_signal.connect(self.setMaximumSize)
        self.signal_handler.set_size.connect(self.set_window_size)
        self.signal_handler.get_page.connect(self.webview.load)
        self.signal_handler.start_account_create.connect(self.call_manage_account_creating)

        threading.Thread(target=lambda: api.api(self.signal_handler), daemon=True).start()

    def set_window_size(self, width, height):
        self.resize(width, height)
        
    # confirmar fechamento do programa
    
    def closeEvent(self, event):

        if len(self.accounts) >=1:

            reply = QMessageBox.question(
                self,
                "deseja cancelar a operação:",
                f"se você fechar o programa agora, apenas {len(self.accounts)} serão salvar, deseja realmente continuar?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                self.prospex.created_accounts = self.accounts.copy()
                path  = self.prospex.save_dataframe() if self.configs["formato"] == "xlsx" else self.prospex.save_html()
                self.accounts = []
                messagebox.showinfo(
                "contas criadas com sucesso",
                f"contas criadas com sucesso, os dados de todas as contas criadas pode ser encontrado em: {path}")
                event.accept()
            else:
                event.ignore()

    # coloca a função que gerencia a criação de contas em uma theard para não trava a interace

    def call_manage_account_creating(self, configs:dict, logs:list, finish:list):
        threading.Thread(target=lambda: self.manage_account_creating(configs=configs, logs=logs, finish=finish), daemon=True).start()
    
    # gerenciar a criação de contas

    def manage_account_creating(self, configs:dict, logs:list, finish:list):

        self.prospex = Prospex(configs=configs, logs=logs)
        self.configs = configs.copy()
        for i in range(0, int(configs["numeroContas"])):
            try:
                if i >= 1:
                    self.prospex.write_log(message="aguardando fim do intervalo")
                    time.sleep(1)
                
                self.prospex.write_log(message=f"\ngerando conta n° {(i + 1)}")
                account = self.prospex.create_account()
                self.accounts.append(account)
                

            except Exception as e:
                print(e)
                self.prospex.write_log(message="erro ao criar conta")
        
        if len(self.accounts) >= 1:
            self.prospex.created_accounts = self.accounts.copy()
            path = self.prospex.save_dataframe() if configs["formato"] == "xlsx" else self.prospex.save_html()
            self.prospex.write_log(message="", finish=True)
            messagebox.showinfo(
                "contas criadas com sucesso",
                f"contas criadas com sucesso, os dados de todas as contas criadas pode ser encontrado em: {path}")
        else:
            self.prospex.write_log(message="", finish=True)
            messagebox.showwarning(
                "erro ao criar contas",
                f"não consegui gerar nenhuma conta. caso você acredite que seja um erro aplicação, por favor entre em contato com o desenvolvedor.") 
        self.accounts = []
    

if __name__ == "__main__":

    try:
        response = requests.get(url="http://127.0.0.1:7845")
        messagebox.showerror(title="erro ao iniciar a aplicação", message="não foi possivel iniciar a aplicação pois existe outra instancia em execução.")
    except:
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec_())
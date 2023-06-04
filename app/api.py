from tkinter import messagebox
from PyQt5.QtCore import QUrl
import traceback
import tempfile
import logging
import flask
import json
import sys

logs = []
finish = [False]

def api(signal_handler):
    try:
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
        #sys.stdout = temp_file
        app = flask.Flask(import_name=__name__, static_url_path="/assets")
        app.template_folder = "pages"
        app.static_folder = "pages/assets"
        
        #logging.getLogger('werkzeug').setLevel(logging.CRITICAL)
        #logging.getLogger('werkzeug').setLevel(sys.maxsize)

        # pagina inicial

        @app.route("/", methods=["GET"])
        def index():
            signal_handler.resize_signal.emit(520, 590)
            signal_handler.set_size.emit(520, 590)
            return flask.render_template("index.html")
        
        # pagina que mostre o status da criação
        
        @app.route("/creating", methods=["GET"])
        def creating():
            signal_handler.resize_signal.emit(400, 550)
            signal_handler.set_size.emit(400, 550)
            return flask.render_template("creating.html")
        
        # rota para obter as configurações atuais do usuario

        @app.route(rule="/api/initial-data",  methods=["GET"])
        def initial_data():
            with open(file="configs.json", mode="r", encoding="utf8") as configs_file:
                return json.load(configs_file)
        
        # rota para iniciar a criação de de contas

        @app.route(rule="/api/start",  methods=["POST"])
        def start():
            email = flask.request.json["email"]
            pasw = flask.request.json["senha"]
            alias = flask.request.json["alias"]
            formato = flask.request.json["formato"]
            random_headers = flask.request.json["headersAleatorios"]
            use_proxy = flask.request.json["usarProxys"]
            
            if not email or not "@gmail.com" in email.lower():
                messagebox.showerror(title="email invalido", message="o email inserido não é valido, lembre-se, apenas emails do google serão aceitos.")
                return flask.jsonify(success=False), 422
            
            if not pasw or len(pasw) < 8:
                messagebox.showerror(title="senha invalida", message="a senha inserida não é valida, lembre-se, a senha necessaria é a senha de app.")
                return flask.jsonify(success=False), 422
            
            if not alias or not alias.isnumeric():
                messagebox.showerror(title="alias invalido", message=f"o alias inserido não é numerico ou é nulo, por favor corrija essa informação para proseguir.")
                return flask.jsonify(success=False), 422
            signal_handler.get_page.emit(QUrl("http://127.0.0.1:7845/creating"))
            user_json = flask.request.json
            signal_handler.start_account_create.emit(user_json, logs, finish)
            return "", 200
        
        # end-point para obter informações/logs da criação de contas

        @app.route("/api/updates", methods=["GET", "POST"])
        def updates():

            if flask.request.method.upper() == "GET":

                try: message = logs.pop(0)
                except Exception as e:  message = ""
                return flask.jsonify(log=message, finish=reset_globals_var() )
            
            logs.append(flask.request.json["message"])
            finish[0] = flask.request.json["finish"]
        
            return ""
        
        # reiniciar variveis globais apos fim da execução

        def reset_globals_var():
            if finish[0]:
                finish[0] = False
                logs = []
                return True
            return False 
        app.run(port=7845, use_evalex=False)
    
    except Exception as e:

        # Capturar o erro e salvar o traceback em um "arquivo de log"

        with open("errors.txt", "w") as log_file:
            traceback.print_exc(file=log_file)
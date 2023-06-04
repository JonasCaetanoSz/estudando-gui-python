from pydantic import BaseModel
from bs4 import BeautifulSoup
import request_base
import fake_headers
import requests
import openpyxl
import imaplib
import random
import email
import time
import json
import os

class Account(BaseModel):
    name:str
    email:str
    password:str
    key:str

class User(BaseModel):
    first_name:str
    last_name:str
    full_name:str
    password:str


class Prospex:
    def __init__(self, configs:dict, logs:list) -> None:
        self.VERSION = "20.05.2023"
        self.configs = configs
        self.logs = logs
        self.created_accounts = []
    
    # criar conta

    def create_account(self):
        
        data = request_base.data.copy()
        proxies = self.set_proxies()
        session = requests.session()
        if self.configs["headersAleatorios"]:
            session.get(
                url="https://prospex.com/app/signup/",
                headers=fake_headers.Headers().generate(),
                proxies=proxies
            )
        else:
            session.get(
                url="https://prospex.com/app/signup/",
                proxies=proxies
            )
        self.write_log(message="gerando dados da conta")
        session.headers.update(request_base.headers.copy())
        account_base_data = self.generate_user_ramdom_data()
        email = self.set_email()
        data.update({
            "name": account_base_data.full_name,
            "email": email,
            "password":account_base_data.password
        })
        self.write_log(message="criando conta")
        self.delete_old_emails()
        response = session.post(
            url="https://prospex.com/app/signup/",
            data=data,
            cookies=request_base.cookies,
            proxies=proxies
        )
        if not "<title>Select a Plan</title>" in response.text:
            raise requests.RequestException("a pagina não é selecione um plano")
        self.write_log(message="verificando conta")
        email_verify_url = self.get_email_confirmation_url()
        if not email_verify_url:
            raise requests.RequestException("o email de verificação não chegou")

        session.get(
            url=email_verify_url
            )
        self.write_log(message="obtendo chave da conta")
        if self.configs["headersAleatorios"]:
            response = session.get(
                url="https://prospex.com/app/dashboard/",
                headers=fake_headers.Headers().generate(),
                proxies=proxies
            )
        else:
            response = session.get(
                url="https://prospex.com/app/dashboard/",
                proxies=proxies
            )
        key = BeautifulSoup(response.text, "html.parser").find('span', {'style': 'text-transform: lowercase;'}).text
        self.write_log(message="conta criada")
        return Account(
            name=account_base_data.full_name,
            email=email,
            password=account_base_data.password,
            key=key
            )
    
    # salva os dados das contas criadas em um html
    

    def save_html(self) -> str:
        data = []
        for acc in self.created_accounts:
            data.append({
                "email": acc.email,
                "chave da conta": acc.key
            })

        if data:
            # Define o caminho da pasta "prospex" dentro da pasta "Documentos"
            documents_path = os.path.join(os.path.expanduser('~'), 'Documents')
            prospex_folder_path = os.path.join(documents_path, 'Prospex')

            if not os.path.exists(prospex_folder_path):
                os.mkdir(prospex_folder_path)
            file_name = "contas.html"
            path_file = os.path.join(prospex_folder_path, file_name)
            count = 0
            while os.path.exists(path_file):
                count += 1
                file_name = f"contas ({count}).html"
                path_file = os.path.join(prospex_folder_path, file_name)

            with open(path_file, 'w') as file:
                file.write('<html>\n<head>\n<style>\n')
                file.write('table { width: 100%; border-collapse: collapse; }\n')
                file.write('th, td { border: 1px solid black; padding: 8px; }\n')
                file.write('</style>\n</head>\n<body>\n')
                file.write('<table>\n<tr>\n<th>Email</th>\n<th>Chave da Conta</th>\n</tr>\n')
                for acc in data:
                    file.write(f'<tr>\n<td>{acc["email"]}</td>\n<td>{acc["chave da conta"]}</td>\n</tr>\n')
                file.write('</table>\n</body>\n</html>\n')

            self.created_accounts = []
            return path_file

    # salvar os dados das contas criadas em um dataframe

    def save_dataframe(self) -> str:
        
        data = []
        for acc in self.created_accounts:
            data.append({
                "email": acc.email,
                "chave da conta": acc.key
            })

        if data:
            
            # Define o caminho da pasta "prospex" dentro da pasta "Documentos"

            documents_path = os.path.join(os.path.expanduser('~'), 'Documents')
            prospex_folder_path = os.path.join(documents_path, 'prospectss')
            
            if not os.path.exists(prospex_folder_path):
                os.mkdir(prospex_folder_path)            
            file_name = "contas.xlsx"
            path_file = os.path.join(prospex_folder_path, file_name)
            count = 0
            while os.path.exists(path_file):
                count += 1
                file_name = f"contas ({count}).xlsx"
                path_file = os.path.join(prospex_folder_path, file_name)
            
            book = openpyxl.Workbook()
            sheet = book["Sheet"]
            sheet.title = "contas"
            sheet.append(["email", "chave da conta"])
            sheet.column_dimensions["A"].width = 33
            sheet.column_dimensions["B"].width = 28
            sheet.column_dimensions["C"].width = 28
            sheet["A1"].font = sheet["A1"].font.copy(bold=True)
            sheet["B1"].font = sheet["B1"].font.copy(bold=True)
            sheet["C1"].font = sheet["C1"].font.copy(bold=True)
            for acc in data:
                sheet.append([acc["email"], acc["chave da conta"]])
            book.save(path_file)
            self.created_accounts = []
            return path_file

    
    # trata proxies para ser usado pela biblioteca requests

    def check_proxie(self, proxy:str) -> str|None:
        proxy_dict = {
        "http": "",
        "https": "",
        "ftp": "",}
        try:
            ip, port, user, password = proxy.split(":")
            for protocol in proxy_dict:
                proxy_dict[protocol] = f"http://{user}:{password}@{ip}:{port}"
            return proxy_dict
        except:
            return {}


    # setar e configurar as proxies caso o usuario deseje usar

    def set_proxies(self) -> dict|None:
        if self.configs["usarProxys"]:
            proxies_path = os.getcwd() + "/proxies.txt"
            self.write_log(message="configurando proxies")
            if os.path.exists(path=proxies_path):
                with open(file=proxies_path, mode="r", encoding="utf8") as proxies_file:
                    proxies = [self.check_proxie(proxy=proxy) for proxy in proxies_file.readlines()]
                    proxies = [proxy for proxy in proxies if proxy]
                    proxy = None
                    if proxies:
                        rand = random.randint(0, len(proxies) - 1)
                        proxy = proxies[rand]
                        self.write_log(message="escolhido: " + proxy.copy()["http"].replace("http://", "").split("@")[1])
                    else:
                        self.write_log(message="nenhum proxie valido")
                    return proxy
            self.write_log(message="proxies não encontrado")
            return None
        
    # apaga os emails de verificação já recebidos

    def delete_old_emails(self):
        imap_host = 'imap.gmail.com'
        imap_user = self.configs["email"]
        imap_pass = self.configs["senha"]
        mail = imaplib.IMAP4_SSL(imap_host)
        mail.login(imap_user, imap_pass)
        mailbox_names = ['INBOX', '[Gmail]/Spam']
        for mailbox_name in mailbox_names:
            mail.select(mailbox_name)
            result, data = mail.uid('search', None, 'SUBJECT "Your pending 25 credits"')
            uids = data[0].split()
            for uid in uids:
                mail.uid('STORE', uid, '+FLAGS', '\\Deleted')
            mail.expunge()
        mail.logout()

    # pega o link de confirmação no email

    def get_email_confirmation_url(self):
        time.sleep(13) 
        imap_host = 'imap.gmail.com'
        imap_user = self.configs["email"]
        imap_pass = self.configs["senha"]

        mail = imaplib.IMAP4_SSL(imap_host)
        mail.login(imap_user, imap_pass)
        
        mailbox_names = ['INBOX', '[Gmail]/Spam'] 
        for mailbox_name in mailbox_names:
            mail.select(mailbox_name)
            data = mail.search(None, 'UNSEEN SUBJECT "pending 25 credits"')[1]
            for num in data[0].split():
                msg_data = mail.fetch(num, '(RFC822)')[1]
                msg_str = str(msg_data[0][1], 'utf-8')
                msg = email.message_from_string(msg_str)

                for part in msg.walk():
                    if part.get_content_type() == 'text/html':
                        body = part.get_payload(decode=True).decode()
                        if 'prospex.com/app/verify' in body:
                            start = body.find('https://prospex.com/app/verify')
                            end = body.find('"', start)
                            link = body[start:end]
                            mail.store(num, '+FLAGS', '\\Deleted')
                            mail.expunge()
                            mail.close()
                            mail.logout()
                            return link
        mail.close()
        mail.logout()
        return None

    # gerar dados para a conta

    def generate_user_ramdom_data(self) -> User:
        response = requests.get(
            url="https://random-data-api.com/api/users/random_user",
            headers=fake_headers.Headers().generate()
        ).json()
        return User(
            full_name=response["first_name"] + " " + response["last_name"],
            **response) 
    
    # setar o alias para o email

    def set_email(self) -> str:

        email:str = self.configs["email"].lower()
        next_alias:str = self.configs["alias"]
        symbol = "+" if next_alias else ""
        email = email.replace("@gmail.com", f"{symbol}{next_alias}@gmail.com")
        next_alias = str(int(next_alias) + 1) if next_alias.isnumeric() else "1"
        self.configs.update({"alias":next_alias})
        self.update_settings()
        return email
    
    # atualizar valores do JSON de configurações

    def update_settings(self) -> None:
        with open(file="configs.json", mode="w", encoding="utf8") as config_file:
            json.dump(obj=self.configs , fp=config_file, indent=4)
    
    # mandar atualizações para a instacia da API

    def write_log(self, message:str, finish:bool = False):
        e = requests.post(url="http://127.0.0.1:7845/api/updates", json={"message":message, "finish":finish})
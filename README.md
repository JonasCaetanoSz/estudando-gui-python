
# Estudando GUI com Python

Originalmente, o projeto tinha como objetivo criar várias contas em um site. No entanto, devido a atualizações no site, o programa não é mais capaz de criar contas. então Decidi tornar o repositório público.


## Instalação

Siga as instruções abaixo para configurar e executar o programa.

- Clone o repositório:


```bash
git clone https://github.com/JonasCaetanoSz/estudando-gui-python.git
```

- Crie e ative o ambiente virtual:


```bash
python3 -m venv .venv
```

```
source .venv/bin/activate # Linux / macOS
```

```
.venv\Scripts\activate  # Windows
```

- Instale as dependências:

```
cd app
python3 -m pip install -r requisitos.txt
```

- Inicie a aplicação:

```
python3 main.py
```
## Aprendizados

Após finalizar este projeto, fiz uma lista de pontos que eu melhoraria se o recriasse do zero hoje:

#### Sistema de Log

Isso, de fato, é o que eu mais desejo mudar. A forma atual, em resumo, funciona em 3 etapas:

- A API possui um endpoint que recebe uma requisição POST com uma nova mensagem e guarda essa mensagem em uma lista.

- O JavaScript na página do programa envia uma requisição GET para o mesmo endpoint mencionado acima, a cada 0 milissegundos.

- Caso haja alguma mensagem na lista, a API retorna a mensagem no índice zero da lista e a remove.

No entanto, isso poderia ser facilmente substituído por um websocket na página.

#### Flask

O que me incomoda um pouco aqui é que leva alguns segundos para que o Flask inicie, o que resulta em um atraso para a inicialização do programa, pois as duas páginas HTML são servidas e as configurações atuais lidas do arquivo JSON. Na minha máquina, ele leva cerca de 5 segundos para iniciar. O atraso na exibição da primeira página pode levar o usuário a tentar iniciar o programa várias vezes (clicando várias vezes no ícone do programa). Isso pode causar algum bug. Apesar de existir uma verificação no main.py do programa para detectar se já existe uma instância em execução (enviando uma requisição para a porta que seria usada pela API e, caso ocorra algum erro, perimite que o programa continue), como há um atraso na inicialização, se o usuário der vários cliques no ícone do programa, o Flask ainda estará iniciando e, portanto, o programa será iniciado novamente.  para resolver o problema do atraso , eu faria o Flask iniciar em uma nova thread após a entrega da primeira página do programa e faria com que o PyQt5 abrisse o webview diretamente do arquivo HTML. Como a página inicial depende da API para carregar as configurações atuais, eu desabilitaria todos os botões da página e exibiria um ícone de "carregando" até que a API inicie e responda.

#### PyQt5

A única questão que não gostei muito é que, ao gerar um executável com pyinstaller ou outros, o programa fica bem grande devido a alguns módulos do PyQt5 que nem é usado pelo programa. Eu testaria trocar o PyQt5 por pywebview para ver se o programa continuaria tão grande assim. Afinal, o programa é quase todo um webview e é mais leve do que usar Electron (JavaScript). O Electron funciona quase como um navegador, o que justifica o tamanho grande de um programa criado com ele. mas também sei que o PyQt5 é bem completo e vai além dos metodos que eu usei,então também faz sentindo ele ser grande.

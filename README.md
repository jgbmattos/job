O documento a seguir tem o objetivo de propor uma solução para o problema detalhado abaixo.
-
O problema consiste em três databases, **BASE A**, **BASE B** e **BASE C**. As três bases de dados tem diferentes necessidades, sendo elas:

- **BASE A**:
  - Deve possuir a mais alta segurança.
  - O acesso aos dados não precisa ser rapido.
- **BASE B**:
  - Deve possuir segurança.
  - O acesso aos dados deve ser mais rápido que o da BASE A.
- **BASE C**:
  - Não possui uma preocupação grande com segurança.
  - O acesso aos dados deve ser muito rapido.

A seguir serão discutidos três temas:
- **Arquitetura utilizada**
- **Tecnologias adotadas**
- **Dados armazenados**


# **Arquitetura**
A arquitetura básica do projeto consiste nos seguintes items:
- AWS API GATEWAY
  - O Gateway terá a função de direcionar as requisições para os devidos serviços, além de criptografar toda a comunicação implementando o protocolo HTTPS.
  - Utilizaria a funcionalidade de cache para aumentar o desempenho.
- Circuit Breaker*
  - Será utilizado o Hystrix como circuit breaker na fila de mensageria entre os microserviços e servidor de authenticação e autorização.
  - Nesse cenário ele também será usado para monitoramento desses recursos.
###### *Não ficou claro no problema se os micro serviços que acessarão esses sistemas vão precisar de uma comunicação assíncrona. Acredito que sim, se este for o caso, a comunicação entre os micro serviços deverá ser feita por um message broker. O Hystrix além de prevenir problemas adicionasse uma camada legal de monitoramento em toda a comunicação.
- Microserviço para base B e C, com o intuito de permitir escalar facilmente.
- Sistema para a base A, não necessáriamente precisaria ser um microserviço. As vezes um monolito numa situação dessa facilite o controle de segurança/acesso etc.

- **Sistema 1**:
  - Sistema deve ficar em um rede interna, atrás de um firewall. 
  - Utilizar além do HTTPS, autenticação mútua.
  - Escopos de autorização bem definidos e sempre temporários.
  
- **Sistema 2**:
  - Segurança, autorização e autenticação será garantida através do protocolo HTTPS + OAUTH 2.0.
  - Acesso temporário.
  - Utilizará um balancedor de carga e um cluster de servidores para poder escalar quando necessário.
  
- **Sistema 3**:
  - Utilizará um balancedor de carga e um cluster de servidores para poder escalar quando necessário.
  - Não utilizará Oauth 2.0 de forma a diminuir o payload de cada requisição, tornando a comunicação mais eficiente. Para garantir segurança enviar usuário e senha em cada requisicao.
  
Diagrama:
![Arquitetura microserviços](https://user-images.githubusercontent.com/10090364/57042620-99c1dc80-6c3b-11e9-8f0f-08916070b6f2.png)

# **Tecnologias adotadas**
- AWS API GATEWAY.
- AWS Load Balancer.
- Hystrix (Ciruit Breaker e monitoramento).
- Python.
  - FLASK. Utilizado nos testes desse documento. *
    - *Para uma solução oficional utilizaria AIOHTTP. Por ser assíncrono ele tende a performar quando temos requisições demoradas e/ou com muitas requisições simultâneas.
- Swagger. Para geração de API e documentação das mesmas (Não utilizado nesse projeto porém seria uma opção para um caso real).
- AWS MQ para mensageria entre os microserviços.

# **Dados armazenados**
- Para todos os sitemas armazenaria dados da ultima consulta. Data/Hora, IP, Usuário da última consulta.
- Para todos os sistemas eu armazenaria pelo menos o CPF, utilizaria esse dado como uma forma de PK entre os sistemas. Idealmente armazenaria também dados básicos de cadastro (CPF, Nome, Endereco, etc)
  - Embora seja uma repetição de dados, evita a requisição para outro micro serviço em cascata em alguns casos, como, por exemplo no serviço 2 aonde o objetivo é calcular o score. Tendo no sistema 2 os dados da pessoa posso chamar esse serviço isolado, sem precisar cascatear de outro serviço.
   
# **Disponibilização dos Dados**
Para disponibilizar os dados acredito que a combinação de aplicação WEB/API's Rest sejam suficientes.
Dados sensíveis devem ser disponibilizados mediante autenticação. 
Bancos e outras instituições acredito que teriam um interesse maior em acessar os dados por uma API diretamente. Nesse cenário um local no site para criação de CHAVES de acesso pode ser uma maneira interessante de criar um link de acesso com sistemas tercerios de forma segura.

Criaria os seguintes endpoints:
- **sistema 1**
  - [GET] /sistema1/pessoa_fisica
    - Filtros: 
      - CPF
      - Data_cadastro
      - Data_atualizacao
      - nome
      - ...
  - [GET] /sistema1/pessoa_fisica/< id>    
  - [POST] /sistema1/pessoa_fisica
    - Parâmetros :
      - Nome
      - cpf
      - nome da mae
      - nome do pai
      - ...
      - Endereco (objeto)
      - Lista de dividas (objeto)
  - [GET] /sistema1/pessoa_fisica/< id>/endereco
  - [POST] /sistema1/pessoa_fisica/< id>/endereco
    - Parâmetros:
      - Logradouro
      - Numero 
      - ...
  - [PUT] /sistema1/pessoa_fisica/< id>/endereco/< id>
      - Parâmetros:
      - Logradouro
      - Numero 
      - ...
  - [GET] /sistema1/pessoa_fisica/< id>/lista_dividas
  - [POST] /sistema1/pessoa_fisica/< id>/lista_dividas
    - Dividas (Objeto)
  - [PUT] /sistema1/pessoa_fisica/<id>/lista_dividas/< id>
  
- **sistema 2**  
  - [GET] /sistema2/pessoa_fisica
    - Filtros:
      - Nome
      - CPF
      - Data_cadastro
      - ...
  - [GET] /sistema2/pessoa_fisica/< id>
  - [PUT] /sistema2/pessoa_fisica/< id>
  - [POST] /sistema2/pessoa_fisica
    - Parâmetros:
      - Nome
      - cpf
      - nome da mae
      - nome do pai
      - ...
      - Endereco (objeto)
      - Lista Bens (objeto)
      - Fontes de renda (objeto)
  - [GET] /sistema2/pessoa_fisica/< id>/endereco
  - [POST] /sistema2/pessoa_fisica/< id>/endereco
    - Parâmetros:
      - Logradouro
      - Numero 
      - ...
  - [PUT] /sistema2/pessoa_fisica/< id>/endereco/< id>
  
  - [GET] /sistema2/pessoa_fisica/< id>/renda
  - [POST] /sistema2/pessoa_fisica/< id>/renda
    - Parâmetros:
      - fontes de renda
      - ...
  - [PUT] /sistema2/pessoa_fisica/< id>/renda
  
  - [GET] /sistema2/pessoa_fisica/< id>/bens
    - Filtros
      - Data_cadastro
      - Valor_bem
  - [PUT] /sistema2/pessoa_fisica/< id>/bens/< id>
  - [POST] /sistema2/pessoa_fisica/< id>/bens
    - Parâmetros:
      - Lista de bens
      
- **sistema 3**  
  - [GET] /sistema3/pessoa_fisica
    - Filtros:
      - Nome
      - CPF
      - Data_cadastro
      - Bureau
  - [GET] /sistema3/pessoa_fisica/< id>
  - [PUT] /sistema3/pessoa_fisica/< id>
  - [POST] /sistema3/pessoa_fisica
    - Parâmetros:
      - Nome
      - cpf
      - nome da mae
      - nome do pai
      - Movimentacao Financeira (objeto)
      - Dados Ultima Compra (objeto)
  - [GET] /sistema3/pessoa_fisica/< id>/movimentacao_financeira
  - [PUT] /sistema3/pessoa_fisica/< id>/movimentacao_financeira/< id>
  - [POST] /sistema3/pessoa_fisica/< id>/movimentacao_financeira
    - Parametros
      - Movimentações financeiras
        - lat
        - lon
        - valor
        - categoria
        
  - [GET] /sistema3/pessoa_fisica/< id>/dados_ultima_compra
  - [PUT] /sistema3/pessoa_fisica/< id>/dados_ultima_compra/< id>
  - [POST] /sistema3/pessoa_fisica/< id>/dados_ultima_compra
      - Parametros
      - Movimentações financeiras
        - lat
        - lon
        - valor
        - categoria
        - cnpj

  - [GET] /sistema3/bureau
    - Filtros
      - ID
      - Cidade
      - Estado
  - [POST] /sistema3/bureau
    - Parametros
      - Endereco
      - Responsavel
      - ...
  - [PUT] /sistema3/bureau/id

# **Sistema**
## Disclaimer
A idéia desse "sistema" criado foi explorar a idéia de Microserviços se comunicando através de uma api REST, além de dar uma passada no tema de mensageria. Em momento algum esse trabalho teve a pretensão de fazer um código bonito, eficiente e a prova de falhas.

Se a idéia fosse evoluir esse sistema faria algumas mudanças de imediato:
- Utilizacao de DOCKER
- Utilização do swagger para criação e versionamento da API Rest.
- Utilização do aiohttp ao invés de flask.
- Conectar realmente a um database.
- Implementar autenticação e autorização no servidor Auth.


Para rodar o sistema:
- Utilizado python 3.6.3
- Crie um ambiente virtual
- Abra um terminal
- Se conecte ao ambiente virtual criado acima
  - instale os pacotes (pip install -r requeriments)
  - rode o arquivo orquestrador.py (python orquestrador.py)
  - O orquestrador irá criar 3 aplicações em flask representando os microserviços, implementará uma comunicação assíncrona com o front end utilizando Celery como broker, além de uma pagina para testar os endpoints desses microserviços.
  - O orquestrador disponibilizará um HTML através do link "http://127.0.0.1:5005". Nesse HTML teremos 3 botões para acessar os "microserviços" indepentementes e um quarto botão que irá utilizar mensageria e comunicação assíncrona para rodar algo que demanda um grande processamento em background.
- Abra um segundo terminal
  - rode serviço do Celery para mensageria (celery -A orquestrador.celery worker)
- Acesse o link http://127.0.0.1:5005


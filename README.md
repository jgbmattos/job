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
- Circuit Breaker*
  - Será utilizado o Hystrix como circuit breaker na fila de mensageria entre os microserviços e servidor de authenticação e autorização.
  - Nesse cenário ele também será usado para monitoramento desses recursos.
###### *Não ficou claro no problema se os micro serviços que acessarão esses sistemas vão precisar de uma comunicação assíncrona. Acredito que sim, se este for o caso, trocasse a API REST proposta aqui, por algum serviço de mensageria entre todos os micro serviços e adicionasse o circuit breaker em toda essa comunicação. Além de prevenir problemas adicionasse uma camada legal de monitoramento em toda a comunicação.
- Microserviço para base B e C, com o intuito de permitir escalar facilmente.
- Base A não necessáriamente precisaria ser um microserviço. As vezes um monolito numa situação dessa facilite o controle de segurança de acesso etc.
- **BASE A**:
  - Sistema deve ficar em um rede interna, atrás de um firewall. Com isso pretende-se além da segurança tradicional que a combinação HTTPS + JWT para requisições da API trazer uma maior facilidade e controle na manutenção por pessoas autorizadas.
  - Acredito também que para um sistema desse tipo é muito importante que as autorização sejam muito bem seguimentadas para somente o escopo que a pessoa realmente deve ter acesso, além do acesso aos dados serem sempre temporários.
  - Banco PostgreSQL
  
- **BASE B**:
  - Segurança, autorização e autenticação será garantida através do protocolo HTTPS + OAUTH 2.0.
  - Acesso temporário aos recursos.
  - Para ter um desempenho satisfatorio, esse micro serviço deverá ficar atrás de um balancedor de carga e distruído em um cluster de servidores.
  - Banco de dados MongoDB
  
- **BASE C**:
  - Utiliza-se de recurso elástico assim como a BASE B e com o intuíto de aumentar ainda mais o desempenho desse recurso não seria utilizado o OAuth 2.0. Com a diminuição do payload adicional que o token JWT insere na comunicação, níveis maiores de velocidade devem ser alcançados.
  - Deve-se, para manter alguma segurança, ser enviado na requisição ao recurso um usuário e senha. A lógica de validação desse usuário deve ser armazenada e tratada pelo próprio micro serviço.
  - Para ter um desempenho satisfatorio, esse micro serviço deverá ficar atrás de um balancedor de carga e distruído em um cluster de servidores.
  - Banco de dados MongoDB

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
- MongoDB & PostgreSQL

# **Dados armazenados**
- Para todos os sitemas armazenaria dados da ultima consulta. Data/Hora, IP, Usuário.
- Sistema 2.
   - Armazenaria também o nome da pessoa. Já tenho todos os dados mais relevantes, o nome não me parece ser um problema. Da forma que está caso eu precise apresentar o score + nome para algum usuário eu precisaria fazer a consulta em outro microservico para buscar essa informação. Me parece disperdício.
   - A lista de dívidas me parece algo importante para fazer o score do cliente, porém, por se tratar de uma informação bastante confidencial acredito que não deveria ser gravado no banco B. Caso seja necessário para o calculo deve ser solicitado ao serviço A que fará uma avaliação de permissão.
   
# **Disponibilização dos Dados**
Para disponibilizar os dados acredito que uma aplicação WEB seja suficiente.
Dados sensíveis devem ser disponibilizados mediante autenticação. 
Bancos e outras instituições acredito que teriam mais interesse em acessar a API diretamente para poder integrar com os sistemas próprios. Nesse cenário um local no site para criação de CHAVES de acesso pode ser uma maneira interessante de criar um link de acesso com sistemas tercerios de forma segura.

Criaria os seguintes endpoints:
- **sistema 1**
  - /sistema1/< cpf>
  - /sistema1/< nome>
  - /sistema1/< endereco> --Entendo que alguem teria interesse em saber dados do dono de determinado imóvel (desconheço a legalidade)
    - Permtiria query's de data para listas de dividas, data de criação da divida, ou algo parecido.
- **sistema 2**  
  - /sistema2/< cpf>
  - /sistema2/< nome>
  - /sistema2/< endereco> --Entendo que alguem teria interesse em saber dados do dono de determinado imóvel (desconheço a legalidade)
  - /sistema2
    - Permitira querys de lista de dividas (Pessoas com maiores dividas, por favor, quantidade, etc).
- **sistema 3**  
  - /sistema3/< cpf>
  - /sistema3/< cartao>
  - /sistema3/<dt_movimentacao> --Entendo que alguem teria interesse em saber dados do dono de determinado imóvel (desconheço a legalidade)
  - /sistema3/<tipo_de_movimentacao>
  - /sistema3/<id_bureau> --listaria consultas no bureau
  
  
OBS: Não fica totalmente claro quais dados são necessários ao final de tudo. Por conta disso é dificil dizer o que será interessante adicionar para cada microserviço.

# **Sistema**
## Disclaimer
A idéia desse "sistema" criado foi explorar a idéia de Microserviços se comunicando através de uma api REST, além de dar uma passada no tema de mensageria. Em momento algum esse trabalho teve a pretensão de fazer um código bonito, eficiente e a prova de falhas.

Se a idéia fosse evoluir esse sistema faria algumas mudanças de imediato:
- Utilização do swagger para criação e versionamento da API Rest.
- Utilização do aiohttp ao invés de flask.
- Conectar realmente a um database.
- Implementar autenticação e autorização no servidor Auth.


Para rodar o sistema:
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


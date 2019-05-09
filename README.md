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
- ## **sistema 1**

![system1](https://user-images.githubusercontent.com/10090364/57422397-4aa11c00-71e6-11e9-8789-586a87b9e6d2.png)
  
- ## **sistema 2**  
- Como possível solução para o problema dos algoritmos de machine learning poderia ser implementada uma query no endpoint do tipo SQL. Essa query receberia um comando SQL. Com isso se ganha em flexibilidade. Porém, deve se tomar um cuidado maior com permissão nesses casos.

![system2](https://user-images.githubusercontent.com/10090364/57422399-4aa11c00-71e6-11e9-89a2-ee5198ba616a.png)

- ## **sistema 3**  

![system3](https://user-images.githubusercontent.com/10090364/57422398-4aa11c00-71e6-11e9-958a-361b3cb6d14a.png)


# **Sistema**
Se a idéia fosse evoluir esse sistema faria algumas mudanças de imediato:
- Utilização do aiohttp ao invés de flask.
- Conectar a um database.
- Implementar autenticação e autorização no servidor Auth.


Para rodar o sistema:
- Clone o repositório ou faça download.
- Acesse o diretorio dos fontes
- rodar: docker-compose build
- rodar: docker-compose up
- Com isso todas as API's irão subir e ficaram disponíveis os seguintes endpoints:
  - http:127.0.0.1:5001/api/pessoa_fisica
  - http:127.0.0.1:5002/api/pessoa_fisica
  - http:127.0.0.1:5003/api/pessoa_fisica
  - http:127.0.0.1:5003/api/bureau
- Documentação da API:
  - http:127.0.0.1:5001/api/doc
  - http:127.0.0.1:5002/api/doc
  - http:127.0.0.1:5003/api/doc

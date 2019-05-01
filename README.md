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
- **BASE A**:
  - Sistema deve ficar em um rede interna, atrás de um firewall. Com isso pretende-se além da segurança tradicional que a combinação HTTPS + JWT para requisições da API trazer uma melhor manutenção de pessoas autorizadas.
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
![Diagrama em branco (1)](https://user-images.githubusercontent.com/10090364/57038271-ef908780-6c2f-11e9-8044-0dceae8d7767.png)

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
- Sistema 1. Não consigo pensar em nada mais para armazenar.
- Sistema 2.
   - Armazenaria também o nome da pessoa. Já tenho todos os dados mais relevantes, o nome não me parece ser um problema. Da forma que está caso eu precise apresentar o score + nome para algum usuário eu precisaria fazer a consulta em outro microservico para buscar essa informação. Me parece disperdício.
   - A lista de dívidas me parece algo importante para fazer o score do cliente, porém, por se tratar de uma informação bastante confidencial acredito que não deveria ser gravado no banco B. Caso seja necessário para o calculo deve ser solicitado ao serviço A que fará uma avaliação de permissão.
   
# **Disponibilização dos Dados**
Para disponibilizar os dados acredito que uma aplicação WEB seja suficiente.
Dados sensíveis devem ser disponibilizados mediando usuário usuário e senha. Para os casos em que se faz necessário o envio do TOKEN na requisição.
Bancos e outras instituições acredito que teriam mais interesse em acessar a API diretamente para poder integrar com os sistemas próprios. Nesse cenário um local no site para criação de CHAVES de acesso podem ser uma maneira interessante de criar um link de acesso com sistemas tercerios.
  



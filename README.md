# Demo Kafka

## Table of Contents
+ [Sobre este Projeto](#sobre-este-projeto) 
+ [Descricao do Projeto](#descricao-do-projeto)
+ [Tecnologias Utilizadas](#tecnologias-utilizadas)
+ [Comunicação Entre os Serviços](#comunicação-entre-os-serviços)
+ [Executando o Ssitema](#executando-o-sistema)

## Sobre este Projeto
Este projeto foi criado por Lucian Augusto para obtenção de nota parcial da disciplina de Sistemas Distribuídos, do Curso Bacharelado em Sistemas de Informação da Universidade Tecnológica Federal do Paraná (UTFPR).

## Descricao do Projeto
Este projeto é uma *Proof of Concept* (**POC**) de um sistema distribuído, em que serviços distintos se comunicam entre si utilizando um serviço de mensageria, com um *broker* dedicado e *tópicos* especificamente estruturados. Como sistema de mensageria, optamos por utilizar o [Apache Kafka](https://kafka.apache.org) devido ao interesse do autor sobre esta tecnologia.

Este projeto visa simular simploriamente uma plataforma online de contabilidade. Esta plataforma possui três serviços:
1. **Dashboard:** Uma aplicação Web que serve páginas e, efetivamente, é responsável por todas as ações que os usuários do sistema possam realizar. Ou seja, esta aplicação e o principal serviço do sistema.
2. **Invoice Geneator:** Aplicação responsável por realizar a geração de notas fiscais que os usuarios da plataforma desejam emitir. Este serviço não possui nenhuma interação direta com o usuário. O usuário faz a requisição através do *Dashboard*. O *Dashboard* então envia uma mensagem para o *Invoice Generator* que faz a geração. Ao finalizar a geração, o serviço notifica o *Dashboard* através de uma mensagem, de que a nota fiscal foi gerada.
3. **Score Calculator:** Esta aplicação é responsável por fazer o cálculo do *score* ou pontuação dos usuários dentro da plataforma, proporcionando a eles, benefícios e outros produtos dentro da plataforma com base nesta pontuação. Novamente, o *Dashboard* envia uma mensagem para esta aplicação requisitando o cálculo desta pontuação. O *Score Calculator* então retorna uma mensagem ao *Dashboard* contendo o *score* calculado.

## Tecnologias Utilizadas
Esta *POC* utiliza o [Apache Kafka](https://kafka.apache.org) como serviço de mensageria. O *Dashboard* é uma aplicação web escrita em [Node.js](https://nodejs.org/en) e utiliza o [KafkaJS](https://kafka.js.org/) como cliente para se comunicar com o *broker*. Ambos *Invoice Generator* e *Score Calculator* foram implementados em [Python](https://www.python.org/) e utilizam o [Confluent_Kafka](https://github.com/confluentinc/confluent-kafka-python) como cliente.

Todas as aplicações rodam dentro de *containers* utilizando a plataforma [Docker](https://www.docker.com/) para facilitar o desenvolvimento, isolar cada serviço, e para poder rodar o sistema dentro de qualquer sistema operacional. Utilizamos as imagens oficiais do Node.js e Python como base para as aplicações e para o Kafka, utilizamos as imagens fornecidas pela [Confluent](https://www.confluent.io/). Para arquitetar todo o sistema, utilizamos a ferramenta [Docker Compose](https://docs.docker.com/compose/) para construir e rodas todos os containers de forma coordenada.

## Comunicação Entre os Serviços
Como dito [aqui](#tecnologias-utilizadas), os serviços se comunicam através de mensagens, utilizando o [Apache Kafka](https://kafka.apache.org) como *broker*. O Kafka organiza suas mensagems em **tópicos**. Cada mensagem gerada por um **Produtor** deve conter um **tópicos**. Os **Consumidores** se ***escrevem*** em **tópicos** e então, recebem as mensagens presentes neste **tópico** por meio da intermediação do *broker*.

É importante destacar que o [Kafka](https://kafka.apache.org) utiliza um **protocolo próprio** para realizar a comunicação. Este **protocolo** é **binário** e é baseado no  **protocolo TCP**.

Neste sistema cada serviço assume ambos os papéis de **Consumidor** e **Produtor**. O *Dashboard* envia uma mensagem para ambos *Invoice Generator* e *Score Calculator* informando que é preciso gerar uma nova nota fiscal ou então calcular um *score*. Neste momento, o *Dashboard* está atuando como o **produtor** e ambos *Invoice Generator* e *Score Calculator* atuam como **consumidores**. O **tópico** utilizado para o *Dashboard* requisitar a geração de uma nota fiscal é o tópico `generate-invoice`, que é consumido pelo *Invoice Generator*. Já o **tópico** que o *Dashboard* utiliza para requisitar o cálculo do *score* é o `calculate-score`, que é consumido pelo *Score Calculator*.

Ao Receber uma mensagem em seus respectivos **tópicos**, ambos *Invoice Generator* e *Score Calculator* realizam suas operações necessárias e então retornam, respectivamente, mensagens nos **tópicos** `invoice-generated` e `score-calculated`. O *Dashboard* consome estes **tópicos**, podendo então notificar o usuário de que a ação requisitada foi concluída com sucesso. Nesta situação, nós temos ambos os serviços *Invoice Generator* e *Score Calculator* agindo como **produtores** e o *Dashboard* agindo como **consumidor**.

Um detalhe importante que deve ser destacado é de que, devido ao fato de todos os serviços estarem rodando dentro de containers, é necessário criar um `hostname` para o container que roda o *broker* e alterar a url padrão de acesso de `localhost:{PORT}` para `hostname:{PORT}` para que os *containers* dos servicos possam se comunicar com o *broker*.

## Executando o Sistema
Para executar o sistema é necessário ter instalado em sua máquina [Git](https://git-scm.com/) e [Docker](https://www.docker.com/).

### Clonando o Repositório
Para clonar o repositório, basta utilizar o seguinte comando num terminal:

``` shell
git clone git clone git@github.com:lucian-augusto/kafka-demo.git
```

e então ir até o diretório criado utilizando:

``` shell
cd kafka-demo
```

### Executando
Para executar o sistema basta navegar até a raíz do projeto e utilizar o seguinte comando no terminal:

``` shell
docker-compose up -d
```

Este comando irá, automaticamente, baixar as camadas de dependência e construir as imagens e subir os *containers*. Caso precise reconstruir as imagens (devido alguma alteração nos *Dockerfiles* ou no *docker-compose.yml*) basta adicionar a flag `--build` ao comando anterior.

Acesse os containers de cada serviço e execute cada um utilizando os seguintes comandos (Se quiser acompanhar as mensagens de todos s serviços, você deverá acessar cada *container* e rodar os serviços em uma sessão de terminal para cada um):

1. **Dashboard:**
Para Acessar o *container**:
``` shell
docker exec -it dashboad /bin/bash
```

Dentro do *container*:

``` shell
npm install && npm run server
```

2. **Invoice Generator:**
Para Acessar o *container**:
``` shell
docker exec -it invoice-generator /bin/bash
```

Dentro do *container*:

``` shell
python src/invoice_generator.py config/config.ini
```

3. **Score Calculator:**
Para Acessar o *container**:
``` shell
docker exec -it score-calculator /bin/bash
```

Dentro do *container*:

``` shell
python src/score_calculator.py config/config.ini
```

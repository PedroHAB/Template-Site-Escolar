# Dependências e instruções de uso do Projeto
![HTML5](https://img.shields.io/badge/html5-%23E34F26.svg?style=for-the-badge&logo=html5&logoColor=white)
![Python](https://img.shields.io/badge/python-%233776AB.svg?style=for-the-badge&logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/postgreSQL-%23336791.svg?style=for-the-badge&logo=postgresql&logoColor=white)


Para que a aplicação funcione corretamente, você precisará instalar as seguintes bibliotecas Python:

- Flask: O framework web principal.
- Flask_bcrypt: Extensão do Flask para hashing seguro de senhas.
- psycopg2: Adaptador para a comunicação com o banco de dados PostgreSQL.

Você pode instalá-las usando pip:

```
pip install Flask Flask-Bcrypt psycopg2
```

## Configuração do Banco de Dados (PostgreSQL)

O programa requer um banco de dados PostgreSQL chamado "usuarios_db".

Você deve criar o banco de dados e as seguintes tabelas nele:

1. Criação do Banco de Dados

Certifique-se de que o banco de dados com o nome exato "usuarios_db" exista.

2. Definição das Tabelas

Execute os comandos SQL abaixo para criar as tabelas com seus respectivos esquemas:

Tabela matriculas

Esta tabela armazena os números de matrícula que serão referenciados pela tabela usuarios. É importante notar que as matrículas devem ser inseridas manualmente nesta tabela antes que um usuário possa ser cadastrado.

```
CREATE TABLE matriculas(
	id serial PRIMARY KEY,
	NUM VARCHAR(30) NOT NULL
);
```
Tabela usuarios

Armazena informações sobre os usuários, incluindo uma chave estrangeira (matricula) que deve ser única e referenciar a coluna id na tabela matriculas.

```
CREATE TABLE usuarios (
	id SERIAL PRIMARY KEY,
	nome VARCHAR(100) NOT NULL,
	email VARCHAR(100) UNIQUE NOT NULL,
	senha VARCHAR(255) NOT NULL,
	matricula INTEGER UNIQUE REFERENCES matriculas (id)
);
```

Tabela noticias

Usada para armazenar o conteúdo das notícias.

```
CREATE TABLE noticias (
	id SERIAL PRIMARY KEY,
	titulo VARCHAR(200) NOT NULL,
	subtitulo VARCHAR(200),
	corpo TEXT NOT NULL,
	imagens BYTEA[]
);
```

Tabela professores

Usada para armazenar informações e fotos dos professores.

```
CREATE TABLE professores (
	id SERIAL PRIMARY KEY,
	nome VARCHAR(100) NOT NULL,
	cargo VARCHAR(100) NOT NULL,
	frase TEXT,
	foto BYTEA
);
```

‼ Observação Importante sobre Matrículas

Conforme a regra do sistema: Cada usuário deve estar associado a uma matrícula que já deve existir na tabela matriculas.

- O valor na coluna matricula da tabela usuarios é um ID que aponta para um registro existente em matriculas(id).
- As matrículas devem ser previamente cadastradas manualmente no banco de dados (matriculas é uma tabela de referência) para que o cadastro de um novo usuário seja possível.


## Como Rodar o Programa

1. Instale as dependências listadas acima.
2. Configure o banco de dados usuarios_db e crie todas as tabelas.
3. Insira algumas matrículas na tabela matriculas para testar o cadastro de usuários.
4. Execute o arquivo principal da aplicação Python:

```
python app.py
```


CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    senha VARCHAR(255) NOT NULL,
	matricula INTEGER UNIQUE REFERENCES matriculas (id)
);
CREATE TABLE matriculas(
	id serial PRIMARY KEY,
	NUM VARCHAR(30) NOT NULL
);
CREATE TABLE noticias (
    id SERIAL PRIMARY KEY,
    titulo VARCHAR(200) NOT NULL,
    subtitulo VARCHAR(200),
    corpo TEXT NOT NULL,
    imagens BYTEA[]
);

CREATE TABLE professores (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    cargo VARCHAR(100) NOT NULL,
    frase TEXT,
    foto BYTEA 
);

INSERT INTO matriculas (NUM) VALUES ('123456789');

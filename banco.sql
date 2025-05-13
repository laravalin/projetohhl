CREATE TABLE configuracao (
    id INT AUTO_INCREMENT PRIMARY KEY, 
    chave_configuracao VARCHAR(200) NOT NULL, 
    valor VARCHAR(200) NOT NULL
);

CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY, 
    nome_usuario VARCHAR(45) NOT NULL, 
    login VARCHAR(45) UNIQUE NOT NULL, 
    senha VARCHAR(256) NOT NULL, 
    nome_empresa VARCHAR(200) NOT NULL, 
    email VARCHAR(200) NOT NULL,
    id_configuracao INT, 
    FOREIGN KEY (id_configuracao) REFERENCES configuracao(id) ON DELETE CASCADE
);

CREATE TABLE origem (
    id INT AUTO_INCREMENT PRIMARY KEY, 
    nome_site VARCHAR(200) NOT NULL, 
    url_site VARCHAR(200) NOT NULL
);

CREATE TABLE marca (
    id INT AUTO_INCREMENT PRIMARY KEY,
	nome_marca VARCHAR(200) NOT NULL,
    nota_marca_avg DECIMAL(3,2) NOT NULL 
);

CREATE TABLE produto (
    id INT AUTO_INCREMENT PRIMARY KEY, 
    nome_produto VARCHAR(45) NOT NULL, 
    valor_produto DECIMAL(10,2) NOT NULL, 
    id_marca INT NOT NULL,
  	id_origem INT NOT NULL, 
    nota_produto_avg DECIMAL(3,2), 
    data_produto DATE, 
    FOREIGN KEY (id_marca) REFERENCES marca(id) ON DELETE CASCADE,
    FOREIGN KEY (id_origem) REFERENCES origem(id) ON DELETE CASCADE
);

CREATE TABLE avaliacao (
    id INT AUTO_INCREMENT PRIMARY KEY, 
    nome_avaliador VARCHAR(200) NOT NULL, 
    comentario TEXT NOT NULL,
    nota_avaliacao DECIMAL(3,2),
    id_produto INT NOT NULL,
    FOREIGN KEY (id_produto) REFERENCES produto(id) ON DELETE CASCADE
);


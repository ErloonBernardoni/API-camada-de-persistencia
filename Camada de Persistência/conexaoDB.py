import mysql.connector

# Configurações de conexão
config = {
  'host': 'localhost',
  'user': 'root',
  'password': 'root@123'
}

# Criação da conexão
conn = mysql.connector.connect(**config)
# Criação do cursor
cursor = conn.cursor()
# Criação da Base
cursor.execute("CREATE DATABASE IF NOT EXISTS proqui;")
conn.commit()
cursor.execute("USE proqui;")
conn.commit()

cursor.execute( """CREATE TABLE IF NOT EXISTS Cidade (
                                              IBGE INTEGER(7) NOT NULL,
                                              Cidade VARCHAR(100) NOT NULL,
                                              UF VARCHAR (2) NOT NULL,
                                              DDD INTEGER (2) NOT NULL,
                                              PRIMARY KEY(IBGE));""")

cursor.execute( """CREATE TABLE IF NOT EXISTS CEP (
                                              CEP INTEGER(9) NOT NULL,
                                              Logradouro VARCHAR(100) NOT NULL,
                                              IBGE INTEGER(7) NOT NULL,
                                              Bairro VARCHAR(55) NOT NULL,
                                              PRIMARY KEY (CEP),
                                              FOREIGN KEY (IBGE) REFERENCES Cidade(IBGE));""")


cursor.execute( """CREATE TABLE IF NOT EXISTS Usuario (
                                              id INTEGER NOT NULL AUTO_INCREMENT,
                                              Nome VARCHAR(100) NOT NULL,
                                              Login VARCHAR(10) NOT NULL,
                                              CEP INTEGER(9) NOT NULL,
                                              Numero INTEGER (5),
                                              Complemento VARCHAR(25),
                                              Telefone INTEGER(11),
                                              PRIMARY KEY (id),
                                              FOREIGN KEY (CEP) REFERENCES CEP(CEP));""")
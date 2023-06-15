from flask import Flask, jsonify, request
from conexaoDB import conn, cursor
import re

app = Flask(__name__)


# Função que trata o JSON
def converteMinusculo(objeto):
    if isinstance(objeto, dict):
        novo_objeto = {}
        for chave, valor in objeto.items():
            novo_objeto[chave.lower()] = valor
        return novo_objeto


@app.route('/localidade', methods=['POST'])
def insereLocal():
    dados = request.json
    dados = converteMinusculo(dados)
    campos = ['cep', 'logradouro', 'bairro', 'cidade', 'uf', 'ibge', 'ddd']

    # Valida tamanho JSON
    if len(dados) > 7 or (len(dados) < 6):
        return jsonify({'mensagem': 'Quantitativo informado incompativel'}), 400

    # Valida chaves JSON
    for campo in campos:
        if campo not in dados:
            return jsonify({'mensagem': f'O campo {campo} não está presente nas chaves do JSON.'}), 400

    cep = dados['cep']
    logradouro = dados['logradouro']
    bairro = dados['bairro']
    cidade = dados['cidade']
    uf = dados['uf']
    ibge = dados['ibge']
    ddd = dados['ddd']

    # Trata campo CEP
    cep = str(cep).replace("-", "")

    # Valida cada campo do JSON
    if len(str(ibge)) > 7 or (not ibge):
        return jsonify({'mensagem': f'Ultrapassou o limite de dígitos ou está vazio no campo{ibge}'}), 400
    elif len(str(cep)) > 8 or (not cep):
        return jsonify({'mensagem': f'Ultrapassou o limite de dígitos ou está vazio no campo{cep}'}), 400
    elif len(str(logradouro)) > 100 or (not logradouro):
        return jsonify({'mensagem': f'Ultrapassou o limite de caracteres ou está vazio no campo{logradouro}'}), 400
    elif len(str(bairro)) > 55:
        return jsonify({'mensagem': f'Ultrapassou o limite de caracteres no campo{bairro}'}), 400
    elif len(str(cidade)) > 100 or (not cidade):
        return jsonify({'mensagem': f'Ultrapassou o limite de caracteres ou está vazio no campo{cidade}'}), 400
    elif len(str(uf)) > 2 or (not uf):
        return jsonify({'mensagem': f'Ultrapassou o limite de caracteres ou está vazia no campo{uf}'}), 400
    elif len(str(ddd)) > 3 or (not ddd):
        return jsonify({'mensagem': f'Ultrapassou o limite de caracteres ou está vazio no campo{ddd}'}), 400
    else:
        print("Todos os campos estão ok!")

    # Valida se existe Cidade e depois valida se existe CEP
    SQL = f"SELECT * FROM CIDADE WHERE IBGE = {ibge}"
    cursor.execute(SQL)
    resultado = cursor.fetchone()

    if resultado:
        SQL = f"SELECT * FROM CEP WHERE CEP = {cep}"
        cursor.execute(SQL)
        resultado = cursor.fetchone()
        if resultado:
            return jsonify({'mensagem': 'Esta Localidade já existe na Base de dados'}), 400
        else:
            SQL = f"INSERT INTO CEP VALUES ({cep}, '{logradouro}', {ibge}, '{bairro}')"
            cursor.execute(SQL)
            conn.commit()
            return jsonify({'mensagem': 'CEP cadastrado!'}), 200
    else:
        SQL = f"INSERT INTO CIDADE VALUES ({ibge}, '{cidade}', '{uf}', {ddd})"
        cursor.execute(SQL)
        conn.commit()
        SQL = f"INSERT INTO CEP VALUES ({cep}, '{logradouro}', {ibge}, '{bairro}')"
        cursor.execute(SQL)
        conn.commit()
        return jsonify({'mensagem': 'Localidade cadastrada!'}), 200


@app.route('/localidade/<int:ibge>', methods=['GET'])
def obtemCidade(ibge):
    SQL = f"SELECT * FROM CIDADE WHERE IBGE = {ibge}"
    cursor.execute(SQL)
    resultado = cursor.fetchone()

    if resultado:
        cidade = {
            'IBGE': resultado[0],
            'Cidade': resultado[1],
            'UF': resultado[2],
            'DDD': resultado[3]
        }
        return jsonify(cidade), 200
    else:
        return jsonify({'mensagem': 'Cidade não encontrada.'}), 404


@app.route('/localidade/<int:ibge>/<int:cep>', methods=['GET'])
def obtemCep(ibge, cep):
    SQL = f"SELECT * FROM CEP WHERE IBGE = {ibge} AND CEP = {cep}"
    cursor.execute(SQL)
    resultado = cursor.fetchone()

    if resultado:
        json = {
            'CEP': resultado[0],
            'Logradouro': resultado[1],
            'IBGE': resultado[2],
            'Bairro': resultado[3]
        }
        return jsonify(json), 200
    else:
        return jsonify({'mensagem': 'Dados não encontrados.'}), 404


@app.route('/localidade/<int:ibge>', methods=['PUT'])
def atualizaCidade(ibge):
    dados = request.json
    converteMinusculo(dados)

    if len(dados) != 3:
        return jsonify({'mensagem': 'Quantitativo informado incompativel'}), 400

    cidade = dados.get('cidade')
    uf = dados.get('UF')
    ddd = dados.get('DDD')

    if len(str(cidade)) > 100 or (not cidade):
        return jsonify({'mensagem': f'Ultrapassou o limite de caracteres ou venho vazio no campo {cidade}'})
    elif len(str(uf)) > 2 or (not uf):
        return jsonify({'mensagem': f'Ultrapassou o limite de caracteres ou venho vazio no campo {uf}'})
    elif len(str(ddd)) > 3 or (not ddd):
        return jsonify({'mensagem': f'Ultrapassou o limite de caracteres ou venho vazio no campo {ddd}'})

    campos: list[str] = [f"cidade = '{cidade}'", f"uf = '{uf}'", f"ddd = {ddd}"]

    # Monta a consulta SQL
    SQL = f"UPDATE CIDADE SET {', '.join(campos)} WHERE IBGE = {ibge}"
    cursor.execute(SQL)
    conn.commit()

    if cursor.rowcount > 0:
        return jsonify({'mensagem': 'Dados da cidade atualizados com sucesso.'}), 200
    else:
        return jsonify({'mensagem': 'Cidade não encontrada.'}), 404


@app.route('/localidade/<int:ibge>', methods=['DELETE'])
def deletaCidade(ibge):
    SQL = f"SELECT * FROM CIDADE WHERE IBGE = {ibge}"
    cursor.execute(SQL)
    resultado = cursor.fetchone()

    if not resultado:
        return jsonify({'mensagem': 'Cidade não encontrada!'}), 404

    SQL = f"DELETE FROM CIDADE WHERE IBGE = {ibge}"
    cursor.execute(SQL)
    conn.commit()
    return jsonify({'mensagem': 'Cidade deletada!'}), 200


@app.route('/usuario', methods=['POST'])
def insereUsuario():
    dados = request.json
    dados = converteMinusculo(dados)
    campos = ['nome', 'login', 'cep', 'numero', 'complemento', 'telefone']

    # Valida tamanho JSON
    if len(dados) < 3 or (len(dados) > 6):
        return jsonify({'mensagem': 'Quantitativo informado incompativel'}), 400

    # Valida chaves JSON
    for campo in campos:
        if campo not in dados:
            return jsonify({'mensagem': f'O campo {campo} não está presente nas chaves do JSON.'}), 400

    nome = dados['nome']
    login = dados['login']
    cep = dados['cep']
    numero = dados['numero'] if 'numero' in dados else ""
    complemento = dados['complemento'] if 'complemento' in dados else ""
    telefone = dados['telefone'] if 'telefone' in dados else ""

    # Trata campo nome
    nome = re.sub(r'\d', '', str(nome))

    # Trata campo CEP
    cep = str(cep).replace("-", "")

    # Trata campo telefone
    telefone = re.sub(r'\D', "", str(telefone))

    # Valida cada campo do JSON
    if len(str(nome)) > 100 or (not nome):
        return jsonify({'mensagem': f'Quantidade de caracteres maior que o permitido ou vazio no campo {nome}'}), 400
    elif len(str(login)) > 20 or (not login):
        return jsonify({'mensagem': f'Quantidade de caracteres maior que o permitido ou vazio no campo {login}'}), 400
    elif len(str(cep)) > 8 or (not cep):
        return jsonify({'mensagem': f'Quantidade de digitos maior que o permitido ou vazio no campo {cep}'}), 400
    elif len(str(complemento)) > 25:
        return jsonify({'mensagem': f'Quantidade de caracteres maior que o permitido no campo {complemento}'}), 400

    SQL = f"SELECT 1 FROM USUARIO WHERE LOGIN = '{login}' "
    cursor.execute(SQL)
    resultado = cursor.fetchone()

    if resultado:
        return jsonify({'mensagem': 'Este usuario já existe'}), 400

    SQL = f"SELECT 1 FROM CEP WHERE CEP = {cep};"
    cursor.execute(SQL)
    resultado = cursor.fetchone()

    if not resultado:
        return jsonify({'mensagem': 'Este cep não existe na base!'}), 400

    SQL = f"""INSERT INTO USUARIO (nome, login, cep, numero, complemento, telefone) 
                          VALUES ('{nome}', '{login}', {cep}, '{numero}', '{complemento}','{telefone}') """
    cursor.execute(SQL)
    conn.commit()
    return jsonify({'mensagem': 'Usuario cadastrado!'}), 200


@app.route('/usuario/<int:id>', methods=['GET'])
def obtemUsuario(id):
    SQL = f"SELECT * FROM USUARIO WHERE ID = {id}"
    cursor.execute(SQL)
    resultado = cursor.fetchone()

    if resultado:
        usuario = {
            'Nome': resultado[0],
            'Login': resultado[1],
            'CEP': resultado[2],
            'Numero': resultado[3],
            'Complemento': resultado[4],
            'Telefone': resultado[5]
        }
        return jsonify(usuario), 200
    else:
        return jsonify({'mensagem': 'Usuario não encontrado.'}), 404


@app.route('/usuario/<int:id>', methods=['DELETE'])
def deletaUsuario(id):
    SQL = f"SELECT 1 FROM USUARIO WHERE ID = {id}"
    cursor.execute(SQL)
    resultado = cursor.fetchone()

    if not resultado:
        return jsonify({'mensagem': 'Usuario não encontrado.'}), 404
    else:
        SQL = f"DELETE FROM USUARIO WHERE ID = {id}"
        cursor.execute(SQL)
        conn.commit()
        return jsonify({'messagem': 'Usuario excluido!'}), 200

@app.route('/usuarios/', methods=['GET'])
def obtemUsuarios():
    SQL = f"SELECT * FROM USUARIO"
    cursor.execute(SQL)
    resultado = cursor.fetchall()
    if resultado:
        users = []
        for user in resultado:
            users.append({
                "id": user[0],
                "nome": user[1],
                "login": user[2],
                "cep": user[3],
                "numero": user[4],
                "complemento": user[5],
                "telefone": user[6],
            })
        return jsonify(users), 200
    else:
        return jsonify({'mensagem': 'Usuario não encontrado.'}), 404


@app.route('/dados/', methods=['GET'])
def obtemTudo():
    SQL = """select x.nome, 
	                x.Login, 
                    x.CEP, 
                    x.Numero, 
                    x.Complemento,
                    x.Telefone,
                    z.Logradouro,
                    z.IBGE,
                    z.Bairro,
                    y.Cidade,
                    y.UF,
                    y.DDD
	                from usuario x 
	   		             inner join cep z on (x.CEP = z.CEP)
	   		             inner join cidade y on (z.IBGE = y.IBGE)"""
    cursor.execute(SQL)
    resultado = cursor.fetchall()

    if resultado:
        return jsonify(resultado), 200
    else:
        return jsonify({'mensagem': 'Banco vazio.'}), 404


if __name__ == '__main__':
    app.run()

from flask import Flask, jsonify, request
from conexaoDB import cursor, conn
import re

app = Flask(__name__)

#Função que trata o JSON
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

    cep = dados['cep']
    logradouro = dados['logradouro']
    bairro = dados['bairro']
    cidade = dados['cidade']
    uf = dados['uf']
    ibge = dados['ibge']
    ddd = dados['ddd']

    #Trata campo CEP
    cep = str(cep).replace("-","")

    # Valida cada campo do JSON
    if (len(str(ibge)) > 7) or (not ibge):
        return jsonify({'mensagem': 'O código do IBGE ultrapassou o limite de dígitos ou está vazio'}), 400
    elif (len(str(cep)) > 8) or (not cep):
        return jsonify({'mensagem': 'O CEP ultrapassou o limite de dígitos ou está vazio'}), 400
    elif (len(str(logradouro)) > 100) or (not logradouro):
        return jsonify({'mensagem': 'O logradouro ultrapassou o limite de caracteres ou está vazio'}), 400
    elif (len(str(bairro)) > 55):
        return jsonify({'mensagem': 'O bairro ultrapassou o limite de caracteres'}), 400
    elif (len(str(cidade)) > 100) or (not cidade):
        return jsonify({'mensagem': 'A cidade ultrapassou o limite de caracteres ou está vazio'}), 400
    elif (len(str(uf)) > 2) or (not uf):
        return jsonify({'mensagem': 'A sigla da UF ultrapassou o limite de caracteres ou está vazia'}), 400
    elif (len(str(ddd)) > 3) or (not ddd):
        return jsonify({'mensagem': 'O DDD ultrapassou o limite de caracteres ou está vazio'}), 400
    else:
        print("Todos os campos estão ok!")

    # Valida se existe Cidade e depois valida se existe CEP
    SQL = f"SELECT * FROM CIDADE WHERE IBGE = {ibge}"
    cursor.execute(SQL)
    resultado = cursor.fetchall()

    if (resultado):
        SQL = f"SELECT * FROM CEP WHERE CEP = {cep}"
        cursor.execute(SQL)
        resultado = cursor.fetchall()
        if (resultado):
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

    cursor.close()
    conn.close()

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

    cursor.close()
    conn.close()

@app.route('/localidade/<int:ibge>', methods=['PUT'])
def atualizaCidade(ibge):
    dados = request.json
    converteMinusculo(dados)

    if len(dados) != 3:
        return jsonify({'mensagem': 'Quantitativo informado incompativel'}), 400

    cidade = dados.get('cidade')
    uf = dados.get('UF')
    ddd = dados.get('DDD')

    if (len(str(cidade)) > 100) or (not cidade):
        return jsonify({'mensagem': 'A cidade ultrapassou o limite de caracteres ou venho vazio'})
    elif (len(str(uf)) > 2) or (not uf):
        return jsonify({'mensagem': 'a sigla da UF ultrapassou o limite de caracteres ou venho vazio'})
    elif (len(str(ddd)) > 3) or (not ddd):
        return jsonify({'mensagem': 'o ddd ultrapassou o limite de caracteres ou venho vazio'})

    campos = []
    campos.append(f"cidade = '{cidade}'")
    campos.append(f"uf = '{uf}'")
    campos.append(f"ddd = {ddd}")

    # Monta a consulta SQL
    SQL = f"UPDATE CIDADE SET {', '.join(campos)} WHERE IBGE = {ibge}"
    cursor.execute(SQL)
    conn.commit()

    if cursor.rowcount > 0:
        return jsonify({'mensagem': 'Dados da cidade atualizados com sucesso.'}), 200
    else:
        return jsonify({'mensagem': 'Cidade não encontrada.'}), 404

    cursor.close()
    conn.close()

@app.route('/localidade/<int:ibge>', methods=['DELETE'])
def deletaCidade(ibge):

    SQL = f"SELECT * FROM CIDADE WHERE IBGE = {ibge}"
    cursor.execute(SQL)
    cidade = cursor.fetchone()

    if (not cidade):
        return jsonify({'mensagem': 'Cidade não encontrada!'}), 404

    # Execute a instrução de exclusão no banco de dados
    SQL = f"DELETE FROM CIDADE WHERE IBGE = {ibge}"
    cursor.execute(SQL)
    conn.commit()

    return jsonify({'mensagem': 'Cidade deletada!'}), 200

    cursor.close()
    conn.close()

@app.route('/usuario', methods=['POST'])
def insereUsuario():

    dados = request.json
    dados = converteMinusculo(dados)

    nome = dados['nome']
    login = dados['login']
    cep = dados['cep']
    numero = dados['numero'] if 'numero' in dados else ""
    complemento = dados['complemento'] if 'complemento' in dados else ""
    telefone = dados['telefone'] if 'telefone' in dados else ""

    #Trata campo nome
    nome = re.sub(r'\d', '', str(nome))

    # Trata campo CEP
    cep = str(cep).replace("-", "")

    #Trata campo telefone
    telefone = re.sub(r'\D', "", str(telefone))


    #Valida cada campo do JSON
    if (len(str(nome)) > 100 or (not nome)):
        return jsonify({'mensagem': f'Quantidade de caracteres maior que o permitido ou vazio no campo {nome}'}), 400
    elif (len(str(login)) > 20 or (not login)):
        return jsonify({'mensagem': f'Quantidade de caracteres maior que o permitido ou vazio no campo {login}'}), 400
    elif (len(str(cep)) > 8 or (not cep)):
        return jsonify({'mensagem': f'Quantidade de digitos maior que o permitido ou vazio no campo {cep}'}), 400
    elif (len(str(complemento)) > 25):
        return jsonify({'mensagem': f'Quantidade de caracteres maior que o permitido no campo {complemento}'}), 400

    SQL = f"SELECT 1 FROM USUARIO WHERE LOGIN = '{login}' "
    cursor.execute(SQL)
    resultado = cursor.fetchall()

    if (resultado):
        return jsonify({'mensagem': 'Este usuario já existe'}), 400

    SQL = f"SELECT 1 FROM CEP WHERE CEP = {cep};"
    cursor.execute(SQL)
    resultado = cursor.fetchall()

    if (not resultado):
        return jsonify({'mensagem': 'Este cep não existe na base!'}), 400

    SQL = f"""INSERT INTO USUARIO (nome, login, cep, numero, complemento, telefone) 
                          VALUES ('{nome}', '{login}', {cep}, '{numero}', '{complemento}','{telefone}') """

    cursor.execute(SQL)
    conn.commit()
    return jsonify({'mensagem': 'Usuario cadastrado!'}), 200

    cursor.close()
    conn.close()

@app.route ('/usuario/<int:id>', methods=['GET'])
def obtemUsuario(id):
    SQL = f"SELECT * FROM USUARIO WHERE ID = {id}"
    cursor.execute(SQL)
    resultado = cursor.fetchone()

    if (resultado):
        cidade = {
            'Nome': resultado[0],
            'Login': resultado[1],
            'CEP': resultado[2],
            'Numero': resultado[3],
            'Complemento': resultado[4],
            'Telefone': resultado[5]
        }
        return jsonify(cidade), 200
    else:
        return jsonify({'mensagem': 'Usuario não encontrado.'}), 404

    cursor.close()
    conn.close()

if __name__ == '__main__':
    app.run()
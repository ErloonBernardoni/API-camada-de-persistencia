from flask import Flask, jsonify, request
from conexaoDB import cursor, conn
import re

app = Flask(__name__)


@app.route('/localidade', methods=['POST'])
def insereLocal():
    dados = request.json

    cep = dados['cep']
    logradouro = dados['logradouro']
    bairro = dados['bairro']
    cidade = dados['cidade']
    uf = dados['uf']
    ibge = dados['ibge']
    ddd = dados['ddd']

    #Trata campo CEP
    cep = str(cep).replace("-","")
    int(cep)

    # Valida cada campo do JSON
    if (len(str(ibge)) > 7) or (ibge == ""):
        return jsonify({'mensagem': 'O código do IBGE ultrapassou o limite de dígitos ou está vazio'})
    elif (len(str(cep)) > 8) or (cep == ""):
        return jsonify({'mensagem': 'O CEP ultrapassou o limite de dígitos ou está vazio'})
    elif (len(str(logradouro)) > 100) or (logradouro == ""):
        return jsonify({'mensagem': 'O logradouro ultrapassou o limite de caracteres ou está vazio'})
    elif (len(str(bairro)) > 55):
        return jsonify({'mensagem': 'O bairro ultrapassou o limite de caracteres'})
    elif (len(str(cidade)) > 100) or (not cidade):
        return jsonify({'mensagem': 'A cidade ultrapassou o limite de caracteres ou está vazio'})
    elif (len(str(uf)) > 2) or (not uf):
        return jsonify({'mensagem': 'A sigla da UF ultrapassou o limite de caracteres ou está vazia'})
    elif (len(str(ddd)) > 3) or (not ddd):
        return jsonify({'mensagem': 'O DDD ultrapassou o limite de caracteres ou está vazio'})
    else:
        print("Todos os campos estão ok!")

    # Valida se existe Cidade e depois valida se existe CEP
    SQL = f"SELECT * FROM CIDADE WHERE IBGE = {ibge}"
    cursor.execute(SQL)
    SQL_RESULT = cursor.fetchall()

    if (SQL_RESULT):
        SQL = f"SELECT * FROM CEP WHERE CEP = {cep}"
        cursor.execute(SQL)
        SQL_RESULT = cursor.fetchall()
        if (SQL_RESULT):
            return jsonify({'mensagem': 'Esta Localidade já existe na Base de dados'})
        else:
            sql = f"INSERT INTO CEP VALUES ({cep}, '{logradouro}', {ibge}, '{bairro}')"
            cursor.execute(sql)
            conn.commit()
            return jsonify({'mensagem': 'CEP cadastrado!'})
    else:
        sql = f"INSERT INTO CIDADE VALUES ({ibge}, '{cidade}', '{uf}', {ddd})"
        cursor.execute(sql)
        conn.commit()
        sql = f"INSERT INTO CEP VALUES ({cep}, '{logradouro}', {ibge}, '{bairro}')"
        cursor.execute(sql)
        conn.commit()

    return jsonify({'mensagem': 'Localidade cadastrada!'})

@app.route('/localidade/<int:ibge>', methods=['GET'])
def obtemCidade(ibge):
    sql = f"SELECT * FROM CIDADE WHERE IBGE = {ibge}"
    cursor.execute(sql)
    resultado = cursor.fetchone()

    if resultado:
        cidade = {
            'IBGE': resultado[0],
            'Cidade': resultado[1],
            'UF': resultado[2],
            'DDD': resultado[3]
        }
        return jsonify(cidade)
    else:
        return jsonify({'mensagem': 'Cidade não encontrada.'}), 404

    cursor.close()
    conn.close()

@app.route('/localidade/<int:ibge>/<int:cep>', methods=['GET'])
def obtemCep(ibge, cep):
    sql = f"SELECT * FROM CEP WHERE IBGE = {ibge} AND CEP = {cep}"
    cursor.execute(sql)
    resultado = cursor.fetchone()

    if resultado:
        json = {
            'CEP': resultado[0],
            'Logradouro': resultado[1],
            'IBGE': resultado[2],
            'BAIRRO': resultado[3]
        }
        return jsonify(json)
    else:
        return jsonify({'mensagem': 'Dados não encontrados.'}), 404

    cursor.close()
    conn.close()

@app.route('/localidade/<int:ibge>', methods=['PUT'])
def atualizaCidade(ibge):
    dados = request.json

    if len(dados) != 3:
        return jsonify({'mensagem': 'Quantitativo informado incompativel'})

    cidade = dados.get('cidade')
    uf = dados.get('UF')
    ddd = dados.get('DDD')

    if (len(str(cidade)) > 100) or (cidade == ""):
        return jsonify({'mensagem': 'A cidade ultrapassou o limite de caracteres ou venho vazio'})
    elif (len(str(uf)) > 2) or (uf == ""):
        return jsonify({'mensagem': 'a sigla da UF ultrapassou o limite de caracteres ou venho vazio'})
    elif (len(str(ddd)) > 3) or (ddd == ""):
        return jsonify({'mensagem': 'o ddd ultrapassou o limite de caracteres ou venho vazio'})

    campos = []
    campos.append(f"Cidade = '{cidade}'")
    campos.append(f"UF = '{uf}'")
    campos.append(f"DDD = {ddd}")

    # Monta a consulta SQL
    sql = f"UPDATE CIDADE SET {', '.join(campos)} WHERE IBGE = {ibge}"
    cursor.execute(sql)
    conn.commit()

    if cursor.rowcount > 0:
        return jsonify({'mensagem': 'Dados da cidade atualizados com sucesso.'})
    else:
        return jsonify({'mensagem': 'Cidade não encontrada.'}), 404

    cursor.close()
    conn.close()

@app.route('/localidade/<int:ibge>', methods=['DELETE'])
def deletaCidade(ibge):

    sql = f"SELECT * FROM CIDADE WHERE IBGE = {ibge}"
    cursor.execute(sql)
    cidade = cursor.fetchone()

    if cidade is None:
        return jsonify({'mensagem': 'Cidade não encontrada!'})

    # Execute a instrução de exclusão no banco de dados
    sql = f"DELETE FROM CIDADE WHERE IBGE = {ibge}"
    cursor.execute(sql)
    conn.commit()

    return jsonify({'mensagem': 'Cidade deletada!'})

    cursor.close()
    conn.close()

@app.route('/usuario', methods=['POST'])
def insereUsuario():

    dados = request.json

    nome = dados['nome']
    login = dados['login']
    cep = dados['cep']
    numero = dados['numero'] if 'numero' in dados else 0
    complemento = dados['complemento'] if 'complemento' in dados else ""
    telefone = dados['telefone'] if 'telefone' in dados else 0

    #Trata campo nome
    nome = re.sub(r'\d', '', nome)

    # Trata campo CEP
    cep = str(cep).replace("-", "")
    int(cep)

    #Trata campo telefone
    telefone = re.sub(r'\D', "", str(telefone))


    #Valida cada campo do JSON
    if (len(str(nome)) > 100 or (nome == "")):
        return jsonify({'mensagem': f'Quantidade de caracteres maior que o permitido ou vazio no campo {nome}'})
    elif (len(str(login)) > 20 or (login == "")):
        return jsonify({'mensagem': f'Quantidade de caracteres maior que o permitido ou vazio no campo {login}'})
    elif (len(str(cep)) > 8 or (cep == "")):
        return jsonify({'mensagem': f'Quantidade de digitos maior que o permitido ou vazio no campo {cep}'})
    elif (len(str(complemento)) > 25):
        return jsonify({'mensagem': f'Quantidade de caracteres maior que o permitido no campo {complemento}'})

    sql = f"SELECT 1 FROM USUARIO WHERE LOGIN = '{login}' "
    cursor.execute(sql)
    sql_result = cursor.fetchall()

    if (sql_result):
        return jsonify({'mensagem': 'Este usuario já existe'})

    sql = f"SELECT 1 FROM CEP WHERE CEP = {cep};"
    cursor.execute(sql)
    sql_result = cursor.fetchall()

    if (not sql_result):
        return jsonify({'mensagem': 'Este cep não existe na base!'})

    sql = f"""INSERT INTO USUARIO (nome, login, cep, numero, complemento, telefone) 
                          VALUES ('{nome}', '{login}', {cep}, {numero}, '{complemento}',{telefone}) """

    cursor.execute(sql)
    conn.commit()
    return jsonify({'mensagem': 'Usuario cadastrado!'})

    cursor.close()
    conn.close()

@app.route ('/usuario/<int:id>', methods=['GET'])
def obtemUsuario(id):
    sql = f"SELECT * FROM USUARIO WHERE ID = {id}"
    cursor.execute(sql)
    sql_result = cursor.fetchone()

    if (sql_result):
        cidade = {
            'Nome': sql_result[0],
            'Login': sql_result[1],
            'CEP': sql_result[2],
            'Numero': sql_result[3],
            'Complemento': sql_result[4],
            'Telefone': sql_result[5]
        }
        return jsonify(cidade)
    else:
        return jsonify({'mensagem': 'Usuario não encontrado.'}), 404

    cursor.close()
    conn.close()

if __name__ == '__main__':
    app.run()
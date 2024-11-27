from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL, MySQLdb
import pandas as pd
import os
from flask_cors import CORS  # Importa CORS
from dotenv import load_dotenv
import bcrypt
from werkzeug.utils import secure_filename
from test_couchdb import test_couchdb_connection


# Carregar variáveis do arquivo .env
load_dotenv()

# Inicializar o aplicativo Flask
app = Flask(__name__)
CORS(app)  # Habilita CORS para todas as rotas

# Define o diretório onde os uploads serão salvos temporariamente
UPLOAD_FOLDER = './uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Cria a pasta de uploads, se não existir
import os
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Configuração do banco de dados usando variáveis de ambiente
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PORT'] = int(os.getenv('MYSQL_PORT', 3306))  # Padrão para 3306 se a variável não existir
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')
app.secret_key = os.getenv('SECRET_KEY')  # Adiciona a chave secreta da sessão

# Verifique se todas as variáveis estão carregadas
if not all([app.config['MYSQL_HOST'], app.config['MYSQL_USER'], app.config['MYSQL_PASSWORD'], app.config['MYSQL_DB'], app.secret_key]):
    raise ValueError("Configuração do banco de dados ou SECRET_KEY não encontrada nas variáveis de ambiente.")

# Inicializar a extensão MySQL com o app configurado
mysql = MySQL(app)
# Função auxiliar para verificar se o usuário está logado
def is_logged_in():
    return 'logged_in' in session

# Função auxiliar para verificar se o usuário é gerente
def is_manager():
    return is_logged_in() and session.get('role') == 'gerente'

# Rota de login
# Função de Login com bcrypt
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Verifica as credenciais no banco de dados
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()

        if user and bcrypt.checkpw(password.encode('utf-8'), user[2].encode('utf-8')):
            # Login bem-sucedido
            session['logged_in'] = True
            session['username'] = user[1]
            session['role'] = user[4]
            flash("Login realizado com sucesso!", "success")
            return redirect(url_for('index'))
        else:
            # Login falhou
            flash("Credenciais inválidas. Tente novamente.", "error")
            return redirect(url_for('login'))
    return render_template('login.html')

# Rota de registro
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        role = request.form.get('role')  # Captura o papel selecionado

        # Verifica se as senhas correspondem
        if password != confirm_password:
            flash("As senhas não correspondem.")
            return render_template('register.html')

        # Verifica se o usuário já existe
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s OR email = %s", (username, email))
        existing_user = cursor.fetchone()

        if existing_user:
            flash("Nome de usuário ou email já estão em uso.")
            return render_template('register.html')

        # Verifica se o papel foi selecionado
        if not role:
            flash("Selecione o papel (gerente ou técnico).")
            return render_template('register.html')

        # Criptografa a senha usando bcrypt
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Insere o novo usuário no banco de dados
        try:
            cursor.execute("INSERT INTO users (username, password, email, role) VALUES (%s, %s, %s, %s)",
                           (username, hashed_password.decode('utf-8'), email, role))
            mysql.connection.commit()
            cursor.close()
            flash("Usuário registrado com sucesso!")
            return redirect(url_for('login'))
        except Exception as e:
            app.logger.error(f"Erro ao registrar usuário: {e}")
            flash("Erro ao registrar. Tente novamente.")
            return render_template('register.html')

    return render_template('register.html')


@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        email = request.form['email']

        # Verifica se o email está cadastrado
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s", [email])
        user = cursor.fetchone()
        cursor.close()

        if user:
            # Aqui, você enviaria um email com instruções de redefinição
            # Para simplificar, vamos supor que a senha é redefinida para 'nova_senha'
            new_password = 'nova_senha'
            hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())

            # Atualiza a senha no banco de dados
            cursor = mysql.connection.cursor()
            cursor.execute("UPDATE users SET password = %s WHERE email = %s",
                           (hashed_password.decode('utf-8'), email))
            mysql.connection.commit()
            cursor.close()

            message = "Uma nova senha foi enviada para o seu email."
            return render_template('reset_password.html', message=message)
        else:
            message = "Email não encontrado."
            return render_template('reset_password.html', message=message)

    return render_template('reset_password.html')

# Rota de upload de planilha
@app.route('/upload_planilha', methods=['GET', 'POST'])
def upload_planilha():
    if request.method == 'POST':
        file = request.files['file']
        if file and file.filename.endswith('.xlsx'):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            try:
                # Carrega a planilha com pandas
                df = pd.read_excel(file_path)
                data = df.to_dict(orient='records')

                # Insere dados no banco de dados
                cursor = mysql.connection.cursor()
                for row in data:
                    cursor.execute("""
                        INSERT INTO tabela_dados (coluna1, coluna2, coluna3)
                        VALUES (%s, %s, %s)
                    """, (row['coluna1'], row['coluna2'], row['coluna3']))
                mysql.connection.commit()
                cursor.close()

                flash('Dados importados com sucesso!', 'success')
            except Exception as e:
                flash(f'Erro ao importar dados: {e}', 'error')
            finally:
                # Remove o arquivo após a importação
                os.remove(file_path)

            return redirect(url_for('index'))
        else:
            flash('Formato de arquivo inválido. Envie um arquivo Excel.', 'error')
            return redirect(request.url)
    return render_template('upload_planilha.html')

# Rota para a página inicial
@app.route('/')
def index():
    if is_logged_in():
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Consulta para contar treinamentos completos, incompletos e total
        cursor.execute("""
            SELECT 
                COUNT(*) AS total_treinamentos,
                SUM(CASE WHEN st.situacao = 'em_dias' THEN 1 ELSE 0 END) AS total_concluidos,
                SUM(CASE WHEN st.situacao = 'vencido' THEN 1 ELSE 0 END) AS total_incompletos
            FROM situacao_treinamento st
        """)
        
        estatisticas = cursor.fetchone()
        
        # Consulta para obter dados de treinamento por mês (usado nos gráficos)
        cursor.execute("""
            SELECT 
                MONTH(t.data) AS mes, 
                SUM(CASE WHEN st.situacao = 'em_dias' THEN 1 ELSE 0 END) AS completos,
                SUM(CASE WHEN st.situacao = 'vencido' THEN 1 ELSE 0 END) AS incompletos
            FROM situacao_treinamento st
            JOIN treinamentos t ON st.treinamento_id = t.id
            GROUP BY MONTH(t.data)
            ORDER BY MONTH(t.data)
        """)
        
        dados_situacao = cursor.fetchall()

        situacao_labels = []
        completos_data = []
        incompletos_data = []

        for row in dados_situacao:
            situacao_labels.append(f'Mês {row["mes"]}')
            completos_data.append(row['completos'] or 0)
            incompletos_data.append(row['incompletos'] or 0)
        
        # Consulta para calcular o percentual de conformidade por colaborador
        cursor.execute("""
            SELECT 
                c.nome, 
                COUNT(CASE WHEN st.situacao = 'em_dias' THEN 1 END) / COUNT(*) * 100 AS percentual_conformidade
            FROM colaboradores c
            JOIN situacao_treinamento st ON c.id = st.colaborador_id
            GROUP BY c.nome
        """)
        
        dados_conformidade = cursor.fetchall()

        nomes_colaboradores = []
        percentuais_conformidade = []

        for row in dados_conformidade:
            nomes_colaboradores.append(row['nome'])
            percentuais_conformidade.append(row['percentual_conformidade'] or 0)

        cursor.close()
        
        return render_template(
            'index.html',
            username=session.get('username'),
            role=session.get('role'),
            situacao_labels=situacao_labels,
            completos_data=completos_data,
            incompletos_data=incompletos_data,
            nomes_colaboradores=nomes_colaboradores,
            percentuais_conformidade=percentuais_conformidade,
            total_treinamentos=estatisticas['total_treinamentos'],
            total_concluidos=estatisticas['total_concluidos'],
            total_incompletos=estatisticas['total_incompletos'],
            current_year=2024
        )

    return redirect(url_for('login'))


# Rota de logout
@app.route('/logout')
def logout():
    session.clear()  # Limpa a sessão do usuário
    return redirect(url_for('login'))

# Rota para visualizar treinamentos
@app.route('/visualizar_treinamentos')
def visualizar_treinamentos():
    if is_logged_in():
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id, titulo, descricao, data, status, participantes, responsavel, local FROM treinamentos")
        treinamentos = cursor.fetchall()
        cursor.close()
        return render_template('visualizar_treinamentos.html', treinamentos=treinamentos)
    return redirect(url_for('login'))


# Rota para inserir um treinamento
@app.route('/inserir_treinamento', methods=['GET', 'POST'])
def inserir_treinamento():
    if is_manager():
        if request.method == 'POST':
            titulo = request.form['titulo']
            descricao = request.form['descricao']
            data = request.form['data']
            status = request.form['status']  # Novo campo
            participantes = request.form['participantes']  # Novo campo
            responsavel = request.form['responsavel']  # Novo campo
            local = request.form['local']  # Novo campo
            cursor = mysql.connection.cursor()
            cursor.execute("INSERT INTO treinamentos (titulo, descricao, data, status, participantes, responsavel, local) VALUES (%s, %s, %s, %s, %s, %s, %s)", 
                           (titulo, descricao, data, status, participantes, responsavel, local))
            mysql.connection.commit()
            cursor.close()
            return redirect(url_for('visualizar_treinamentos'))
        return render_template('inserir_treinamento.html')
    return "Acesso negado", 403


# Rota para alterar um treinamento
@app.route('/alterar_treinamento/<int:id>', methods=['GET', 'POST'])
def alterar_treinamento(id):
    if is_manager():
        cursor = mysql.connection.cursor()
        if request.method == 'POST':
            titulo = request.form['titulo']
            descricao = request.form['descricao']
            data = request.form['data']
            status = request.form['status']  # Novo campo
            participantes = request.form['participantes']  # Novo campo
            responsavel = request.form['responsavel']  # Novo campo
            local = request.form['local']  # Novo campo
            cursor.execute("UPDATE treinamentos SET titulo = %s, descricao = %s, data = %s, status = %s, participantes = %s, responsavel = %s, local = %s WHERE id = %s", 
                           (titulo, descricao, data, status, participantes, responsavel, local, id))
            mysql.connection.commit()
            cursor.close()
            return redirect(url_for('visualizar_treinamentos'))
        cursor.execute("SELECT * FROM treinamentos WHERE id = %s", (id,))
        treinamento = cursor.fetchone()
        cursor.close()
        return render_template('alterar_treinamento.html', treinamento=treinamento)
    return "Acesso negado", 403


# Rota para excluir um treinamento
@app.route('/excluir_treinamento/<int:id>', methods=['GET', 'POST'])
def excluir_treinamento(id):
    if is_manager():
        if request.method == 'POST':
            cursor = mysql.connection.cursor()
            cursor.execute("DELETE FROM treinamentos WHERE id = %s", (id,))
            mysql.connection.commit()
            cursor.close()
            return redirect(url_for('visualizar_treinamentos'))
        return render_template('excluir_treinamento.html', id=id)
    return "Acesso negado", 403

# Rota para visualizar técnicos
@app.route('/visualizar_tecnicos')
def visualizar_tecnicos():
    if is_logged_in():
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM tecnicos")
        tecnicos = cursor.fetchall()
        cursor.close()
        return render_template('visualizar_tecnicos.html', tecnicos=tecnicos)
    return redirect(url_for('login'))


# Rota para inserir um técnico
@app.route('/inserir_tecnico', methods=['GET', 'POST'])
def inserir_tecnico():
    if is_manager():
        if request.method == 'POST':
            nome = request.form['nome']
            email = request.form['email']
            telefone = request.form['telefone']
            setor = request.form['setor']
            cursor = mysql.connection.cursor()
            cursor.execute("INSERT INTO tecnicos (nome, email, telefone, setor) VALUES (%s, %s, %s, %s)", (nome, email, telefone, setor))
            mysql.connection.commit()
            cursor.close()
            return redirect(url_for('visualizar_tecnicos'))
        return render_template('inserir_tecnico.html')
    return "Acesso negado", 403

# Rota para alterar um técnico
@app.route('/alterar_tecnico/<int:id>', methods=['GET', 'POST'])
def alterar_tecnico(id):
    if is_manager():
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if request.method == 'POST':
            nome = request.form['nome']
            email = request.form['email']
            telefone = request.form['telefone']
            setor = request.form['setor']
            cursor.execute("UPDATE tecnicos SET nome = %s, email = %s, telefone = %s, setor = %s WHERE id = %s", (nome, email, telefone, setor, id))
            mysql.connection.commit()
            cursor.close()
            return redirect(url_for('visualizar_tecnicos'))
        cursor.execute("SELECT * FROM tecnicos WHERE id = %s", (id,))
        tecnico = cursor.fetchone()
        cursor.close()
        return render_template('alterar_tecnico.html', tecnico=tecnico)
    return "Acesso negado", 403

# Rota para excluir um técnico
@app.route('/excluir_tecnico/<int:id>', methods=['GET', 'POST'])
def excluir_tecnico(id):
    if is_manager():
        if request.method == 'POST':
            cursor = mysql.connection.cursor()
            cursor.execute("DELETE FROM tecnicos WHERE id = %s", (id,))
            mysql.connection.commit()
            cursor.close()
            return redirect(url_for('visualizar_tecnicos'))
        return render_template('excluir_tecnico.html', id=id)
    return "Acesso negado", 403

from flask_mysqldb import MySQLdb

# Rota para consultar a situação do colaborador
@app.route('/consultar_situacao', methods=['POST'])
def consultar_situacao():
    consulta = request.form['consulta']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)  # Usa DictCursor para resultados como dicionários
    query = """
        SELECT c.nome, c.funcao, t.titulo AS treinamento, s.situacao 
        FROM colaboradores c
        JOIN situacao_treinamento s ON c.id = s.colaborador_id
        JOIN treinamentos t ON s.treinamento_id = t.id
        WHERE c.nome LIKE %s OR c.matricula = %s
    """
    cursor.execute(query, (f"%{consulta}%", consulta))
    resultados = cursor.fetchall()
    cursor.close()
    
    # Retorna o template com resultados
    return render_template('situacao.html', resultados=resultados)

@app.route('/listar_tecnicos')
def listar_tecnicos():
    if is_manager():
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM tecnicos")
        tecnicos = cursor.fetchall()
        cursor.close()
        return render_template('alterar_tecnico.html', tecnicos=tecnicos)
    return "Acesso negado", 403

@app.route('/test_couchdb', methods=['GET'])
def test_couchdb():
    message, databases = test_couchdb_connection()
    return render_template(
        'test_couchdb.html',
        message=message,
        databases=databases
    )

# Executa o app
if __name__ == '__main__':
    app.run(debug=True)

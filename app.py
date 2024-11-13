from flask import Flask, render_template, request, redirect, url_for, session,  flash
from flask_mysqldb import MySQL, MySQLdb
import hashlib, bcrypt

app = Flask(__name__)

# Configuração do banco de dados
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PORT'] = 
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = ''
mysql = MySQL(app)

# Chave secreta para gerenciamento de sessão
app.secret_key = 'your_secret_key_here'

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


# Rota para a página inicial
@app.route('/')
def index():
    if is_logged_in():
        # Exibe o dashboard principal com as opções para acessar outras funcionalidades
        return render_template('index.html', username=session.get('username'), role=session.get('role'))
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
        cursor.execute("SELECT * FROM treinamentos")
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
            cursor = mysql.connection.cursor()
            cursor.execute("INSERT INTO treinamentos (titulo, descricao, data) VALUES (%s, %s, %s)", (titulo, descricao, data))
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
            cursor.execute("UPDATE treinamentos SET titulo = %s, descricao = %s, data = %s WHERE id = %s", (titulo, descricao, data, id))
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


# Executa o app
if __name__ == '__main__':
    app.run(debug=True)

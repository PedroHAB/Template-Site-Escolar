# Importações necessárias para o funcionamento da aplicação web em Flask
from functools import wraps # Utilizado para preservar metadados da função original no decorador
from flask import (
    Flask, render_template, request, redirect, url_for, session, flash
) # Módulos essenciais do Flask: app, renderização, requisições, redirecionamento, sessão e mensagens flash
import psycopg2 # Adaptador para conexão e interação com o banco de dados PostgreSQL
from flask_bcrypt import Bcrypt # Biblioteca para hash seguro de senhas
import base64 # Utilizado para codificar dados binários (imagens) em formato Base64 para exibição em HTML

# ---------------------- CONFIGURAÇÃO E INICIALIZAÇÃO ----------------------

# Inicialização da aplicação Flask
app = Flask(__name__)
# Chave secreta obrigatória para gerenciar sessões (cookies) de forma segura e usar mensagens flash
app.secret_key = 'chave-secreta'
# Inicializa o Bcrypt, associando-o à instância do app
bcrypt = Bcrypt(app)

# Função para estabelecer a conexão com o banco de dados PostgreSQL
def get_db_connection():
    """
    Retorna um objeto de conexão para o banco de dados 'usuarios_db'.
    As credenciais de acesso (host, database, user, password) estão hardcoded.
    """
    return psycopg2.connect(
        host="localhost",
        database="usuarios_db",
        user="postgres",
        password="postgres"
    )

# ---------------------- DECORADOR DE AUTENTICAÇÃO ----------------------

def login_required(f):
    """
    Decorador para proteger rotas.
    Verifica se a chave 'usuario' existe na sessão. Se não, redireciona para a rota de login.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario' not in session:
            # Redireciona para o login se o usuário não estiver autenticado
            return redirect(url_for('login'))
        # Executa a função da rota original se a sessão estiver ativa
        return f(*args, **kwargs)
    return decorated_function

# ---------------------- ROTAS PRINCIPAIS DE AUTENTICAÇÃO ----------------------

@app.route('/')
def home():
    """
    Rota da página inicial (pública).
    Se o usuário já estiver logado, redireciona diretamente para o painel de controle.
    """
    if 'usuario' in session:
        return redirect(url_for('painel'))
    # Renderiza o template 'home.html' para usuários não logados
    return render_template('paginaInicial.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        matricula = request.form['matricula']
        senha_hashed = bcrypt.generate_password_hash(request.form['senha']).decode('utf-8')

        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute('SELECT id FROM matriculas WHERE NUM = %s', (matricula,))
            matricula_existente = cur.fetchone()

            if not matricula_existente:
                flash('Erro: Matrícula não encontrada no sistema.', 'error')
                return redirect(url_for('cadastro'))

            # Inserção do usuário
            cur.execute(
                'INSERT INTO usuarios (nome, email, senha, matricula) VALUES (%s, %s, %s, %s)',
                (nome, email, senha_hashed, matricula_existente)
            )
            conn.commit()
            flash('Cadastro realizado com sucesso!', 'success')
            return redirect(url_for('login'))

        except Exception as e:
            flash(f'{e}', 'error')
            return redirect(url_for('cadastro'))
        finally:
            cur.close()
            conn.close()

    return render_template('cadastro.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Rota para autenticação de usuários.
    GET: Exibe o formulário.
    POST: Processa o login.
    """
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        conn = get_db_connection()
        cur = conn.cursor()
        # Busca o nome e o hash da senha do usuário pelo e-mail
        cur.execute('SELECT nome, senha FROM usuarios WHERE email = %s', (email,))
        usuario = cur.fetchone()
        cur.close()
        conn.close()

        # Verifica se o usuário foi encontrado E se o hash da senha corresponde à senha fornecida
        if usuario and bcrypt.check_password_hash(usuario[1], senha):
            # Armazena o nome do usuário na sessão para manter o estado de login
            session['usuario'] = usuario[0]
            return redirect(url_for('painel'))
        else:
            # Re-renderiza o formulário com uma mensagem de erro em caso de falha na autenticação
            return render_template('login.html', erro="E-mail ou senha incorretos.")
    # Exibe o formulário de login no método GET
    return render_template('login.html')

@app.route('/painel')
@login_required # Rota protegida
def painel():
    """
    Página de dashboard ou painel de controle, acessível apenas para usuários logados.
    """
    # Renderiza o template, passando o nome do usuário recuperado da sessão
    return render_template('painel.html', usuario=session['usuario'])

# ---------------------- ROTAS DE CADASTRO DE CONTEÚDO ----------------------

@app.route('/cadastro_noticias', methods=['GET', 'POST'])
@login_required # Rota protegida
def cadastro_noticias():
    """
    Rota para cadastrar novas notícias. Suporta o upload de até 4 imagens.
    As imagens são lidas como bytes e salvas diretamente no banco de dados.
    """
    if request.method == 'POST':
        titulo = request.form['titulo']
        subtitulo = request.form['subtitulo']
        corpo = request.form['corpo']

        # Obtém a lista de arquivos enviados no campo 'imagens'
        imagens_files = request.files.getlist('imagens')
        imagens_bytes = []

        # Itera sobre os arquivos (limitando a 4) e lê o conteúdo binário de cada um
        for imagem in imagens_files[:4]:
            if imagem.filename != '':
                # Lê o conteúdo do arquivo em bytes (formato BLOB)
                imagens_bytes.append(imagem.read())

        # Conecta e insere no banco
        conn = get_db_connection()
        cur = conn.cursor()
        # Insere a notícia. A expressão condicional garante que NULL seja inserido se não houver imagens.
        # A coluna 'imagens' no PostgreSQL deve suportar array de bytes (ex: BYTEA[])
        cur.execute(
            "INSERT INTO noticias (titulo, subtitulo, corpo, imagens) VALUES (%s, %s, %s, %s)",
            (titulo, subtitulo, corpo, imagens_bytes if imagens_bytes else None)
        )
        conn.commit()
        cur.close()
        conn.close()

        # Exibe uma mensagem de sucesso na próxima requisição
        flash('Notícia cadastrada com sucesso!', 'success')
        return redirect(url_for('painel'))

    return render_template('cadastro_noticias.html') # Exibe o formulário

@app.route('/cadastro_professores', methods=['GET', 'POST'])
@login_required # Rota protegida
def cadastro_professores():
    """
    Rota para cadastrar professores. Suporta o upload de uma única foto.
    A foto é lida como bytes e salva diretamente no banco de dados.
    """
    if request.method == 'POST':
        nome = request.form['nome']
        cargo = request.form['cargo']
        frase = request.form['frase']

        foto = request.files['foto']
        # Lê a foto como bytes se um arquivo válido for fornecido; caso contrário, None
        foto_bytes = foto.read() if foto and foto.filename != '' else None

        # Conecta e insere no banco
        conn = get_db_connection()
        cur = conn.cursor()
        # Insere o professor, salvando a foto no formato BLOB
        cur.execute(
            "INSERT INTO professores (nome, cargo, frase, foto) VALUES (%s, %s, %s, %s)",
            (nome, cargo, frase, foto_bytes)
        )
        conn.commit()
        cur.close()
        conn.close()

        flash('Professor cadastrado com sucesso!', 'success')
        return redirect(url_for('painel'))

    return render_template('cadastro_professores.html') # Exibe o formulário

# ---------------------- ROTAS DE LISTAGEM E EXIBIÇÃO ----------------------

@app.route('/professores')
@login_required # Rota protegida
def listar_professores():
    """
    Rota para listar todos os professores cadastrados e preparar suas fotos para exibição.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    # Busca todos os dados dos professores
    cur.execute("SELECT id, nome, cargo, frase, foto FROM professores ORDER BY nome")
    professores = cur.fetchall()
    cur.close()
    conn.close()

    professores_formatados = []
    # Itera sobre os resultados para converter o campo binário 'foto' para Base64
    for prof in professores:
        imagem_base64 = None
        if prof[4]:  # Verifica se o campo foto (índice 4) contém dados
            # Codifica os bytes da imagem para Base64 e decodifica para string UTF-8
            imagem_base64 = base64.b64encode(prof[4]).decode('utf-8')
        
        # Cria um dicionário formatado para ser mais fácil de usar no template Jinja
        professores_formatados.append({
            'id': prof[0],
            'nome': prof[1],
            'cargo': prof[2],
            'frase': prof[3],
            'imagem': imagem_base64 # A string Base64 é usada na tag <img> do HTML
        })

    return render_template('listar_professores.html', professores=professores_formatados)

@app.route('/pgServidores')
def listar_servidores():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT id, nome, cargo, frase, foto FROM professores ORDER BY nome")
    servidores = cur.fetchall()
    cur.close()
    conn.close()

    servidores_formatados = []
    # Itera sobre os resultados para converter o campo binário 'foto' para Base64
    for prof in servidores:
        imagem_base64 = None
        if prof[4]:  # Verifica se o campo foto (índice 4) contém dados
            # Codifica os bytes da imagem para Base64 e decodifica para string UTF-8
            imagem_base64 = base64.b64encode(prof[4]).decode('utf-8')
        
        # Cria um dicionário formatado para ser mais fácil de usar no template Jinja
        servidores_formatados.append({
            'id': prof[0],
            'nome': prof[1],
            'cargo': prof[2],
            'frase': prof[3],
            'imagem': imagem_base64 # A string Base64 é usada na tag <img> do HTML
        })

    return render_template('pgServidores.html', professores=servidores_formatados)

@app.route('/pgNoticias')
def listar_noticias_Site():
    """
    Rota para listar todas as notícias e converter suas múltiplas imagens para Base64.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    # Busca todas as notícias (a coluna imagens contém um array de BYTEA)
    cur.execute("SELECT id, titulo, subtitulo, corpo, imagens FROM noticias ORDER BY id DESC")
    noticias = cur.fetchall()
    cur.close()
    conn.close()
    
    noticias_formatadas = []
    # Itera sobre os resultados para processar os arrays de imagens
    for noticia in noticias:
        imagens_base64 = []
        if noticia[4]:  # Verifica se o campo imagens (array) contém dados
            # Itera sobre cada item do array de bytes (cada imagem)
            for img in noticia[4]:
                # Codifica cada imagem individualmente para Base64
                imagens_base64.append(base64.b64encode(img).decode('utf-8'))
        
        # Cria o dicionário formatado
        noticias_formatadas.append({
            'id': noticia[0],
            'titulo': noticia[1],
            'subtitulo': noticia[2],
            'corpo': noticia[3],
            'imagens': imagens_base64 # Lista de strings Base64
        })

    return render_template('pgNoticias.html', noticias=noticias_formatadas)

@app.route('/noticias')
@login_required # Rota protegida
def listar_noticias():
    """
    Rota para listar todas as notícias e converter suas múltiplas imagens para Base64.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    # Busca todas as notícias (a coluna imagens contém um array de BYTEA)
    cur.execute("SELECT id, titulo, subtitulo, corpo, imagens FROM noticias ORDER BY id DESC")
    noticias = cur.fetchall()
    cur.close()
    conn.close()
    
    noticias_formatadas = []
    # Itera sobre os resultados para processar os arrays de imagens
    for noticia in noticias:
        imagens_base64 = []
        if noticia[4]:  # Verifica se o campo imagens (array) contém dados
            # Itera sobre cada item do array de bytes (cada imagem)
            for img in noticia[4]:
                # Codifica cada imagem individualmente para Base64
                imagens_base64.append(base64.b64encode(img).decode('utf-8'))
        
        # Cria o dicionário formatado
        noticias_formatadas.append({
            'id': noticia[0],
            'titulo': noticia[1],
            'subtitulo': noticia[2],
            'corpo': noticia[3],
            'imagens': imagens_base64 # Lista de strings Base64
        })

    return render_template('listar_noticias.html', noticias=noticias_formatadas)

@app.route('/logout')
def logout():
    """
    Rota de logout. Remove a chave 'usuario' da sessão e encerra a autenticação.
    """
    session.pop('usuario', None)
    return redirect(url_for('home')) # Redireciona para a página inicial

# ---------------------------------------------------

if __name__ == '__main__':
    # Bloco padrão para rodar a aplicação em modo de desenvolvimento
    app.run(debug=True)
from flask import (
    Flask, 
    render_template, 
    request, 
    send_file, 
    session,        # Importado para gerenciar sessões
    redirect,       # Importado para redirecionar usuários
    url_for,        # Importado para construir URLs
    flash           # Importado para exibir mensagens (ex: "Login falhou")
)
from io import BytesIO
import os

# Inicializa o Flask
app = Flask(__name__)

# !!! IMPORTANTE: Chave Secreta !!!
# Sessões do Flask exigem uma 'secret_key' para funcionar com segurança.
# Troque esta chave por algo aleatório e complexo em produção.
app.secret_key = 'sua_chave_secreta_muito_forte_aqui_12345'

# Configura o limite máximo de tamanho de arquivo
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB

# --- Configuração de Autenticação Simples ---
# Em um app real, isso viria de um banco de dados.
# Para este exemplo, vamos "hardcodar" (fixar no código).
USUARIO_VALIDO = "admin"
SENHA_VALIDA = "senha123"  # Mude esta senha!
# ---------------------------------------------


# A lógica de formatação (mantida - sem alterações)
def formatar_dados(dados_brutos):
    """Processa a string de dados, enumera e formata."""
    # Divide os dados brutos em uma lista de linhas
    # Usa decode('utf-8') para lidar com o conteúdo do arquivo
    lista_dados = [linha.strip() for linha in dados_brutos.splitlines() if linha.strip()]
    
    dados_formatados = []

    for indice, linha_dado in enumerate(lista_dados):
        numero_item = indice + 1
        num_formatado = f"{numero_item:02d}."
        
        try:
            primeiro_ponto_e_virgula = linha_dado.find(';')
            
            if primeiro_ponto_e_virgula != -1:
                cpf_e_separador = linha_dado[:primeiro_ponto_e_virgula + 1]
                restante_da_linha = linha_dado[primeiro_ponto_e_virgula + 1:] 
                
                # Formatação com a linha extra no final
                nova_linha = (
                    f"{num_formatado} {cpf_e_separador}{restante_da_linha.strip()};;\n"
                    f"Telefone:\n" 
                    f"======================================\n\n\n"
                )
            else:
                 nova_linha = (
                    f"{num_formatado} {linha_dado.strip()};;\n\n"
                    f"Telefone:\n"
                    f"======================================\n\n\n"
                )
        except Exception:
             nova_linha = (
                f"{num_formatado} {linha_dado.strip()};;\n"
                f"Telefone:\n"
                f"======================================\n\n\n"
            )

        dados_formatados.append(nova_linha)

    return "".join(dados_formatados)

# --- Novas Rotas de Autenticação ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Exibe a página de login e processa o formulário."""
    # Se o usuário já estiver logado, redireciona para o index
    if session.get('logged_in'):
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Verifica as credenciais
        if username == USUARIO_VALIDO and password == SENHA_VALIDA:
            # Credenciais corretas: armazena na sessão
            session['logged_in'] = True
            flash('', 'success') # Mensagem de sucesso
            return redirect(url_for('index'))
        else:
            # Credenciais erradas: exibe erro
            flash('', 'danger')
            
    # Se for GET ou se o login falhar, exibe a página de login
    return render_template('login.html')


@app.route('/logout')
def logout():
    """Remove o usuário da sessão (faz logout)."""
    session.pop('logged_in', None) # Remove a chave da sessão
    flash('Você foi desconectado.', 'info') # Mensagem de aviso
    return redirect(url_for('login'))

# -------------------------------------


@app.route('/', methods=['GET', 'POST'])
def index():
    # !!! VERIFICAÇÃO DE AUTENTICAÇÃO !!!
    # Esta é a proteção principal. Se 'logged_in' não estiver na sessão,
    # o usuário é enviado para a página de login.
    if not session.get('logged_in'):
        return redirect(url_for('login'))
        
    # --- O restante do seu código original continua abaixo ---
    
    if request.method == 'POST':
        # Verifica se o arquivo foi incluído no request
        if 'arquivo_dados' not in request.files:
            flash("", "danger")
            return redirect(request.url) # Recarrega a página

        arquivo = request.files['arquivo_dados']

        # Verifica se o nome do arquivo está vazio
        if arquivo.filename == '':
            flash("", "warning")
            return redirect(request.url)
        
        # Opcional: Verifica a extensão
        if not arquivo.filename.lower().endswith('.txt'):
            flash("Por favor, envie apenas arquivos .txt.", "danger")
            return redirect(request.url)

        try:
            # 1. Lê o conteúdo do arquivo
            dados_brutos = arquivo.read().decode('utf-8') 
            
            if not dados_brutos.strip():
                flash("O arquivo está vazio.", "warning")
                return redirect(request.url)

            # 2. Processa os dados
            dados_saida_formatados = formatar_dados(dados_brutos)
            
            # 3. Prepara para download
            memoria_arquivo = BytesIO()
            memoria_arquivo.write(dados_saida_formatados.encode('utf-8'))
            memoria_arquivo.seek(0)
            
            # 4. Retorna o arquivo formatado para download
            return send_file(
                memoria_arquivo,
                mimetype='text/plain',
                as_attachment=True,
                download_name='lista_formatada.txt'
            )

        except Exception as e:
            flash(f"Erro no processamento do arquivo: {e}", "danger")
            return redirect(request.url)
    
    # Se for um GET (primeira vez acessando), apenas carrega o template
    return render_template('index.html')


if __name__ == '__main__':
    # Roda o servidor na porta 5000
    app.run(debug=True)
from flask import Flask, render_template, request, send_file
from io import BytesIO
import os

# Inicializa o Flask
app = Flask(__name__)

# Configura o limite máximo de tamanho de arquivo (opcional, mas recomendado)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB

# A lógica de formatação (mantida)
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


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Verifica se o arquivo foi incluído no request
        if 'arquivo_dados' not in request.files:
            return render_template('index.html', erro="Nenhum arquivo enviado.", resultado_pronto=None)

        arquivo = request.files['arquivo_dados']

        # Verifica se o nome do arquivo está vazio (caso o usuário clique em enviar sem escolher)
        if arquivo.filename == '':
            return render_template('index.html', erro="Nenhum arquivo selecionado.", resultado_pronto=None)
        
        # Opcional: Verifica a extensão (só permite .txt)
        if arquivo.filename.rsplit('.', 1)[1].lower() != 'txt':
            return render_template('index.html', erro="Por favor, envie apenas arquivos .txt.", resultado_pronto=None)

        try:
            # 1. Lê o conteúdo do arquivo
            # read() retorna bytes. decode('utf-8') converte para string.
            dados_brutos = arquivo.read().decode('utf-8') 
            
            if not dados_brutos.strip():
                return render_template('index.html', erro="O arquivo está vazio.", resultado_pronto=None)

            # 2. Processa os dados
            dados_saida_formatados = formatar_dados(dados_brutos)
            
            # 3. Armazena o resultado formatado em uma sessão para download
            # Como a sessão do Flask tem limite de tamanho, o ideal é retornar o arquivo
            # diretamente no POST para download, mas a visualização exige um truque.
            
            # Para simplificar a visualização, vamos apenas retornar a visualização.
            # O download será feito na mesma rota.

            # Cria um objeto BytesIO para simular o arquivo formatado
            memoria_arquivo = BytesIO()
            memoria_arquivo.write(dados_saida_formatados.encode('utf-8'))
            memoria_arquivo.seek(0)
            
            # Retorna o arquivo formatado para download imediato (o mais limpo)
            return send_file(
                memoria_arquivo,
                mimetype='text/plain',
                as_attachment=True,
                download_name='lista_formatada.txt'
            )

        except Exception as e:
            return render_template('index.html', erro=f"Erro no processamento do arquivo: {e}", resultado_pronto=None)
    
    # Se for um GET (primeira vez acessando), apenas carrega o template
    return render_template('index.html', resultado_pronto=None, erro=None)


if __name__ == '__main__':
    # Roda o servidor na porta 5000
    app.run(debug=True)
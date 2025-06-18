from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
import os

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        'mensagem': 'API de Consulta de CA Online',
        'exemplo': '/consulta-ca/41036'
    })

@app.route('/consulta-ca/<int:ca_num>', methods=['GET'])
def consulta_ca(ca_num):
    url = f'https://consultaca.com/{ca_num}'
    headers = {'User-Agent': 'Mozilla/5.0'}

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return jsonify({'erro': f'CA {ca_num} não encontrado'}), 404

    soup = BeautifulSoup(response.text, 'html.parser')
    result = {}

    try:
        campos = {
            'Nome do Equipamento': 'nome_epi',
            'Nome do Fabricante': 'fabricante',
            'Situação': 'situacao',
            'Validade': 'validade'
        }

        for li in soup.select('li'):
            texto = li.get_text(strip=True)
            for label, chave in campos.items():
                if texto.startswith(label + ":"):
                    result[chave] = texto.split(":", 1)[1].strip()

        if not result:
            return jsonify({'erro': 'Dados não encontrados na página.'}), 500

        result['ca'] = ca_num
        return jsonify(result)

    except Exception as e:
        return jsonify({'erro': 'Erro ao processar a resposta', 'detalhes': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Porta fornecida pelo Render
    app.run(host='0.0.0.0', port=port)

from flask import Flask, render_template, request, jsonify
from datetime import datetime
import json
import os

app = Flask(__name__)

# Caminhos dos arquivos JSON
CATEGORIAS_FILE = "categorias.json"
ORCAMENTOS_FILE = "orcamentos.json"
LANCAMENTOS_FILE = "lancamentos.json"

# Funções utilitárias
def carregar_dados(arquivo):
    if os.path.exists(arquivo):
        with open(arquivo, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def salvar_dados(arquivo, dados):
    with open(arquivo, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

# Carregar dados ao iniciar
categorias = carregar_dados(CATEGORIAS_FILE)
orcamentos = carregar_dados(ORCAMENTOS_FILE)
lancamentos = carregar_dados(LANCAMENTOS_FILE)

# Gerar IDs automáticos
def proximo_id(lista):
    return max([item["id"] for item in lista], default=0) + 1

# ROTAS PRINCIPAIS

from flask import redirect

@app.route("/")
def redirecionar_para_lancamentos():
    return redirect("/lancamentos")

@app.route("/categorias")
def categorias_view():
    return render_template("cadastro.html", categorias=categorias)

@app.route("/nova_categoria", methods=["POST"])
def nova_categoria():
    nome = request.form.get("nome")
    nova = {"id": proximo_id(categorias), "nome": nome}
    categorias.append(nova)
    salvar_dados(CATEGORIAS_FILE, categorias)
    return jsonify({"status": "ok"})

@app.route("/excluir_categoria", methods=["POST"])
def excluir_categoria():
    categoria_id = int(request.form.get("categoria_id"))
    global categorias
    categorias = [c for c in categorias if c["id"] != categoria_id]
    salvar_dados(CATEGORIAS_FILE, categorias)
    return jsonify({"status": "ok"})

@app.route("/editar_categoria", methods=["POST"])
def editar_categoria():
    categoria_id = int(request.form.get("categoria_id"))
    novo_nome = request.form.get("novo_nome")
    for c in categorias:
        if c["id"] == categoria_id:
            c["nome"] = novo_nome
            break
    salvar_dados(CATEGORIAS_FILE, categorias)
    return jsonify({"status": "ok"})

@app.route("/orcamentos")
def orcamentos_view():
    return render_template("orcamentos.html", categorias=categorias)

@app.route("/novo_orcamento", methods=["POST"])
def novo_orcamento():
    categoria = request.form.get("categoria")
    mes = request.form.get("mes")
    ano = int(request.form.get("ano"))
    valor = float(request.form.get("valor"))

    novo = {
        "id": proximo_id(orcamentos),
        "categoria": categoria,
        "mes": mes,
        "ano": ano,
        "valor": valor
    }
    orcamentos.append(novo)
    salvar_dados(ORCAMENTOS_FILE, orcamentos)
    return jsonify({"status": "ok"})

@app.route("/ver_orcamentos")
def ver_orcamentos():
    return render_template("ver_orcamentos.html", orcamentos=orcamentos)

@app.route("/excluir_orcamento", methods=["POST"])
def excluir_orcamento():
    orcamento_id = int(request.form.get("orcamento_id"))
    global orcamentos
    orcamentos = [o for o in orcamentos if o["id"] != orcamento_id]
    salvar_dados(ORCAMENTOS_FILE, orcamentos)
    return jsonify({"status": "ok"})

@app.route("/editar_orcamento", methods=["POST"])
def editar_orcamento():
    orcamento_id = int(request.form.get("orcamento_id"))
    categoria = request.form.get("categoria")
    mes = request.form.get("mes")
    valor = float(request.form.get("valor"))
    for o in orcamentos:
        if o["id"] == orcamento_id:
            o["categoria"] = categoria
            o["mes"] = mes
            o["valor"] = valor
            break
    salvar_dados(ORCAMENTOS_FILE, orcamentos)
    return jsonify({"status": "ok"})

@app.route("/lancamentos")
def lancamentos_view():
    return render_template("lancamentos.html", categorias=categorias)

@app.route("/novo_lancamento", methods=["POST"])
def novo_lancamento():
    categoria = request.form.get("categoria")
    data_str = request.form.get("data")
    tipo = request.form.get("tipo")
    descricao = request.form.get("descricao", "")
    valor_total = float(request.form.get("valor"))
    parcelado = request.form.get("parcelado") == "on"
    parcelas = int(request.form.get("parcelas") or 1)

    data_obj = datetime.strptime(data_str, "%Y-%m-%d")
    meses_lista = ["janeiro", "fevereiro", "março", "abril", "maio", "junho",
                   "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
    mes_index = data_obj.month - 1
    ano = data_obj.year
    valor_parcela = round(valor_total / parcelas, 2)

    for i in range(parcelas):
        novo_mes_index = (mes_index + i) % 12
        novo_ano = ano + ((mes_index + i) // 12)
        novo_mes = meses_lista[novo_mes_index]

        nova_descricao = descricao
        if parcelado:
            nova_descricao += f" (parcela {i+1}/{parcelas})"

        novo = {
            "id": proximo_id(lancamentos),
            "categoria": categoria,
            "mes": novo_mes,
            "ano": novo_ano,
            "tipo": tipo,
            "descricao": nova_descricao,
            "valor": valor_parcela,
            "data": data_str
        }
        lancamentos.append(novo)

    salvar_dados(LANCAMENTOS_FILE, lancamentos)
    return jsonify({"status": "ok"})

@app.route("/ver_lancamentos")
def ver_lancamentos():
    return render_template("ver_lancamentos.html", lancamentos=lancamentos)

@app.route("/editar_lancamento", methods=["POST"])
def editar_lancamento():
    lancamento_id = int(request.form.get("lancamento_id"))
    descricao = request.form.get("descricao", "")
    valor = float(request.form.get("valor"))
    for l in lancamentos:
        if l["id"] == lancamento_id:
            l["descricao"] = descricao
            l["valor"] = valor
            break
    salvar_dados(LANCAMENTOS_FILE, lancamentos)
    return jsonify({"status": "ok"})

@app.route("/excluir_lancamento", methods=["POST"])
def excluir_lancamento():
    lancamento_id = int(request.form.get("lancamento_id"))
    global lancamentos
    lancamentos = [l for l in lancamentos if l["id"] != lancamento_id]
    salvar_dados(LANCAMENTOS_FILE, lancamentos)
    return jsonify({"status": "ok"})

@app.route("/dados_graficos")
def dados_graficos():
    mes = request.args.get("mes")
    ano = int(request.args.get("ano"))

    orcamentos_mes = [o for o in orcamentos if o["mes"] == mes and o["ano"] == ano]
    lancamentos_mes = [l for l in lancamentos if l["mes"] == mes and l["ano"] == ano]

    categorias = list(set([o["categoria"] for o in orcamentos_mes] + [l["categoria"] for l in lancamentos_mes]))

    resumo = {
        "orcado": sum(o["valor"] for o in orcamentos_mes),
        "entradas": sum(l["valor"] for l in lancamentos_mes if l["tipo"] == "Entrada"),
        "saidas": sum(l["valor"] for l in lancamentos_mes if l["tipo"] == "Saída"),
        "montantes": sum(l["valor"] for l in lancamentos_mes if l["tipo"] == "Montante")
    }

    comparativo = []
    for cat in categorias:
        orcado = sum(o["valor"] for o in orcamentos_mes if o["categoria"] == cat)
        gasto = sum(l["valor"] for l in lancamentos_mes if l["categoria"] == cat and l["tipo"] == "Saída")
        comparativo.append({
            "nome": cat,
            "orcado": orcado,
            "gasto": gasto
        })

    return jsonify({"resumo": resumo, "categorias": comparativo})

@app.route("/graficos")
def graficos_view():
    return render_template("graficos.html")

# INICIAR SERVIDOR
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

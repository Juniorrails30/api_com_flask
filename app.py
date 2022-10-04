
from itertools import count
from typing import List, Optional

from flask import Flask, jsonify, request
from flask_pydantic_spec import FlaskPydanticSpec, Request, Response
from pydantic import BaseModel, Field
from tinydb import Query, TinyDB

app = Flask(__name__)
spec = FlaskPydanticSpec("flask", title="lutadores")
spec.register(app)
database = TinyDB("database.json")
c = count()


class Pessoa(BaseModel):
    id: Optional[int] = Field(default_factory=lambda: next(c))
    name: str
    idade: int


class Pessoas(BaseModel):
    pessoas: List[Pessoa]
    count: int


@app.get("/pessoas")
@spec.validate(resp=Response(HTTP_200=Pessoas))
def buscar_pessoas():
    """Retorna todas as Pessoas da base de dados."""
    return jsonify(
        Pessoas(
            pessoas=database.all(),
            count=len(database.all())
        ).dict()
    )


@app.get('/pessoas/<int:id>')
@spec.validate(resp=Response(HTTP_200=Pessoa))
def buscar_pessoa(id):
    """Retorna uma Pessoa da base de dados."""
    try:
        pessoa = database.search(Query().id == id)[0]
    except IndexError:
        return {"messagem": "Pessoa não encontrada"}
    return jsonify(pessoa)


@ app.post('/pessoas')
@ spec.validate(body=Request(Pessoa), resp=Response(HTTP_201=Pessoa))
def inserir_pessoas():
    """Insere uma Pessoa no Banco de dados."""
    body = request.context.body.dict()
    database.insert(body)
    return body


@app.put('/pessoas/<int:id>')
@spec.validate(body=Request(Pessoa), resp=Response(HTTP_201=Pessoa))
def altera_pessoa(id):
    """Alterar uma Pessoa no Banco de dados."""
    body = request.context.body.dict()
    database.update(body, Query().id == id)
    return jsonify(body)


@app.delete('/pessoas/<int:id>')
@spec.validate(resp=Response('HTTP_204'))
def deleta_pessoa(id):
    """Remove uma Pessoa no Banco de dados."""
    database.remove(Query().id == id)
    return jsonify({})


if __name__ == '__main__':
    app.run(debug=True)

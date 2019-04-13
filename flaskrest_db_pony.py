from pony.orm import *
from pony.orm.serialization import to_dict

from flask import Flask
from flask_restful import reqparse, Api, Resource

app = Flask(__name__)
api = Api(app)

##
######### Persistência ##########
##
# Criando um banco de dados e seus respectivos recursos

db = Database()

class DB_Tarefa(db.Entity):
    numero_tarefa = PrimaryKey(int)
    descricao = Required(str)
    data = Required(str)

db.bind('sqlite', 'db_test.sqlite', create_db=True)
db.generate_mapping(create_tables=True)
#sql_debug(True)

# O parser será responsável por gerenciar os argumentos passados via requisições Web
parser = reqparse.RequestParser()
parser.add_argument('numero_tarefa', type=int)
parser.add_argument('descricao')
parser.add_argument('data')

##
######### Recursos (usados no Flask_restful) ##########
##
class Inicio(Resource):
    def get(self):
        return {'Tela inicial' : '=)'}

class Lista(Resource):
    def get(self): #retorna a lista com todos os afazeres
        with db_session: # sintaxe alternativa seria @db_session
            return {
                item.numero_tarefa: {
                    'Tarefa' : item.descricao,
                    'Data' : item.data
                }
                for item in DB_Tarefa.select() # essa sintaxe (com select, sem argumentos adicionais) percorre todos os items do tipo db_Tarefa
            }

    def post(self): # permite inserir uma tarefa na lista        
        with db_session:            
            args = parser.parse_args() # gera uma classe do tipo Namespace com os argumentos adicionados anteriormente via add_argument()
            DB_Tarefa(numero_tarefa=args['numero_tarefa'], descricao=args['descricao'], data=args['data'])     
            return ('Tarefa adicionada com sucesso!')

class Tarefa(Resource):
    def get(self, n_tarefa): #retorna informação sobre uma tarefa específica
        with db_session:
            try:            
                # t_query = select(t for t in DB_Tarefa if t.numero_tarefa == n_tarefa)
                t_query = DB_Tarefa[n_tarefa] #sintaxe análoga a linha de cima, mas mais compacta
                tarefa_selecionada = to_dict(t_query)
                return (tarefa_selecionada)
            except ObjectNotFound:    
                return 'Tarefa não encontrada'

    def delete(self, n_tarefa):
        with db_session:
            try:
                tarefa = DB_Tarefa[n_tarefa] # se a tarefa existir no banco de dados, ela será deletada
                if tarefa: # acusa falso se a tarefa requisitada não existir
                    tarefa.delete()
            except ObjectNotFound:
                return 'Tarefa não encontrada'
            
            return 'Tarefa deletada com sucesso'
##
## Configurando os recursos API para os endereços adequados
##

api.add_resource(Inicio, '/')
api.add_resource(Lista, '/lista', endpoint='Lista')
api.add_resource(Tarefa, '/lista/<int:n_tarefa>', endpoint='Tarefa')

if __name__ == '__main__':
    app.run(debug=True)
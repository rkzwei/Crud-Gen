from flask import Flask, request, jsonify
from flask_restx import Api, Resource, fields
import psycopg2

app = Flask(__name__)
api = Api(app, version='1.0', title='API de Alunos', description='API para gerenciar notas, por Gabriel Neves')

# Database Configuration
db_config = {
    "database": "students",
    "user": "postgres",
    "password": "samplepass",
    "host": "db",
    "port": "5432",
}

def establish_db_connection():
    try:
        connection = psycopg2.connect(**db_config)
        return connection
    except psycopg2.Error as e:
        raise Exception(f"Failed to connect to the database: {str(e)}")

def check_tables(table_name, connection):
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = %s);", (table_name,))
        exists = cursor.fetchone()[0]
        cursor.close()
        return exists
    except psycopg2.Error as e:
        raise Exception(f"Database error while checking table existence: {str(e)}")

def create_tables(connection):
    try:
        cursor = connection.cursor()
        cursor.execute('''
            CREATE TABLE students (
                id SERIAL PRIMARY KEY,
                nome TEXT,
                idade INTEGER,
                nota_primeiro_semestre FLOAT,
                nota_segundo_semestre FLOAT,
                nome_professor TEXT,
                numero_sala INTEGER
            )
        ''')
        connection.commit()
        cursor.close()
    except psycopg2.Error as e:
        raise Exception(f"Database error while creating tables: {str(e)}")

@api.route('/alunos', methods=['POST', 'GET'])
class Students(Resource):
    @api.doc('list_students')
    def get(self):
        """
        Listar alunos
        """
        try:
            connection = establish_db_connection()
            cursor = connection.cursor()
            cursor.execute('SELECT * FROM students')
            students = cursor.fetchall()
            cursor.close()

            column_names = [desc[0] for desc in cursor.description]

            student_list = []
            for student in students:
                student_dict = {}
                for i, column_name in enumerate(column_names):
                    student_dict[column_name] = student[i]
                student_list.append(student_dict)
            return student_list
        except Exception as e:
            return {'error': str(e)}, 500

    @api.doc('create_student')
    @api.expect(api.model('Aluno', {
        'nome': fields.String(required=True, description='Nome do Aluno'),
        'idade': fields.Integer(required=True, description='Idade do Aluno'),
        'nota_primeiro_semestre': fields.Float(description='Nota do Primeiro Semestre'),
        'nota_segundo_semestre': fields.Float(description='Nota do Segundo Semestre'),
        'nome_professor': fields.String(description='Nome do Professor'),
        'numero_sala': fields.Integer(description='Numero de Sala')
    }))
    def post(self):
        """
        Criar novo Aluno
        """
        try:
            connection = establish_db_connection()
            data = request.get_json()
            nome = data.get('nome')
            idade = data.get('idade')
            nota_primeiro_semestre = data.get('nota_primeiro_semestre')
            nota_segundo_semestre = data.get('nota_segundo_semestre')
            nome_professor = data.get('nome_professor')
            numero_sala = data.get('numero_sala')

            cursor = connection.cursor()
            cursor.execute('''
                INSERT INTO students (nome, idade, nota_primeiro_semestre, nota_segundo_semestre, nome_professor, numero_sala)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (nome, idade, nota_primeiro_semestre, nota_segundo_semestre, nome_professor, numero_sala))
            connection.commit()
            cursor.close()
            connection.close()
            return {'message': 'Aluno adicionado com sucesso'}
        except Exception as e:
            return {'error': str(e)}, 500

@api.route('/alunos/<int:id>', methods=['GET', 'PUT', 'DELETE'])
class Student(Resource):
    @api.doc('get_student')
    def get(self, id):
        """
        Listar aluno por ID
        """
        try:
            connection = establish_db_connection()
            cursor = connection.cursor()
            cursor.execute('SELECT * FROM students WHERE id = %s', (id,))
            student = cursor.fetchone()
            cursor.close()

            if student:
                column_names = [desc[0] for desc in cursor.description]
                student_dict = {column_names[i]: student[i] for i in range(len(column_names))}
                connection.close()
                return jsonify(student_dict)
            else:
                connection.close()
                return {'message': 'Aluno não encontrado'}, 404
        except Exception as e:
            return {'error': str(e)}, 500

    @api.doc('update_student')
    @api.expect(api.model('Aluno', {
        'nome': fields.String(description='Nome do Aluno'),
        'idade': fields.Integer(description='Idade do Aluno'),
        'nota_primeiro_semestre': fields.Float(description='Nota do Primeiro Semestre'),
        'nota_segundo_semestre': fields.Float(description='Nota do Segundo Semestre'),
        'nome_professor': fields.String(description='Nome do Professor'),
        'numero_sala': fields.Integer(description='Numero de Sala')
    }))
    def put(self, id):
        """
        Atualizar aluno por ID
        """
        try:
            connection = establish_db_connection()
            data = request.get_json()
            updated_data = {
                column_mapping[column]: data.get(column) for column in column_mapping
            }

            cursor = connection.cursor()
            update_db = '''
                UPDATE students
                SET {}
                WHERE id = %s
            '''.format(', '.join(['{} = %s'.format(column) for column in updated_data.keys()]))
            query_values = list(updated_data.values())
            query_values.append(id)

            cursor.execute(update_db, query_values)
            connection.commit()
            cursor.close()
            connection.close()
            return {'message': 'Aluno atualizado com sucesso'}
        except Exception as e:
            return {'error': str(e)}, 500

    @api.doc('delete_student')
    def delete(self, id):
        """
        Deletar aluno por ID
        """
        try:
            connection = establish_db_connection()
            cursor = connection.cursor()
            cursor.execute('DELETE FROM students WHERE id = %s', (id,))
            connection.commit()
            cursor.close()
            connection.close()
            return {'message': 'Aluno deletado com sucesso'}
        except Exception as e:
            return {'error': str(e)}, 500

if __name__ == '__main__':
    connection = establish_db_connection()

    if not check_tables("students", connection):
        create_tables(connection)
    connection.close()

    app.run(debug=True)

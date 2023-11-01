-- Connect to the 'students' database
\c students;

-- Create a table for students
CREATE TABLE students (
    id SERIAL PRIMARY KEY,
    nome TEXT,
    idade INTEGER,
    nota_primeiro_semestre FLOAT,
    nota_segundo_semestre FLOAT,
    nome_professor TEXT,
    numero_sala INTEGER
);
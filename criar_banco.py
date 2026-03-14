import sqlite3

# conecta ou cria o banco
conn = sqlite3.connect("database.db")

cursor = conn.cursor()


# =========================
# TABELA TRABALHADORES
# =========================

cursor.execute("""
CREATE TABLE IF NOT EXISTS trabalhadores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    funcao TEXT,
    valor REAL
)
""")


# =========================
# TABELA PRODUCAO
# =========================

cursor.execute("""
CREATE TABLE IF NOT EXISTS producao (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trabalhador_id INTEGER,
    quantidade INTEGER,
    data DATE DEFAULT CURRENT_DATE
)
""")


# =========================
# TABELA INSUMOS
# =========================

cursor.execute("""
CREATE TABLE IF NOT EXISTS insumos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    valor REAL,
    data DATE DEFAULT CURRENT_DATE
)
""")


# salva alterações
conn.commit()

# fecha banco
conn.close()

print("Banco criado com sucesso!")
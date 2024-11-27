import couchdb

def test_couchdb_connection():
    try:
        # Endereço do servidor CouchDB
        server = couchdb.Server("http://127.0.0.1:5984/")
        # Testa a conexão listando os bancos disponíveis
        databases = list(server)
        print("Conexão ao CouchDB foi bem-sucedida!")
        print(f"Bancos de dados disponíveis: {databases}")
        return "Conexão bem-sucedida ao CouchDB!", databases
    except Exception as e:
        print(f"Erro ao conectar ao CouchDB: {e}")
        return f"Erro ao conectar ao CouchDB: {e}", []

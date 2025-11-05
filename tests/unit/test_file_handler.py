"""
Testes unitários para o FileHandler
"""
import os
import tempfile
import pytest
import pandas as pd
from src.utils.file_handler import FileHandler


class TestFileHandler:
    """
    Testes para a classe FileHandler
    """
    
    def setup_method(self):
        """
        Configuração executada antes de cada teste
        """
        self.file_handler = FileHandler()
        self.temp_dir = tempfile.mkdtemp()
    
    def test_initialization(self):
        """
        Testa a inicialização do FileHandler
        """
        assert self.file_handler.encryption_key is not None
        assert self.file_handler.cipher is not None
    
    def test_save_and_load_key(self):
        """
        Testa salvar e carregar chave de criptografia
        """
        key_path = os.path.join(self.temp_dir, 'test_key.key')
        
        # Salva a chave
        self.file_handler.save_encryption_key(key_path)
        assert os.path.exists(key_path)
        
        # Cria novo handler e carrega a chave
        new_handler = FileHandler()
        new_handler.load_encryption_key(key_path)
        
        # Verifica se as chaves são iguais
        assert new_handler.encryption_key == self.file_handler.encryption_key
    
    def test_compress_decompress(self):
        """
        Testa compressão e descompressão de arquivo
        """
        # Cria arquivo de teste
        test_file = os.path.join(self.temp_dir, 'test.txt')
        test_content = b'Hello, World! This is a test file.'
        
        with open(test_file, 'wb') as f:
            f.write(test_content)
        
        # Comprime
        compressed_file = os.path.join(self.temp_dir, 'test.txt.gz')
        self.file_handler.compress_file(test_file, compressed_file)
        assert os.path.exists(compressed_file)
        
        # Descomprime
        decompressed_file = os.path.join(self.temp_dir, 'test_decompressed.txt')
        self.file_handler.decompress_file(compressed_file, decompressed_file)
        
        # Verifica se o conteúdo é o mesmo
        with open(decompressed_file, 'rb') as f:
            assert f.read() == test_content
    
    def test_encrypt_decrypt(self):
        """
        Testa criptografia e descriptografia de arquivo
        """
        # Cria arquivo de teste
        test_file = os.path.join(self.temp_dir, 'test.txt')
        test_content = b'Sensitive data that needs encryption.'
        
        with open(test_file, 'wb') as f:
            f.write(test_content)
        
        # Criptografa
        encrypted_file = os.path.join(self.temp_dir, 'test.encrypted')
        self.file_handler.encrypt_file(test_file, encrypted_file)
        assert os.path.exists(encrypted_file)
        
        # Verifica que o conteúdo criptografado é diferente
        with open(encrypted_file, 'rb') as f:
            encrypted_content = f.read()
        assert encrypted_content != test_content
        
        # Descriptografa
        decrypted_file = os.path.join(self.temp_dir, 'test_decrypted.txt')
        self.file_handler.decrypt_file(encrypted_file, decrypted_file)
        
        # Verifica se o conteúdo é o mesmo
        with open(decrypted_file, 'rb') as f:
            assert f.read() == test_content
    
    def test_process_csv_upload(self):
        """
        Testa o processamento de um arquivo CSV
        """
        # Cria CSV de teste
        csv_file = os.path.join(self.temp_dir, 'test.csv')
        df = pd.DataFrame({
            'feature1': [1, 2, 3, 4, 5],
            'feature2': [10, 20, 30, 40, 50],
            'target': [0, 1, 0, 1, 0]
        })
        df.to_csv(csv_file, index=False)
        
        # Processa o CSV
        output_dir = os.path.join(self.temp_dir, 'processed')
        processed_path, loaded_df = self.file_handler.process_csv_upload(
            csv_file, output_dir, compress=True, encrypt=True
        )
        
        # Verifica se o arquivo processado foi criado
        assert os.path.exists(processed_path)
        
        # Verifica se o DataFrame carregado é correto
        assert loaded_df.shape == df.shape
        assert list(loaded_df.columns) == list(df.columns)
    
    def test_load_processed_csv(self):
        """
        Testa o carregamento de um CSV processado
        """
        # Cria e processa um CSV
        csv_file = os.path.join(self.temp_dir, 'test.csv')
        df_original = pd.DataFrame({
            'A': [1, 2, 3],
            'B': [4, 5, 6],
            'C': [7, 8, 9]
        })
        df_original.to_csv(csv_file, index=False)
        
        output_dir = os.path.join(self.temp_dir, 'processed')
        processed_path, _ = self.file_handler.process_csv_upload(
            csv_file, output_dir, compress=True, encrypt=True
        )
        
        # Carrega o CSV processado
        df_loaded = self.file_handler.load_processed_csv(
            processed_path,
            temp_dir=self.temp_dir,
            is_encrypted=True,
            is_compressed=True
        )
        
        # Verifica se os dados são os mesmos
        pd.testing.assert_frame_equal(df_original, df_loaded)

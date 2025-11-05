"""
Módulo para manipulação de arquivos CSV com criptografia e compressão
"""
import os
import gzip
from typing import Optional, Tuple
from pathlib import Path
import pandas as pd
from cryptography.fernet import Fernet


class FileHandler:
    """
    Classe responsável por gerenciar uploads, compressão e criptografia de arquivos CSV
    """
    
    def __init__(self, encryption_key: Optional[bytes] = None):
        """
        Inicializa o handler de arquivos
        
        Args:
            encryption_key: Chave de criptografia (opcional). Se não fornecida, será gerada.
        """
        if encryption_key is None:
            self.encryption_key = Fernet.generate_key()
        else:
            self.encryption_key = encryption_key
        
        self.cipher = Fernet(self.encryption_key)
    
    def save_encryption_key(self, filepath: str) -> None:
        """
        Salva a chave de criptografia em um arquivo
        
        Args:
            filepath: Caminho para salvar a chave
        """
        with open(filepath, 'wb') as key_file:
            key_file.write(self.encryption_key)
    
    def load_encryption_key(self, filepath: str) -> None:
        """
        Carrega a chave de criptografia de um arquivo
        
        Args:
            filepath: Caminho do arquivo contendo a chave
        """
        with open(filepath, 'rb') as key_file:
            self.encryption_key = key_file.read()
            self.cipher = Fernet(self.encryption_key)
    
    def compress_file(self, input_path: str, output_path: str) -> None:
        """
        Comprime um arquivo usando gzip
        
        Args:
            input_path: Caminho do arquivo de entrada
            output_path: Caminho do arquivo comprimido de saída
        """
        with open(input_path, 'rb') as f_in:
            with gzip.open(output_path, 'wb') as f_out:
                f_out.writelines(f_in)
    
    def decompress_file(self, input_path: str, output_path: str) -> None:
        """
        Descomprime um arquivo gzip
        
        Args:
            input_path: Caminho do arquivo comprimido
            output_path: Caminho do arquivo descomprimido de saída
        """
        with gzip.open(input_path, 'rb') as f_in:
            with open(output_path, 'wb') as f_out:
                f_out.writelines(f_in)
    
    def encrypt_file(self, input_path: str, output_path: str) -> None:
        """
        Criptografa um arquivo
        
        Args:
            input_path: Caminho do arquivo de entrada
            output_path: Caminho do arquivo criptografado de saída
        """
        with open(input_path, 'rb') as f_in:
            data = f_in.read()
            encrypted_data = self.cipher.encrypt(data)
        
        with open(output_path, 'wb') as f_out:
            f_out.write(encrypted_data)
    
    def decrypt_file(self, input_path: str, output_path: str) -> None:
        """
        Descriptografa um arquivo
        
        Args:
            input_path: Caminho do arquivo criptografado
            output_path: Caminho do arquivo descriptografado de saída
        """
        with open(input_path, 'rb') as f_in:
            encrypted_data = f_in.read()
            decrypted_data = self.cipher.decrypt(encrypted_data)
        
        with open(output_path, 'wb') as f_out:
            f_out.write(decrypted_data)
    
    def process_csv_upload(self, 
                          csv_path: str, 
                          output_dir: str,
                          compress: bool = True,
                          encrypt: bool = True) -> Tuple[str, pd.DataFrame]:
        """
        Processa um arquivo CSV recebido: comprime e/ou criptografa conforme especificado
        
        Args:
            csv_path: Caminho do arquivo CSV recebido
            output_dir: Diretório para salvar os arquivos processados
            compress: Se True, comprime o arquivo
            encrypt: Se True, criptografa o arquivo
            
        Returns:
            Tupla contendo (caminho do arquivo processado, DataFrame com os dados)
        """
        # Cria o diretório de saída se não existir
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Carrega os dados do CSV
        df = pd.read_csv(csv_path)
        
        # Define o caminho base do arquivo processado
        base_name = Path(csv_path).stem
        current_path = csv_path
        
        # Aplica compressão se solicitado
        if compress:
            compressed_path = os.path.join(output_dir, f"{base_name}.csv.gz")
            self.compress_file(current_path, compressed_path)
            current_path = compressed_path
        
        # Aplica criptografia se solicitado
        if encrypt:
            encrypted_path = os.path.join(output_dir, f"{base_name}.encrypted")
            if compress:
                encrypted_path = os.path.join(output_dir, f"{base_name}.csv.gz.encrypted")
            self.encrypt_file(current_path, encrypted_path)
            current_path = encrypted_path
        
        return current_path, df
    
    def load_processed_csv(self, 
                          processed_path: str,
                          temp_dir: str = "/tmp",
                          is_encrypted: bool = True,
                          is_compressed: bool = True) -> pd.DataFrame:
        """
        Carrega um arquivo CSV processado (descriptografa e/ou descomprime conforme necessário)
        
        Args:
            processed_path: Caminho do arquivo processado
            temp_dir: Diretório temporário para arquivos intermediários
            is_encrypted: Se True, o arquivo está criptografado
            is_compressed: Se True, o arquivo está comprimido
            
        Returns:
            DataFrame com os dados do CSV
        """
        current_path = processed_path
        
        # Descriptografa se necessário
        if is_encrypted:
            decrypted_path = os.path.join(temp_dir, "decrypted.tmp")
            self.decrypt_file(current_path, decrypted_path)
            current_path = decrypted_path
        
        # Descomprime se necessário
        if is_compressed:
            decompressed_path = os.path.join(temp_dir, "decompressed.csv")
            self.decompress_file(current_path, decompressed_path)
            current_path = decompressed_path
        
        # Carrega o DataFrame
        df = pd.read_csv(current_path)
        
        # Limpa arquivos temporários
        if is_encrypted and os.path.exists(os.path.join(temp_dir, "decrypted.tmp")):
            os.remove(os.path.join(temp_dir, "decrypted.tmp"))
        if is_compressed and os.path.exists(os.path.join(temp_dir, "decompressed.csv")):
            os.remove(os.path.join(temp_dir, "decompressed.csv"))
        
        return df

"""
Exemplo de uso do sistema de ML
"""
import os
import sys
import pandas as pd
import numpy as np
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.file_handler import FileHandler
from src.models.ml_model import MLModelManager


def create_sample_data():
    """
    Cria dados de exemplo para demonstração
    """
    print("📊 Criando dados de exemplo...")
    
    # Cria diretório de dados se não existir
    data_dir = Path(__file__).parent.parent / 'data' / 'raw'
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Cria dataset de classificação (exemplo: prever se um aluno será aprovado)
    np.random.seed(42)
    n_samples = 200
    
    df = pd.DataFrame({
        'nota_prova1': np.random.uniform(0, 10, n_samples),
        'nota_prova2': np.random.uniform(0, 10, n_samples),
        'frequencia': np.random.uniform(50, 100, n_samples),
        'horas_estudo': np.random.uniform(0, 40, n_samples)
    })
    
    # Define aprovação baseado em regras (média >= 6 e frequência >= 75)
    df['media'] = (df['nota_prova1'] + df['nota_prova2']) / 2
    df['aprovado'] = ((df['media'] >= 6) & (df['frequencia'] >= 75)).astype(int)
    df = df.drop(columns=['media'])
    
    # Salva CSV
    train_file = data_dir / 'treino_exemplo.csv'
    df.head(150).to_csv(train_file, index=False)
    
    test_file = data_dir / 'teste_exemplo.csv'
    df.tail(50).to_csv(test_file, index=False)
    
    print(f"✅ Dados criados: {train_file} e {test_file}")
    return train_file, test_file


def example_full_workflow():
    """
    Demonstra o fluxo completo do sistema
    """
    print("\n" + "="*60)
    print("🚀 EXEMPLO DE USO COMPLETO DO SISTEMA")
    print("="*60 + "\n")
    
    # 1. Criar dados de exemplo
    train_file, test_file = create_sample_data()
    
    # 2. Inicializar FileHandler
    print("\n🔐 Inicializando handler de arquivos com criptografia...")
    file_handler = FileHandler()
    
    # Salvar chave de criptografia
    key_dir = Path(__file__).parent.parent / 'config'
    key_dir.mkdir(exist_ok=True)
    key_file = key_dir / 'encryption.key'
    file_handler.save_encryption_key(str(key_file))
    print(f"✅ Chave salva em: {key_file}")
    
    # 3. Processar arquivo de treino (comprime e criptografa)
    print("\n📦 Processando arquivo de treino (compressão + criptografia)...")
    encrypted_dir = Path(__file__).parent.parent / 'data' / 'encrypted'
    encrypted_train_path, train_df = file_handler.process_csv_upload(
        str(train_file),
        str(encrypted_dir),
        compress=True,
        encrypt=True
    )
    print(f"✅ Arquivo processado: {encrypted_train_path}")
    print(f"   Shape dos dados: {train_df.shape}")
    print(f"   Colunas: {train_df.columns.tolist()}")
    
    # 4. Carregar dados processados
    print("\n📂 Carregando dados processados...")
    loaded_df = file_handler.load_processed_csv(
        encrypted_train_path,
        is_encrypted=True,
        is_compressed=True
    )
    print(f"✅ Dados carregados: {loaded_df.shape}")
    
    # 5. Treinar modelo
    print("\n🤖 Treinando modelo de classificação...")
    ml_manager = MLModelManager(
        model_type='classification',
        algorithm='random_forest'
    )
    
    metrics = ml_manager.train(loaded_df, 'aprovado', test_size=0.2)
    
    print("\n📊 Métricas de treinamento:")
    print(f"   Acurácia treino: {metrics['train_accuracy']:.4f}")
    print(f"   Acurácia teste: {metrics['test_accuracy']:.4f}")
    print(f"   Amostras treino: {metrics['train_samples']}")
    print(f"   Amostras teste: {metrics['test_samples']}")
    
    # 6. Salvar modelo
    print("\n💾 Salvando modelo...")
    model_dir = Path(__file__).parent.parent / 'data' / 'models'
    model_dir.mkdir(parents=True, exist_ok=True)
    model_path = model_dir / 'modelo_exemplo.pkl'
    ml_manager.save_model(str(model_path))
    print(f"✅ Modelo salvo em: {model_path}")
    
    # 7. Processar dados de teste
    print("\n🧪 Processando dados de teste...")
    encrypted_test_path, test_df = file_handler.process_csv_upload(
        str(test_file),
        str(encrypted_dir),
        compress=True,
        encrypt=True
    )
    print(f"✅ Arquivo de teste processado: {encrypted_test_path}")
    
    # 8. Fazer predições
    print("\n🎯 Realizando predições nos dados de teste...")
    test_data_loaded = file_handler.load_processed_csv(
        encrypted_test_path,
        is_encrypted=True,
        is_compressed=True
    )
    
    # Remove coluna target para predição
    X_test = test_data_loaded.drop(columns=['aprovado'])
    predictions = ml_manager.predict(X_test)
    
    print(f"✅ Predições realizadas: {len(predictions)} amostras")
    print(f"   Primeiras 10 predições: {predictions[:10]}")
    
    # Comparar com valores reais
    y_true = test_data_loaded['aprovado'].values
    accuracy = (predictions == y_true).mean()
    print(f"   Acurácia nas predições: {accuracy:.4f}")
    
    # 9. Demonstrar reset do modelo
    print("\n🔄 Demonstrando reset do modelo...")
    info_before = ml_manager.get_model_info()
    print(f"   Antes do reset - Treinado: {info_before['is_trained']}")
    
    ml_manager.reset_model()
    info_after = ml_manager.get_model_info()
    print(f"   Depois do reset - Treinado: {info_after['is_trained']}")
    print("✅ Modelo resetado, pronto para novo treinamento!")
    
    print("\n" + "="*60)
    print("✨ EXEMPLO COMPLETO EXECUTADO COM SUCESSO!")
    print("="*60 + "\n")


if __name__ == "__main__":
    example_full_workflow()

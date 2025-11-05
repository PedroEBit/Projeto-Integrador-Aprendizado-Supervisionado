"""
Testes unitários para o MLModelManager
"""
import os
import tempfile
import pytest
import pandas as pd
import numpy as np
from src.models.ml_model import MLModelManager


class TestMLModelManager:
    """
    Testes para a classe MLModelManager
    """
    
    def setup_method(self):
        """
        Configuração executada antes de cada teste
        """
        self.temp_dir = tempfile.mkdtemp()
        
        # Cria dataset de teste para classificação
        np.random.seed(42)
        self.classification_df = pd.DataFrame({
            'feature1': np.random.randn(100),
            'feature2': np.random.randn(100),
            'feature3': np.random.randn(100),
            'target': np.random.randint(0, 2, 100)
        })
        
        # Cria dataset de teste para regressão
        self.regression_df = pd.DataFrame({
            'feature1': np.random.randn(100),
            'feature2': np.random.randn(100),
            'feature3': np.random.randn(100),
            'target': np.random.randn(100) * 10
        })
    
    def test_initialization_classification(self):
        """
        Testa a inicialização com modelo de classificação
        """
        manager = MLModelManager(model_type='classification', algorithm='random_forest')
        assert manager.model_type == 'classification'
        assert manager.algorithm == 'random_forest'
        assert manager.is_trained is False
        assert manager.model is not None
    
    def test_initialization_regression(self):
        """
        Testa a inicialização com modelo de regressão
        """
        manager = MLModelManager(model_type='regression', algorithm='random_forest')
        assert manager.model_type == 'regression'
        assert manager.algorithm == 'random_forest'
        assert manager.is_trained is False
    
    def test_train_classification(self):
        """
        Testa o treinamento de um modelo de classificação
        """
        manager = MLModelManager(model_type='classification', algorithm='random_forest')
        metrics = manager.train(self.classification_df, 'target')
        
        assert manager.is_trained is True
        assert 'train_accuracy' in metrics
        assert 'test_accuracy' in metrics
        assert metrics['train_samples'] > 0
        assert metrics['test_samples'] > 0
    
    def test_train_regression(self):
        """
        Testa o treinamento de um modelo de regressão
        """
        manager = MLModelManager(model_type='regression', algorithm='random_forest')
        metrics = manager.train(self.regression_df, 'target')
        
        assert manager.is_trained is True
        assert 'train_mse' in metrics
        assert 'test_mse' in metrics
        assert 'train_rmse' in metrics
        assert 'test_rmse' in metrics
    
    def test_predict(self):
        """
        Testa a realização de predições
        """
        manager = MLModelManager(model_type='classification', algorithm='random_forest')
        manager.train(self.classification_df, 'target')
        
        # Prepara dados para predição (sem a coluna target)
        test_data = self.classification_df.drop(columns=['target']).head(10)
        predictions = manager.predict(test_data)
        
        assert len(predictions) == 10
        assert all(pred in [0, 1] for pred in predictions)
    
    def test_predict_without_training(self):
        """
        Testa que predição sem treinamento levanta erro
        """
        manager = MLModelManager(model_type='classification', algorithm='random_forest')
        test_data = self.classification_df.drop(columns=['target'])
        
        with pytest.raises(ValueError, match="Modelo não foi treinado"):
            manager.predict(test_data)
    
    def test_save_and_load_model(self):
        """
        Testa salvar e carregar um modelo
        """
        # Treina e salva modelo
        manager1 = MLModelManager(model_type='classification', algorithm='random_forest')
        manager1.train(self.classification_df, 'target')
        
        model_path = os.path.join(self.temp_dir, 'test_model.pkl')
        manager1.save_model(model_path)
        assert os.path.exists(model_path)
        
        # Carrega modelo em novo manager
        manager2 = MLModelManager(model_type='classification', algorithm='random_forest')
        manager2.load_model(model_path)
        
        assert manager2.is_trained is True
        assert manager2.feature_names == manager1.feature_names
        assert manager2.target_name == manager1.target_name
        
        # Verifica que as predições são iguais
        test_data = self.classification_df.drop(columns=['target']).head(5)
        pred1 = manager1.predict(test_data)
        pred2 = manager2.predict(test_data)
        
        np.testing.assert_array_equal(pred1, pred2)
    
    def test_reset_model(self):
        """
        Testa o reset do modelo
        """
        manager = MLModelManager(model_type='classification', algorithm='random_forest')
        manager.train(self.classification_df, 'target')
        
        assert manager.is_trained is True
        assert manager.feature_names is not None
        
        # Reseta o modelo
        manager.reset_model()
        
        assert manager.is_trained is False
        assert manager.feature_names is None
        assert manager.target_name is None
    
    def test_get_model_info(self):
        """
        Testa obtenção de informações do modelo
        """
        manager = MLModelManager(model_type='classification', algorithm='random_forest')
        
        # Antes do treinamento
        info_before = manager.get_model_info()
        assert info_before['is_trained'] is False
        assert info_before['feature_names'] is None
        
        # Depois do treinamento
        manager.train(self.classification_df, 'target')
        info_after = manager.get_model_info()
        
        assert info_after['is_trained'] is True
        assert info_after['feature_names'] is not None
        assert info_after['target_name'] == 'target'
        assert 'feature_importances' in info_after

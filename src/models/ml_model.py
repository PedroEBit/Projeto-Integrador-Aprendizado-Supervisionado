"""
Módulo para gerenciamento de modelos de Machine Learning supervisionado
"""
import os
import pickle
from typing import Optional, Dict, Any, Tuple
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.metrics import accuracy_score, mean_squared_error, classification_report


class MLModelManager:
    """
    Classe para gerenciar o ciclo de vida de modelos de ML supervisionado
    """
    
    def __init__(self, model_type: str = "classification", algorithm: str = "random_forest"):
        """
        Inicializa o gerenciador de modelos
        
        Args:
            model_type: Tipo de problema ("classification" ou "regression")
            algorithm: Algoritmo a ser usado ("random_forest", "logistic_regression", "linear_regression")
        """
        self.model_type = model_type
        self.algorithm = algorithm
        self.model = None
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_names = None
        self.target_name = None
        
        self._initialize_model()
    
    def _initialize_model(self) -> None:
        """
        Inicializa o modelo baseado no tipo e algoritmo especificados
        """
        if self.model_type == "classification":
            if self.algorithm == "random_forest":
                self.model = RandomForestClassifier(n_estimators=100, random_state=42)
            elif self.algorithm == "logistic_regression":
                self.model = LogisticRegression(random_state=42, max_iter=1000)
            else:
                raise ValueError(f"Algoritmo desconhecido para classificação: {self.algorithm}")
        
        elif self.model_type == "regression":
            if self.algorithm == "random_forest":
                self.model = RandomForestRegressor(n_estimators=100, random_state=42)
            elif self.algorithm == "linear_regression":
                self.model = LinearRegression()
            else:
                raise ValueError(f"Algoritmo desconhecido para regressão: {self.algorithm}")
        
        else:
            raise ValueError(f"Tipo de modelo desconhecido: {self.model_type}")
    
    def train(self, 
             df: pd.DataFrame, 
             target_column: str,
             test_size: float = 0.2,
             random_state: int = 42) -> Dict[str, Any]:
        """
        Treina o modelo com os dados fornecidos
        
        Args:
            df: DataFrame com os dados de treinamento
            target_column: Nome da coluna alvo (target)
            test_size: Proporção dos dados para teste
            random_state: Seed para reproducibilidade
            
        Returns:
            Dicionário com métricas de desempenho
        """
        # Separa features e target
        X = df.drop(columns=[target_column])
        y = df[target_column]
        
        # Armazena nomes das features e target
        self.feature_names = X.columns.tolist()
        self.target_name = target_column
        
        # Divide em treino e teste
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )
        
        # Normaliza os dados
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Treina o modelo
        self.model.fit(X_train_scaled, y_train)
        self.is_trained = True
        
        # Avalia o modelo
        train_predictions = self.model.predict(X_train_scaled)
        test_predictions = self.model.predict(X_test_scaled)
        
        # Calcula métricas baseadas no tipo de modelo
        metrics = {
            "train_samples": len(X_train),
            "test_samples": len(X_test),
            "features": self.feature_names,
            "target": self.target_name
        }
        
        if self.model_type == "classification":
            metrics["train_accuracy"] = accuracy_score(y_train, train_predictions)
            metrics["test_accuracy"] = accuracy_score(y_test, test_predictions)
            metrics["classification_report"] = classification_report(
                y_test, test_predictions, output_dict=True
            )
        else:  # regression
            metrics["train_mse"] = mean_squared_error(y_train, train_predictions)
            metrics["test_mse"] = mean_squared_error(y_test, test_predictions)
            metrics["train_rmse"] = np.sqrt(metrics["train_mse"])
            metrics["test_rmse"] = np.sqrt(metrics["test_mse"])
        
        return metrics
    
    def predict(self, df: pd.DataFrame) -> np.ndarray:
        """
        Realiza predições com o modelo treinado
        
        Args:
            df: DataFrame com os dados para predição
            
        Returns:
            Array com as predições
            
        Raises:
            ValueError: Se o modelo não foi treinado
        """
        if not self.is_trained:
            raise ValueError("Modelo não foi treinado. Execute o método train() primeiro.")
        
        # Garante que as features estão na ordem correta
        X = df[self.feature_names]
        
        # Normaliza os dados
        X_scaled = self.scaler.transform(X)
        
        # Realiza predições
        predictions = self.model.predict(X_scaled)
        
        return predictions
    
    def save_model(self, filepath: str) -> None:
        """
        Salva o modelo treinado em disco
        
        Args:
            filepath: Caminho do arquivo para salvar o modelo
        """
        if not self.is_trained:
            raise ValueError("Modelo não foi treinado. Não há nada para salvar.")
        
        model_data = {
            "model": self.model,
            "scaler": self.scaler,
            "model_type": self.model_type,
            "algorithm": self.algorithm,
            "feature_names": self.feature_names,
            "target_name": self.target_name,
            "is_trained": self.is_trained
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
    
    def load_model(self, filepath: str) -> None:
        """
        Carrega um modelo salvo do disco
        
        Args:
            filepath: Caminho do arquivo do modelo salvo
        """
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)
        
        self.model = model_data["model"]
        self.scaler = model_data["scaler"]
        self.model_type = model_data["model_type"]
        self.algorithm = model_data["algorithm"]
        self.feature_names = model_data["feature_names"]
        self.target_name = model_data["target_name"]
        self.is_trained = model_data["is_trained"]
    
    def reset_model(self) -> None:
        """
        Reseta o modelo para o estado inicial, permitindo treino com nova base de dados
        """
        self._initialize_model()
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_names = None
        self.target_name = None
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Retorna informações sobre o modelo atual
        
        Returns:
            Dicionário com informações do modelo
        """
        info = {
            "model_type": self.model_type,
            "algorithm": self.algorithm,
            "is_trained": self.is_trained,
            "feature_names": self.feature_names,
            "target_name": self.target_name
        }
        
        if self.is_trained and hasattr(self.model, 'feature_importances_'):
            info["feature_importances"] = dict(
                zip(self.feature_names, self.model.feature_importances_.tolist())
            )
        
        return info

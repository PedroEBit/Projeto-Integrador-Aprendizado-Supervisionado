# Projeto Integrador - Aprendizado Supervisionado

Sistema completo para treinamento de modelos de Machine Learning com upload seguro de arquivos CSV, criptografia ponta-a-ponta e gerenciamento de modelos.

## 📋 Funcionalidades

- ✅ **Upload de arquivos CSV**: Interface para envio de datasets de treino e teste
- 🔐 **Criptografia ponta-a-ponta**: Arquivos são comprimidos (gzip) e criptografados (Fernet)
- 🤖 **Modelos de ML supervisionado**: Suporte para classificação e regressão
- 🔄 **Reset de modelo**: Capacidade de resetar o modelo para treinar com nova base de dados
- 📊 **Métricas de desempenho**: Avaliação automática dos modelos treinados
- 🚀 **API REST**: Interface Flask para integração com outras aplicações

## 🏗️ Estrutura do Projeto

```
.
├── config/                    # Configurações e chaves de criptografia
│   ├── config.py             # Configurações gerais
│   └── encryption.key        # Chave de criptografia (gerada automaticamente)
├── data/                      # Dados do projeto
│   ├── raw/                  # Arquivos CSV originais
│   ├── encrypted/            # Arquivos processados (criptografados)
│   ├── processed/            # Dados intermediários
│   └── models/               # Modelos treinados
├── src/                       # Código fonte
│   ├── api/                  # API Flask
│   │   └── app.py           # Aplicação principal
│   ├── models/               # Modelos de ML
│   │   └── ml_model.py      # Gerenciador de modelos
│   └── utils/                # Utilitários
│       └── file_handler.py  # Manipulação e criptografia de arquivos
├── tests/                     # Testes
│   ├── unit/                 # Testes unitários
│   └── integration/          # Testes de integração
├── examples/                  # Exemplos de uso
│   └── example_usage.py      # Exemplo completo
├── requirements.txt           # Dependências do projeto
└── README.md                  # Este arquivo

```

## 🚀 Instalação

### Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

### Passos

1. **Clone o repositório**:
```bash
git clone https://github.com/PedroEBit/Projeto-Integrador-Aprendizado-Supervisionado.git
cd Projeto-Integrador-Aprendizado-Supervisionado
```

2. **Crie um ambiente virtual** (recomendado):
```bash
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
```

3. **Instale as dependências**:
```bash
pip install -r requirements.txt
```

## 📖 Uso

### Opção 1: Executar Exemplo Completo

Execute o script de exemplo para ver todas as funcionalidades:

```bash
python examples/example_usage.py
```

Este exemplo demonstra:
- Criação de dados de exemplo
- Processamento de arquivos (compressão + criptografia)
- Treinamento de modelo
- Realização de predições
- Reset do modelo

### Opção 2: Usar a API REST

1. **Inicie o servidor**:
```bash
python src/api/app.py
```

2. **Endpoints disponíveis**:

#### Health Check
```bash
GET http://localhost:5000/health
```

#### Upload de arquivo CSV
```bash
POST http://localhost:5000/upload
Content-Type: multipart/form-data

# Formulário com campo 'file' contendo o CSV
```

Resposta:
```json
{
  "message": "Arquivo recebido e processado com sucesso",
  "original_filename": "dados.csv",
  "processed_filepath": "data/encrypted/dados.csv.gz.encrypted",
  "rows": 1000,
  "columns": ["feature1", "feature2", "target"],
  "shape": [1000, 3]
}
```

#### Treinar modelo
```bash
POST http://localhost:5000/train
Content-Type: application/json

{
  "processed_file": "data/encrypted/dados.csv.gz.encrypted",
  "target_column": "target",
  "model_type": "classification",
  "algorithm": "random_forest"
}
```

Resposta:
```json
{
  "message": "Modelo treinado com sucesso",
  "metrics": {
    "train_accuracy": 0.95,
    "test_accuracy": 0.92,
    "train_samples": 800,
    "test_samples": 200
  },
  "model_path": "data/models/current_model.pkl"
}
```

#### Fazer predições
```bash
POST http://localhost:5000/predict
Content-Type: application/json

{
  "processed_file": "data/encrypted/teste.csv.gz.encrypted"
}
```

#### Informações do modelo
```bash
GET http://localhost:5000/model/info
```

#### Resetar modelo
```bash
POST http://localhost:5000/model/reset
```

#### Exportar chave de criptografia
```bash
GET http://localhost:5000/key/export
```

### Opção 3: Uso Programático

```python
from src.utils.file_handler import FileHandler
from src.models.ml_model import MLModelManager
import pandas as pd

# 1. Processar arquivo CSV
file_handler = FileHandler()
processed_path, df = file_handler.process_csv_upload(
    'dados.csv',
    'data/encrypted',
    compress=True,
    encrypt=True
)

# 2. Treinar modelo
ml_manager = MLModelManager(
    model_type='classification',
    algorithm='random_forest'
)
metrics = ml_manager.train(df, 'target_column')

# 3. Fazer predições
predictions = ml_manager.predict(test_data)

# 4. Resetar modelo para nova base
ml_manager.reset_model()
```

## 🔐 Segurança

### Criptografia

O sistema utiliza o algoritmo **Fernet** (criptografia simétrica) da biblioteca `cryptography`:
- Chave de 128 bits
- Autenticação integrada (HMAC)
- Timestamping para prevenir replay attacks

### Fluxo de Processamento

1. **Upload**: Arquivo CSV é recebido
2. **Compressão**: Arquivo é comprimido com gzip (reduz tamanho)
3. **Criptografia**: Arquivo comprimido é criptografado
4. **Armazenamento**: Arquivo criptografado é salvo
5. **Uso**: Quando necessário, arquivo é descriptografado e descomprimido em memória

### Boas Práticas

- ⚠️ **NUNCA** commite a chave de criptografia (`config/encryption.key`) no repositório
- 🔑 Mantenha a chave de criptografia em local seguro
- 🔒 Em produção, use variáveis de ambiente para chaves sensíveis
- 🔐 Implemente autenticação nos endpoints da API

## 🧪 Testes

Execute os testes unitários:

```bash
pytest tests/unit/ -v
```

Execute todos os testes com cobertura:

```bash
pytest tests/ --cov=src --cov-report=html
```

## 📊 Tipos de Modelos Suportados

### Classificação
- **Random Forest Classifier**: Ensemble de árvores de decisão (padrão)
- **Logistic Regression**: Regressão logística

### Regressão
- **Random Forest Regressor**: Ensemble de árvores de decisão
- **Linear Regression**: Regressão linear

## 🔄 Reset de Modelo

O sistema permite resetar completamente o modelo treinado:

```python
# Treina modelo
ml_manager.train(df1, 'target')

# Reseta para treinar com nova base
ml_manager.reset_model()

# Treina com nova base
ml_manager.train(df2, 'new_target')
```

Ou via API:
```bash
POST http://localhost:5000/model/reset
```

## 🛠️ Configuração

### Variáveis de Ambiente

Crie um arquivo `.env` baseado no `.env.example`:

```bash
API_HOST=0.0.0.0
API_PORT=5000
DEBUG_MODE=True
DEFAULT_MODEL_TYPE=classification
DEFAULT_ALGORITHM=random_forest
```

### Configurações Personalizadas

Edite `config/config.py` para ajustar:
- Tamanho máximo de arquivo
- Diretórios de dados
- Parâmetros padrão dos modelos

## 📝 Requisitos Implementados

✅ **Capacidade de upload de arquivos CSV**: Implementado via API e módulo FileHandler

✅ **Processamento ponta-a-ponta**: Arquivos são comprimidos (gzip) e criptografados (Fernet) antes do armazenamento

✅ **Reset de modelo**: Funcionalidade completa para resetar e treinar com nova base de dados

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto é de código aberto e está disponível para fins educacionais.

## 👥 Autores

Projeto Integrador - Aprendizado Supervisionado

## 📞 Contato

Para dúvidas ou sugestões, abra uma issue no repositório.
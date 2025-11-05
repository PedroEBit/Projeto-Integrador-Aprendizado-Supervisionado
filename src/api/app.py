"""
API Flask para gerenciar upload de arquivos CSV e treinamento de modelos
"""
import os
from pathlib import Path
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename

from src.utils.file_handler import FileHandler
from src.models.ml_model import MLModelManager


# Configurações
UPLOAD_FOLDER = 'data/raw'
ENCRYPTED_FOLDER = 'data/encrypted'
MODEL_FOLDER = 'data/models'
ALLOWED_EXTENSIONS = {'csv'}

# Cria diretórios necessários
Path(UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)
Path(ENCRYPTED_FOLDER).mkdir(parents=True, exist_ok=True)
Path(MODEL_FOLDER).mkdir(parents=True, exist_ok=True)

# Inicializa Flask
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max file size

# Inicializa componentes
file_handler = FileHandler()
ml_manager = None  # Será inicializado quando necessário


def allowed_file(filename: str) -> bool:
    """
    Verifica se a extensão do arquivo é permitida
    
    Args:
        filename: Nome do arquivo
        
    Returns:
        True se a extensão é permitida, False caso contrário
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/health', methods=['GET'])
def health_check():
    """
    Endpoint de health check
    """
    return jsonify({
        "status": "healthy",
        "service": "ML Model API"
    }), 200


@app.route('/upload', methods=['POST'])
def upload_file():
    """
    Endpoint para upload de arquivo CSV
    
    Recebe um arquivo CSV e o processa (comprime e criptografa)
    """
    # Verifica se há arquivo na requisição
    if 'file' not in request.files:
        return jsonify({"error": "Nenhum arquivo foi enviado"}), 400
    
    file = request.files['file']
    
    # Verifica se o arquivo tem nome
    if file.filename == '':
        return jsonify({"error": "Nenhum arquivo selecionado"}), 400
    
    # Verifica se é um arquivo CSV
    if not allowed_file(file.filename):
        return jsonify({"error": "Apenas arquivos CSV são permitidos"}), 400
    
    try:
        # Salva o arquivo com nome seguro
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Processa o arquivo (comprime e criptografa)
        processed_path, df = file_handler.process_csv_upload(
            filepath, 
            ENCRYPTED_FOLDER,
            compress=True,
            encrypt=True
        )
        
        # Retorna informações sobre o arquivo processado
        return jsonify({
            "message": "Arquivo recebido e processado com sucesso",
            "original_filename": filename,
            "processed_filepath": processed_path,
            "rows": len(df),
            "columns": df.columns.tolist(),
            "shape": df.shape
        }), 200
    
    except Exception as e:
        # Log the error for debugging but don't expose stack trace to users
        app.logger.error(f"Error processing file: {str(e)}")
        return jsonify({"error": "Erro ao processar arquivo"}), 500


@app.route('/train', methods=['POST'])
def train_model():
    """
    Endpoint para treinar um modelo
    
    Espera JSON com:
    - processed_file: caminho do arquivo processado
    - target_column: coluna alvo
    - model_type: "classification" ou "regression"
    - algorithm: nome do algoritmo
    """
    global ml_manager
    
    try:
        data = request.get_json()
        
        # Valida dados de entrada
        if not data or 'processed_file' not in data or 'target_column' not in data:
            return jsonify({
                "error": "Dados inválidos. Forneça 'processed_file' e 'target_column'"
            }), 400
        
        processed_file = data['processed_file']
        target_column = data['target_column']
        model_type = data.get('model_type', 'classification')
        algorithm = data.get('algorithm', 'random_forest')
        
        # Carrega os dados do arquivo processado
        df = file_handler.load_processed_csv(
            processed_file,
            is_encrypted=True,
            is_compressed=True
        )
        
        # Inicializa o modelo
        ml_manager = MLModelManager(model_type=model_type, algorithm=algorithm)
        
        # Treina o modelo
        metrics = ml_manager.train(df, target_column)
        
        # Salva o modelo
        model_path = os.path.join(MODEL_FOLDER, 'current_model.pkl')
        ml_manager.save_model(model_path)
        
        return jsonify({
            "message": "Modelo treinado com sucesso",
            "metrics": metrics,
            "model_path": model_path
        }), 200
    
    except Exception as e:
        # Log the error for debugging but don't expose stack trace to users
        app.logger.error(f"Error training model: {str(e)}")
        return jsonify({"error": "Erro ao treinar modelo"}), 500


@app.route('/predict', methods=['POST'])
def predict():
    """
    Endpoint para realizar predições
    
    Espera JSON com:
    - processed_file: caminho do arquivo processado com dados para predição
    """
    global ml_manager
    
    try:
        if ml_manager is None or not ml_manager.is_trained:
            return jsonify({
                "error": "Modelo não treinado. Execute /train primeiro."
            }), 400
        
        data = request.get_json()
        
        if not data or 'processed_file' not in data:
            return jsonify({
                "error": "Forneça 'processed_file' com os dados para predição"
            }), 400
        
        processed_file = data['processed_file']
        
        # Carrega os dados
        df = file_handler.load_processed_csv(
            processed_file,
            is_encrypted=True,
            is_compressed=True
        )
        
        # Realiza predições
        predictions = ml_manager.predict(df)
        
        return jsonify({
            "message": "Predições realizadas com sucesso",
            "predictions": predictions.tolist(),
            "num_predictions": len(predictions)
        }), 200
    
    except Exception as e:
        # Log the error for debugging but don't expose stack trace to users
        app.logger.error(f"Error making predictions: {str(e)}")
        return jsonify({"error": "Erro ao realizar predições"}), 500


@app.route('/model/info', methods=['GET'])
def model_info():
    """
    Endpoint para obter informações sobre o modelo atual
    """
    global ml_manager
    
    if ml_manager is None:
        return jsonify({
            "message": "Nenhum modelo inicializado"
        }), 200
    
    try:
        info = ml_manager.get_model_info()
        return jsonify(info), 200
    
    except Exception as e:
        # Log the error for debugging but don't expose stack trace to users
        app.logger.error(f"Error getting model info: {str(e)}")
        return jsonify({"error": "Erro ao obter informações"}), 500


@app.route('/model/reset', methods=['POST'])
def reset_model():
    """
    Endpoint para resetar o modelo atual
    
    Permite treinar com uma nova base de dados
    """
    global ml_manager
    
    try:
        if ml_manager is not None:
            ml_manager.reset_model()
            return jsonify({
                "message": "Modelo resetado com sucesso. Pronto para novo treinamento."
            }), 200
        else:
            return jsonify({
                "message": "Nenhum modelo para resetar"
            }), 200
    
    except Exception as e:
        # Log the error for debugging but don't expose stack trace to users
        app.logger.error(f"Error resetting model: {str(e)}")
        return jsonify({"error": "Erro ao resetar modelo"}), 500


@app.route('/key/export', methods=['GET'])
def export_key():
    """
    Endpoint para exportar a chave de criptografia
    
    ATENÇÃO: Em produção, isso deve ser protegido com autenticação
    """
    try:
        key_path = os.path.join('config', 'encryption.key')
        Path('config').mkdir(exist_ok=True)
        file_handler.save_encryption_key(key_path)
        
        return jsonify({
            "message": "Chave exportada com sucesso",
            "key_path": key_path
        }), 200
    
    except Exception as e:
        # Log the error for debugging but don't expose stack trace to users
        app.logger.error(f"Error exporting key: {str(e)}")
        return jsonify({"error": "Erro ao exportar chave"}), 500


if __name__ == '__main__':
    # Use environment variable for debug mode, default to False for security
    debug_mode = os.getenv('DEBUG_MODE', 'False').lower() == 'true'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)

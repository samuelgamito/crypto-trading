#!/usr/bin/env python3
"""
Script para testar o sistema de logging da Binance API
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.config.config import Config
from src.api.binance_client import BinanceClient


def test_binance_logging():
    """Testa o sistema de logging da Binance"""
    
    print("🔧 Testando Sistema de Logging da Binance API")
    print("=" * 50)
    
    try:
        # Load configuration
        config = Config()
        print(f"✅ Configuração carregada")
        print()
        
        # Initialize Binance client
        client = BinanceClient(config)
        print(f"✅ Cliente Binance inicializado")
        print()
        
        # Test successful API call
        print("📞 Testando chamada bem-sucedida...")
        try:
            ticker = client.get_ticker_price('BTCBRL')
            print(f"   ✅ Preço BTC: R$ {ticker['price']}")
        except Exception as e:
            print(f"   ❌ Erro na chamada: {e}")
        print()
        
        # Test API call that might fail (invalid symbol)
        print("📞 Testando chamada que pode falhar...")
        try:
            ticker = client.get_ticker_price('INVALIDPAIR')
            print(f"   ✅ Chamada inesperadamente bem-sucedida")
        except Exception as e:
            print(f"   ⚠️  Erro esperado: {e}")
        print()
        
        # Get API statistics
        print("📊 Estatísticas da API:")
        stats = client.get_api_statistics()
        print(f"   Total de chamadas: {stats['total_calls']}")
        print(f"   Chamadas com erro: {stats['error_calls']}")
        print(f"   Taxa de sucesso: {stats['success_rate']:.1f}%")
        print()
        
        # Check log files
        log_dir = Path("logs/binance")
        print("📁 Verificando arquivos de log:")
        
        api_log = log_dir / "binance_api.log"
        if api_log.exists():
            print(f"   ✅ {api_log} - {api_log.stat().st_size} bytes")
        else:
            print(f"   ❌ {api_log} - Não encontrado")
        
        error_log = log_dir / "binance_errors.log"
        if error_log.exists():
            print(f"   ✅ {error_log} - {error_log.stat().st_size} bytes")
        else:
            print(f"   ⚠️  {error_log} - Não encontrado (normal se não houver erros)")
        
        # Check error detail files
        error_files = list(log_dir.glob("error_*.log"))
        if error_files:
            print(f"   📋 {len(error_files)} arquivos de erro detalhados encontrados")
            for error_file in error_files[-3:]:  # Show last 3
                print(f"      - {error_file.name}")
        else:
            print(f"   📋 Nenhum arquivo de erro detalhado encontrado")
        
        print()
        print("=" * 50)
        print("✅ Teste de logging concluído!")
        print()
        print("💡 Para visualizar os logs:")
        print("   python3 view_binance_logs.py --stats")
        print("   python3 view_binance_logs.py --errors 5")
        print("   python3 view_binance_logs.py --calls 10")
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()


def test_log_sanitization():
    """Testa a sanitização de dados sensíveis"""
    
    print("\n🔒 Testando Sanitização de Dados Sensíveis")
    print("=" * 50)
    
    try:
        from src.utils.binance_logger import BinanceLogger
        
        logger = BinanceLogger()
        
        # Test data with sensitive information
        test_data = {
            'apiKey': 'sensitive_api_key_12345',
            'signature': 'sensitive_signature_67890',
            'timestamp': '1234567890',
            'symbol': 'BTCBRL',
            'headers': {
                'X-MBX-APIKEY': 'sensitive_header_key_abcdef',
                'Content-Type': 'application/json'
            }
        }
        
        # Test sanitization
        sanitized = logger._sanitize_sensitive_data(test_data)
        
        print("📋 Dados originais (simulados):")
        print(f"   apiKey: {test_data['apiKey']}")
        print(f"   signature: {test_data['signature']}")
        print(f"   headers: {test_data['headers']}")
        print()
        
        print("🔒 Dados sanitizados:")
        print(f"   apiKey: {sanitized['apiKey']}")
        print(f"   signature: {sanitized['signature']}")
        print(f"   headers: {sanitized['headers']}")
        print()
        
        # Verify sensitive data is redacted
        if sanitized['apiKey'] == '***REDACTED***':
            print("✅ apiKey foi sanitizado corretamente")
        else:
            print("❌ apiKey não foi sanitizado")
        
        if sanitized['signature'] == '***REDACTED***':
            print("✅ signature foi sanitizado corretamente")
        else:
            print("❌ signature não foi sanitizado")
        
        if 'sensitive_header_key_abcdef' not in str(sanitized['headers']):
            print("✅ header API key foi sanitizado corretamente")
        else:
            print("❌ header API key não foi sanitizado")
        
        print()
        print("✅ Teste de sanitização concluído!")
        
    except Exception as e:
        print(f"❌ Erro no teste de sanitização: {e}")


if __name__ == "__main__":
    test_binance_logging()
    test_log_sanitization() 
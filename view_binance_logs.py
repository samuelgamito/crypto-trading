#!/usr/bin/env python3
"""
Script para visualizar e analisar logs da Binance API
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.config.config import Config
from src.api.binance_client import BinanceClient


def view_recent_errors(limit: int = 10):
    """View recent API errors"""
    log_dir = Path("logs/binance")
    error_log = log_dir / "binance_errors.log"
    
    if not error_log.exists():
        print("❌ Nenhum arquivo de erro encontrado")
        return
    
    print(f"🔍 Últimos {limit} erros da API Binance:")
    print("=" * 60)
    
    with open(error_log, 'r') as f:
        lines = f.readlines()
    
    # Parse error lines
    errors = []
    current_error = {}
    
    for line in lines:
        if "API ERROR" in line or "API EXCEPTION" in line:
            if current_error:
                errors.append(current_error)
            current_error = {'line': line.strip()}
        elif current_error and line.strip():
            current_error['details'] = line.strip()
    
    if current_error:
        errors.append(current_error)
    
    # Show recent errors
    for i, error in enumerate(errors[-limit:], 1):
        print(f"\n{i}. {error['line']}")
        if 'details' in error:
            print(f"   {error['details']}")
    
    print(f"\n📊 Total de erros encontrados: {len(errors)}")


def view_api_statistics():
    """View API call statistics"""
    try:
        config = Config()
        client = BinanceClient(config)
        stats = client.get_api_statistics()
        
        print("📊 Estatísticas da API Binance:")
        print("=" * 40)
        print(f"Total de chamadas: {stats['total_calls']}")
        print(f"Chamadas com erro: {stats['error_calls']}")
        print(f"Taxa de sucesso: {stats['success_rate']:.1f}%")
        
        if stats['total_calls'] > 0:
            success_rate = stats['success_rate']
            if success_rate >= 95:
                status = "🟢 Excelente"
            elif success_rate >= 90:
                status = "🟡 Bom"
            elif success_rate >= 80:
                status = "🟠 Atenção"
            else:
                status = "🔴 Crítico"
            
            print(f"Status: {status}")
        
    except Exception as e:
        print(f"❌ Erro ao obter estatísticas: {e}")


def view_error_details(error_id: str = None):
    """View detailed error information"""
    log_dir = Path("logs/binance")
    
    if error_id:
        # View specific error file
        error_file = log_dir / f"error_{error_id}.log"
        if error_file.exists():
            print(f"📋 Detalhes do erro: {error_id}")
            print("=" * 60)
            with open(error_file, 'r') as f:
                print(f.read())
        else:
            print(f"❌ Arquivo de erro {error_id} não encontrado")
    else:
        # List all error files
        error_files = list(log_dir.glob("error_*.log"))
        
        if not error_files:
            print("❌ Nenhum arquivo de erro detalhado encontrado")
            return
        
        print("📋 Arquivos de erro disponíveis:")
        print("=" * 40)
        
        for error_file in sorted(error_files, key=lambda x: x.stat().st_mtime, reverse=True):
            file_id = error_file.stem.replace("error_", "")
            file_time = datetime.fromtimestamp(error_file.stat().st_mtime)
            print(f"   {file_id} - {file_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        print(f"\n💡 Use: python3 view_binance_logs.py --error <ID> para ver detalhes")


def view_recent_api_calls(limit: int = 20):
    """View recent API calls"""
    log_dir = Path("logs/binance")
    api_log = log_dir / "binance_api.log"
    
    if not api_log.exists():
        print("❌ Nenhum arquivo de log da API encontrado")
        return
    
    print(f"📞 Últimas {limit} chamadas da API:")
    print("=" * 60)
    
    with open(api_log, 'r') as f:
        lines = f.readlines()
    
    # Filter API call lines
    api_calls = []
    for line in lines:
        if "API REQUEST" in line or "API RESPONSE" in line:
            api_calls.append(line.strip())
    
    # Show recent calls
    for call in api_calls[-limit:]:
        print(call)


def cleanup_old_logs(days: int = 30):
    """Clean up old log files"""
    try:
        config = Config()
        client = BinanceClient(config)
        client.cleanup_old_logs(days)
        print(f"✅ Logs antigos (mais de {days} dias) foram removidos")
    except Exception as e:
        print(f"❌ Erro ao limpar logs: {e}")


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Visualizar logs da Binance API")
    parser.add_argument("--errors", "-e", type=int, default=10, 
                       help="Número de erros recentes para mostrar (padrão: 10)")
    parser.add_argument("--stats", "-s", action="store_true",
                       help="Mostrar estatísticas da API")
    parser.add_argument("--error", "-d", type=str,
                       help="Mostrar detalhes de um erro específico")
    parser.add_argument("--calls", "-c", type=int, default=20,
                       help="Número de chamadas recentes para mostrar (padrão: 20)")
    parser.add_argument("--cleanup", type=int, default=30,
                       help="Limpar logs antigos (dias, padrão: 30)")
    
    args = parser.parse_args()
    
    if args.stats:
        view_api_statistics()
    elif args.error:
        view_error_details(args.error)
    elif args.cleanup:
        cleanup_old_logs(args.cleanup)
    elif args.calls:
        view_recent_api_calls(args.calls)
    else:
        # Default: show recent errors
        view_recent_errors(args.errors)
        
        print("\n" + "=" * 60)
        print("📋 Comandos disponíveis:")
        print("   python3 view_binance_logs.py --stats          # Estatísticas")
        print("   python3 view_binance_logs.py --errors 5       # Últimos 5 erros")
        print("   python3 view_binance_logs.py --calls 10       # Últimas 10 chamadas")
        print("   python3 view_binance_logs.py --error <ID>     # Detalhes de erro")
        print("   python3 view_binance_logs.py --cleanup 7      # Limpar logs > 7 dias")


if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
"""
Script simples para testar a colocação de uma ordem na Binance
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.config.config import Config
from src.api.binance_client import BinanceClient


def test_simple_order():
    """Testa a colocação de uma ordem simples"""
    
    print("🧪 Teste Simples de Ordem na Binance")
    print("=" * 50)
    
    try:
        # Load configuration
        config = Config()
        print(f"✅ Configuração carregada")
        print(f"   Symbol: {config.default_symbol}")
        print(f"   Testnet: {config.testnet}")
        print()
        
        # Initialize Binance client
        client = BinanceClient(config)
        print(f"✅ Cliente Binance inicializado")
        print()
        
        # Get current price
        print("📊 Obtendo preço atual...")
        ticker = client.get_ticker_price(config.default_symbol)
        current_price = float(ticker['price'])
        print(f"   Preço atual: R$ {current_price:,.2f}")
        print()
        
        # Get account balance
        print("💰 Obtendo saldo da conta...")
        account_info = client.get_account_info()
        balances = account_info.get('balances', [])
        
        # Find BRL balance
        brl_balance = None
        for balance in balances:
            if balance['asset'] == 'BRL':
                brl_balance = float(balance['free'])
                break
        
        if brl_balance is None:
            print("❌ Saldo BRL não encontrado")
            return
        
        print(f"   Saldo BRL: R$ {brl_balance:,.2f}")
        print()
        
        # Calculate a small test order (R$ 50)
        test_amount_brl = 50.0
        quantity = test_amount_brl / current_price
        
        # Round to 5 decimal places (BTC precision)
        quantity = round(quantity, 5)
        
        print("📈 Parâmetros da Ordem de Teste:")
        print("-" * 40)
        print(f"   Valor: R$ {test_amount_brl:,.2f}")
        print(f"   Quantidade: {quantity:.8f} BTC")
        print(f"   Preço estimado: R$ {quantity * current_price:,.2f}")
        print()
        
        # Check if we have enough balance
        if test_amount_brl > brl_balance:
            print(f"❌ Saldo insuficiente: R$ {brl_balance:,.2f} < R$ {test_amount_brl:,.2f}")
            return
        
        print("✅ Saldo suficiente para o teste!")
        print()
        
        # Confirm order placement
        print("⚠️  ATENÇÃO: Esta é uma ordem REAL!")
        print(f"   Symbol: {config.default_symbol}")
        print(f"   Side: BUY")
        print(f"   Type: MARKET")
        print(f"   Quantity: {quantity:.5f} BTC")
        print(f"   Estimated Value: R$ {test_amount_brl:,.2f}")
        print()
        
        if config.testnet:
            print("🟡 Modo TESTNET - Ordem será executada no ambiente de teste")
        else:
            print("🔴 Modo PRODUÇÃO - Ordem será executada com dinheiro real!")
        
        print()
        
        # Ask for confirmation
        confirm = input("🤔 Confirmar ordem de teste? (yes/no): ").lower().strip()
        
        if confirm not in ['yes', 'y', 'sim', 's']:
            print("❌ Ordem cancelada pelo usuário")
            return
        
        print()
        print("🚀 Executando ordem de teste...")
        print("-" * 40)
        
        # Place the order
        order_result = client.place_order(
            symbol=config.default_symbol,
            side='BUY',
            order_type='MARKET',
            quantity=quantity
        )
        
        print("✅ Ordem executada com sucesso!")
        print()
        
        # Display order details
        print("📋 Detalhes da Ordem:")
        print("-" * 40)
        print(f"   Order ID: {order_result.get('orderId', 'N/A')}")
        print(f"   Symbol: {order_result.get('symbol', 'N/A')}")
        print(f"   Side: {order_result.get('side', 'N/A')}")
        print(f"   Type: {order_result.get('type', 'N/A')}")
        print(f"   Status: {order_result.get('status', 'N/A')}")
        print(f"   Quantity: {order_result.get('executedQty', 'N/A')}")
        
        # Show fills if available
        fills = order_result.get('fills', [])
        if fills:
            print(f"   Fills: {len(fills)}")
            for i, fill in enumerate(fills):
                print(f"     Fill {i+1}: {fill.get('qty', 'N/A')} @ R$ {float(fill.get('price', 0)):,.2f}")
        
        print()
        
        # Get updated balance
        print("💰 Saldo Atualizado:")
        print("-" * 40)
        
        updated_account = client.get_account_info()
        updated_balances = updated_account.get('balances', [])
        
        updated_brl = None
        updated_btc = None
        
        for balance in updated_balances:
            if balance['asset'] == 'BRL':
                updated_brl = float(balance['free'])
            elif balance['asset'] == 'BTC':
                updated_btc = float(balance['free'])
        
        if updated_brl is not None:
            print(f"   BRL: R$ {updated_brl:,.2f}")
        if updated_btc is not None:
            print(f"   BTC: {updated_btc:.6f}")
        
        print()
        print("=" * 50)
        print("✅ Teste de ordem concluído com sucesso!")
        
        # Log API statistics
        api_stats = client.get_api_statistics()
        print(f"📊 API Calls: {api_stats['total_calls']} total, {api_stats['error_calls']} errors, {api_stats['success_rate']:.1f}% success rate")
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()


def test_connection_only():
    """Testa apenas a conexão e configuração"""
    
    print("🔗 Teste de Conexão com Binance")
    print("=" * 40)
    
    try:
        # Load configuration
        config = Config()
        print(f"✅ Configuração carregada")
        print(f"   Symbol: {config.default_symbol}")
        print(f"   Testnet: {config.testnet}")
        print(f"   API Key: {config.api_key[:10]}...")
        print()
        
        # Initialize Binance client
        client = BinanceClient(config)
        print(f"✅ Cliente Binance inicializado")
        print()
        
        # Test connection with ticker price
        print("🏓 Testando conexão...")
        print("   Conexão estabelecida com sucesso!")
        print()
        
        # Test ticker price
        print("💰 Obtendo preço...")
        ticker = client.get_ticker_price(config.default_symbol)
        current_price = float(ticker['price'])
        print(f"   Preço {config.default_symbol}: R$ {current_price:,.2f}")
        print()
        
        # Test account info
        print("📊 Obtendo informações da conta...")
        account_info = client.get_account_info()
        balances = account_info.get('balances', [])
        
        # Show some balances
        print("   Saldos:")
        for balance in balances:
            free = float(balance['free'])
            if free > 0:
                print(f"     {balance['asset']}: {free:,.8f}")
        
        print()
        print("✅ Conexão testada com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro no teste de conexão: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Teste simples de ordem na Binance")
    parser.add_argument("--connection-only", "-c", action="store_true",
                       help="Apenas testar conexão, sem executar ordem")
    
    args = parser.parse_args()
    
    if args.connection_only:
        test_connection_only()
    else:
        test_simple_order()


if __name__ == "__main__":
    main() 
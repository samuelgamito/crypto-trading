#!/usr/bin/env python3
"""
Script para testar a venda de BTC na Binance
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.config.config import Config
from src.api.binance_client import BinanceClient
from src.utils.fee_manager import FeeManager


def test_sell_order():
    """Testa a venda de BTC"""
    
    print("🔴 Teste de Venda de BTC na Binance")
    print("=" * 50)
    
    try:
        # Load configuration
        config = Config()
        print(f"✅ Configuração carregada")
        print(f"   Symbol: {config.default_symbol}")
        print(f"   Testnet: {config.testnet}")
        print()
        
        # Initialize Binance client and fee manager
        client = BinanceClient(config)
        fee_manager = FeeManager(client)
        print(f"✅ Cliente Binance e Fee Manager inicializados")
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
        
        # Find BTC balance
        btc_balance = None
        for balance in balances:
            if balance['asset'] == 'BTC':
                btc_balance = float(balance['free'])
                break
        
        if btc_balance is None or btc_balance <= 0:
            print("❌ Saldo BTC não encontrado ou insuficiente")
            return
        
        print(f"   Saldo BTC: {btc_balance:.8f} BTC")
        print(f"   Valor em BRL: R$ {btc_balance * current_price:,.2f}")
        print()
        
        # Calculate sell quantity (use 50% of available balance for test)
        sell_percentage = 50.0
        raw_quantity = btc_balance * (sell_percentage / 100.0)
        
        # Round quantity using fee manager
        quantity = fee_manager.round_quantity(raw_quantity, config.default_symbol)
        
        # Validate the order parameters
        validation = fee_manager.validate_order_parameters(config.default_symbol, quantity)
        
        if not validation['valid']:
            print("❌ Validação da ordem falhou:")
            for error in validation['errors']:
                print(f"   - {error}")
            return
        
        # Calculate expected proceeds
        expected_proceeds = fee_manager.calculate_sell_proceeds(quantity, config.default_symbol)
        fee_amount = (quantity * current_price) - expected_proceeds
        
        print("📈 Parâmetros da Ordem de Venda:")
        print("-" * 40)
        print(f"   Quantidade: {quantity:.8f} BTC")
        print(f"   Preço estimado: R$ {current_price:,.2f}")
        print(f"   Valor bruto: R$ {quantity * current_price:,.2f}")
        print(f"   Taxa estimada: R$ {fee_amount:.2f}")
        print(f"   Valor líquido: R$ {expected_proceeds:.2f}")
        print()
        
        # Check if we have enough balance
        if quantity > btc_balance:
            print(f"❌ Saldo insuficiente: {btc_balance:.8f} BTC < {quantity:.8f} BTC")
            return
        
        print("✅ Saldo suficiente para a venda!")
        print()
        
        # Confirm order placement
        print("⚠️  ATENÇÃO: Esta é uma ordem REAL de VENDA!")
        print(f"   Symbol: {config.default_symbol}")
        print(f"   Side: SELL")
        print(f"   Type: MARKET")
        print(f"   Quantity: {quantity:.8f} BTC")
        print(f"   Estimated Proceeds: R$ {expected_proceeds:.2f}")
        print()
        
        if config.testnet:
            print("🟡 Modo TESTNET - Ordem será executada no ambiente de teste")
        else:
            print("🔴 Modo PRODUÇÃO - Ordem será executada com dinheiro real!")
        
        print()
        
        # Ask for confirmation
        confirm = input("🤔 Confirmar ordem de venda? (yes/no): ").lower().strip()
        
        if confirm not in ['yes', 'y', 'sim', 's']:
            print("❌ Ordem cancelada pelo usuário")
            return
        
        print()
        print("🚀 Executando ordem de venda...")
        print("-" * 40)
        
        # Place the order
        order_result = client.place_order(
            symbol=config.default_symbol,
            side='SELL',
            order_type='MARKET',
            quantity=quantity
        )
        
        print("✅ Ordem de venda executada com sucesso!")
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
            total_proceeds = 0.0
            for i, fill in enumerate(fills):
                qty = float(fill.get('qty', 0))
                price = float(fill.get('price', 0))
                commission = float(fill.get('commission', 0))
                proceeds = qty * price - commission
                total_proceeds += proceeds
                print(f"     Fill {i+1}: {qty:.8f} @ R$ {price:,.2f} (comissão: R$ {commission:.2f})")
            print(f"   Total Proceeds: R$ {total_proceeds:.2f}")
        
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
            print(f"   BTC: {updated_btc:.8f}")
        
        print()
        print("=" * 50)
        print("✅ Teste de venda concluído com sucesso!")
        
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
        ticker = client.get_ticker_price(config.default_symbol)
        current_price = float(ticker['price'])
        print(f"   Conexão estabelecida com sucesso!")
        print(f"   Preço atual: R$ {current_price:,.2f}")
        print()
        
        # Get account balance
        account_info = client.get_account_info()
        balances = account_info.get('balances', [])
        
        btc_balance = None
        brl_balance = None
        
        for balance in balances:
            if balance['asset'] == 'BTC':
                btc_balance = float(balance['free'])
            elif balance['asset'] == 'BRL':
                brl_balance = float(balance['free'])
        
        print("💰 Saldos da Conta:")
        print("-" * 40)
        if btc_balance is not None:
            print(f"   BTC: {btc_balance:.8f} (R$ {btc_balance * current_price:,.2f})")
        if brl_balance is not None:
            print(f"   BRL: R$ {brl_balance:,.2f}")
        
        print()
        print("=" * 40)
        print("✅ Teste de conexão concluído!")
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Função principal"""
    print("🔴 Script de Teste de Venda de BTC")
    print("=" * 50)
    print()
    print("Escolha uma opção:")
    print("1. Testar venda de BTC")
    print("2. Testar apenas conexão")
    print("3. Sair")
    print()
    
    choice = input("Digite sua escolha (1-3): ").strip()
    
    if choice == '1':
        test_sell_order()
    elif choice == '2':
        test_connection_only()
    elif choice == '3':
        print("👋 Saindo...")
    else:
        print("❌ Opção inválida")


if __name__ == "__main__":
    main() 
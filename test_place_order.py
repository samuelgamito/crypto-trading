#!/usr/bin/env python3
"""
Script para testar a colocação de uma ordem real na Binance
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.config.config import Config
from src.api.binance_client import BinanceClient
from src.utils.fee_manager import FeeManager


def test_place_order():
    """Testa a colocação de uma ordem real"""
    
    print("🧪 Testando Colocação de Ordem Real na Binance")
    print("=" * 60)
    
    try:
        # Load configuration
        config = Config()
        print(f"✅ Configuração carregada")
        print(f"   Symbol: {config.default_symbol}")
        print(f"   Testnet: {config.testnet}")
        print(f"   Trade Amount: R$ {config.trade_amount}")
        print(f"   Trade Percentage: {config.trade_percentage}%")
        print()
        
        # Initialize Binance client
        client = BinanceClient(config)
        print(f"✅ Cliente Binance inicializado")
        print()
        
        # Initialize fee manager
        fee_manager = FeeManager(client)
        print(f"✅ Fee Manager inicializado")
        print()
        
        # Get current account info
        print("📊 Informações da Conta:")
        print("-" * 40)
        
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
        
        # Get current price
        ticker = client.get_ticker_price(config.default_symbol)
        current_price = float(ticker['price'])
        print(f"   Preço atual: R$ {current_price:,.2f}")
        print()
        
        # Calculate order parameters
        print("📈 Cálculo dos Parâmetros da Ordem:")
        print("-" * 40)
        
        # Calculate trade amount based on percentage
        total_wallet_brl = brl_balance  # Simplified for test
        trade_amount_brl = total_wallet_brl * (config.trade_percentage / 100.0)
        
        print(f"   Saldo total: R$ {total_wallet_brl:,.2f}")
        print(f"   Percentual de trade: {config.trade_percentage}%")
        print(f"   Valor do trade: R$ {trade_amount_brl:,.2f}")
        
        # Get fee information
        fee_summary = fee_manager.get_fee_summary(config.default_symbol)
        print(f"   Taxa taker: {fee_summary['taker_fee_percent']:.3f}%")
        
        # Calculate quantity
        raw_quantity = trade_amount_brl / current_price
        quantity = fee_manager.round_quantity(raw_quantity, config.default_symbol)
        actual_value = quantity * current_price
        
        print(f"   Quantidade bruta: {raw_quantity:.6f} BTC")
        print(f"   Quantidade arredondada: {quantity:.6f} BTC")
        print(f"   Valor real: R$ {actual_value:,.2f}")
        
        # Validate order parameters
        validation = fee_manager.validate_order_parameters(
            config.default_symbol, quantity, current_price
        )
        
        print(f"   Válido: {validation['valid']}")
        if not validation['valid']:
            print(f"   Erros: {validation['errors']}")
            return
        
        print()
        
        # Check if we have enough balance
        if actual_value > brl_balance:
            print(f"❌ Saldo insuficiente: R$ {brl_balance:,.2f} < R$ {actual_value:,.2f}")
            return
        
        print("✅ Parâmetros da ordem válidos!")
        print()
        
        # Confirm order placement
        print("⚠️  ATENÇÃO: Esta é uma ordem REAL!")
        print(f"   Symbol: {config.default_symbol}")
        print(f"   Side: BUY")
        print(f"   Type: MARKET")
        print(f"   Quantity: {quantity:.6f} BTC")
        print(f"   Estimated Value: R$ {actual_value:,.2f}")
        print()
        
        if config.testnet:
            print("🟡 Modo TESTNET - Ordem será executada no ambiente de teste")
        else:
            print("🔴 Modo PRODUÇÃO - Ordem será executada com dinheiro real!")
        
        print()
        
        # Ask for confirmation
        confirm = input("🤔 Confirmar ordem? (yes/no): ").lower().strip()
        
        if confirm not in ['yes', 'y', 'sim', 's']:
            print("❌ Ordem cancelada pelo usuário")
            return
        
        print()
        print("🚀 Executando ordem...")
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
        print(f"   Price: R$ {float(order_result.get('fills', [{}])[0].get('price', 0)):,.2f}")
        
        # Calculate actual cost
        fills = order_result.get('fills', [])
        total_cost = sum(float(fill.get('qty', 0)) * float(fill.get('price', 0)) for fill in fills)
        total_fee = sum(float(fill.get('commission', 0)) for fill in fills)
        
        print(f"   Total Cost: R$ {total_cost:,.2f}")
        print(f"   Total Fee: R$ {total_fee:,.2f}")
        print(f"   Net Cost: R$ {total_cost - total_fee:,.2f}")
        
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
        print("=" * 60)
        print("✅ Teste de ordem concluído com sucesso!")
        
        # Log API statistics
        api_stats = client.get_api_statistics()
        print(f"📊 API Calls: {api_stats['total_calls']} total, {api_stats['error_calls']} errors, {api_stats['success_rate']:.1f}% success rate")
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()


def test_order_validation_only():
    """Testa apenas a validação da ordem sem executar"""
    
    print("🧪 Testando Validação de Ordem (SEM EXECUTAR)")
    print("=" * 60)
    
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
        
        # Initialize fee manager
        fee_manager = FeeManager(client)
        print(f"✅ Fee Manager inicializado")
        print()
        
        # Get current price
        ticker = client.get_ticker_price(config.default_symbol)
        current_price = float(ticker['price'])
        print(f"💰 Preço atual: R$ {current_price:,.2f}")
        print()
        
        # Test different quantities
        test_quantities = [0.0001, 0.001, 0.01, 0.1]
        
        print("📊 Teste de Validação de Quantidades:")
        print("-" * 40)
        
        for qty in test_quantities:
            rounded_qty = fee_manager.round_quantity(qty, config.default_symbol)
            validation = fee_manager.validate_order_parameters(
                config.default_symbol, rounded_qty, current_price
            )
            
            order_value = rounded_qty * current_price
            
            print(f"   Quantidade: {qty:.6f} -> {rounded_qty:.6f}")
            print(f"   Valor: R$ {order_value:,.2f}")
            print(f"   Válido: {validation['valid']}")
            if not validation['valid']:
                print(f"   Erros: {validation['errors']}")
            print()
        
        print("✅ Teste de validação concluído!")
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Testar colocação de ordem na Binance")
    parser.add_argument("--validation-only", "-v", action="store_true",
                       help="Apenas testar validação, sem executar ordem")
    
    args = parser.parse_args()
    
    if args.validation_only:
        test_order_validation_only()
    else:
        test_place_order()


if __name__ == "__main__":
    main() 
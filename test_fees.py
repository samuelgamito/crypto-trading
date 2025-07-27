#!/usr/bin/env python3
"""
Script para testar o sistema de taxas da Binance
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.config.config import Config
from src.api.binance_client import BinanceClient
from src.utils.fee_manager import FeeManager


def test_fee_system():
    """Testa o sistema de taxas"""
    
    print("🔧 Testando Sistema de Taxas da Binance")
    print("=" * 50)
    
    try:
        # Load configuration
        config = Config()
        print(f"✅ Configuração carregada")
        print(f"   Symbol: {config.default_symbol}")
        print(f"   Include Fees: {config.include_fees}")
        print(f"   Fee Buffer: {config.fee_buffer_percentage}%")
        print()
        
        # Initialize Binance client
        binance_client = BinanceClient(config)
        print(f"✅ Cliente Binance inicializado")
        print()
        
        # Initialize fee manager
        fee_manager = FeeManager(binance_client)
        print(f"✅ Fee Manager inicializado")
        print()
        
        # Test fee information for BTCBRL
        symbol = config.default_symbol
        print(f"📊 Informações de Taxas para {symbol}:")
        print("-" * 40)
        
        fee_summary = fee_manager.get_fee_summary(symbol)
        print(f"   Maker Fee: {fee_summary['maker_fee_percent']:.3f}%")
        print(f"   Taker Fee: {fee_summary['taker_fee_percent']:.3f}%")
        print(f"   Min Fee: {fee_summary['min_fee']:.6f}")
        print()
        
        # Test fee calculations
        print(f"💰 Teste de Cálculos de Taxas:")
        print("-" * 40)
        
        # Get current price
        ticker = binance_client.get_ticker_price(symbol)
        current_price = float(ticker['price'])
        print(f"   Preço atual: {current_price:,.2f}")
        print()
        
        # Test buy scenario
        trade_value_brl = 1000.0  # R$ 1000
        quantity = trade_value_brl / current_price
        
        print(f"🟢 Cenário de COMPRA:")
        print(f"   Valor do trade: R$ {trade_value_brl:,.2f}")
        print(f"   Quantidade BTC: {quantity:.6f}")
        
        fee_amount = fee_manager.calculate_fee_amount(trade_value_brl, symbol, 'MARKET')
        net_quantity = fee_manager.calculate_net_quantity(quantity, symbol, 'MARKET')
        
        print(f"   Taxa estimada: R$ {fee_amount:,.2f}")
        print(f"   Quantidade líquida: {net_quantity:.6f} BTC")
        print(f"   Valor líquido: R$ {net_quantity * current_price:,.2f}")
        print()
        
        # Test sell scenario
        print(f"🔴 Cenário de VENDA:")
        print(f"   Quantidade BTC: {quantity:.6f}")
        print(f"   Valor bruto: R$ {trade_value_brl:,.2f}")
        
        sell_fee = fee_manager.calculate_fee_amount(trade_value_brl, symbol, 'MARKET')
        net_proceeds = fee_manager.calculate_sell_proceeds(quantity, symbol, 'MARKET')
        
        print(f"   Taxa estimada: R$ {sell_fee:,.2f}")
        print(f"   Proventos líquidos: R$ {net_proceeds:,.2f}")
        print()
        
        # Test position size calculation with fees
        print(f"📈 Teste de Cálculo de Posição com Taxas:")
        print("-" * 40)
        
        # Simulate wallet balance
        wallet_balance_brl = 2000.0
        trade_percentage = 5.0
        
        desired_trade_amount = wallet_balance_brl * (trade_percentage / 100.0)
        print(f"   Saldo da carteira: R$ {wallet_balance_brl:,.2f}")
        print(f"   Percentual de trade: {trade_percentage}%")
        print(f"   Valor desejado: R$ {desired_trade_amount:,.2f}")
        
        # Calculate required amount including fees
        required_gross = desired_trade_amount / (1 - fee_summary['taker_fee_rate'])
        fee_buffer = required_gross * (config.fee_buffer_percentage / 100.0)
        total_required = required_gross + fee_buffer
        
        print(f"   Valor bruto necessário: R$ {required_gross:,.2f}")
        print(f"   Buffer de taxa: R$ {fee_buffer:,.2f}")
        print(f"   Total necessário: R$ {total_required:,.2f}")
        
        if total_required <= wallet_balance_brl:
            print(f"   ✅ Saldo suficiente para incluir taxas")
        else:
            print(f"   ⚠️  Saldo insuficiente para incluir taxas")
            # Calculate what we can actually trade
            available_for_trade = wallet_balance_brl * (1 - fee_summary['taker_fee_rate'] - config.fee_buffer_percentage / 100.0)
            print(f"   Valor disponível para trade: R$ {available_for_trade:,.2f}")
        
        print()
        
        # Show fee impact on profitability
        print(f"📊 Impacto das Taxas na Lucratividade:")
        print("-" * 40)
        
        # Example: Buy at 100, sell at 105 (5% gain)
        buy_price = 100.0
        sell_price = 105.0
        quantity_example = 1.0
        
        buy_value = quantity_example * buy_price
        buy_fee = fee_manager.calculate_fee_amount(buy_value, symbol, 'MARKET')
        total_buy_cost = buy_value + buy_fee
        
        sell_value = quantity_example * sell_price
        sell_fee = fee_manager.calculate_fee_amount(sell_value, symbol, 'MARKET')
        net_sell_proceeds = sell_value - sell_fee
        
        gross_profit = sell_value - buy_value
        net_profit = net_sell_proceeds - total_buy_cost
        total_fees = buy_fee + sell_fee
        
        print(f"   Preço de compra: R$ {buy_price:,.2f}")
        print(f"   Preço de venda: R$ {sell_price:,.2f}")
        print(f"   Ganho bruto: R$ {gross_profit:,.2f} ({gross_profit/buy_value*100:.2f}%)")
        print(f"   Taxas totais: R$ {total_fees:,.2f}")
        print(f"   Ganho líquido: R$ {net_profit:,.2f} ({net_profit/total_buy_cost*100:.2f}%)")
        print(f"   Impacto das taxas: {total_fees/gross_profit*100:.2f}% do ganho bruto")
        
        print()
        print("=" * 50)
        print("✅ Teste de taxas concluído com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro no teste de taxas: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_fee_system() 
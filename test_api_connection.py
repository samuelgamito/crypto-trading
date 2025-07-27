#!/usr/bin/env python3
"""
Script para testar a conexão com a API da Binance
"""

import os
import sys
import time
import hmac
import hashlib
import requests
from urllib.parse import urlencode
from dotenv import load_dotenv

def test_binance_connection():
    """Testa a conexão com a API da Binance"""
    
    # Carrega as variáveis de ambiente
    load_dotenv()
    
    # Obtém as configurações
    api_key = os.getenv('BINANCE_API_KEY')
    secret_key = os.getenv('BINANCE_SECRET_KEY')
    testnet = os.getenv('BINANCE_TESTNET', 'true').lower() == 'true'
    
    # Define a URL base
    if testnet:
        base_url = "https://testnet.binance.vision"
    else:
        base_url = "https://api.binance.com"
    
    print(f"🔧 Configuração:")
    print(f"   API Key: {api_key[:10]}...{api_key[-10:] if api_key else 'N/A'}")
    print(f"   Secret Key: {secret_key[:10]}...{secret_key[-10:] if secret_key else 'N/A'}")
    print(f"   Testnet: {testnet}")
    print(f"   Base URL: {base_url}")
    print()
    
    # Valida as chaves
    if not api_key or not secret_key:
        print("❌ Erro: BINANCE_API_KEY e BINANCE_SECRET_KEY devem estar configuradas")
        return False
    
    # Testa endpoint público primeiro
    print("🔍 Testando endpoint público...")
    try:
        response = requests.get(f"{base_url}/api/v3/ping")
        if response.status_code == 200:
            print("✅ Endpoint público funcionando")
        else:
            print(f"❌ Endpoint público falhou: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao acessar endpoint público: {e}")
        return False
    
    # Testa endpoint de preço (público)
    print("🔍 Testando endpoint de preço...")
    try:
        response = requests.get(f"{base_url}/api/v3/ticker/price", params={'symbol': 'BTCUSDT'})
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Preço BTCUSDT: ${float(data['price']):,.2f}")
        else:
            print(f"❌ Endpoint de preço falhou: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao obter preço: {e}")
        return False
    
    # Testa endpoint autenticado
    print("🔍 Testando endpoint autenticado...")
    try:
        # Prepara parâmetros para assinatura
        params = {
            'timestamp': int(time.time() * 1000)
        }
        
        # Gera assinatura
        query_string = urlencode(params)
        signature = hmac.new(
            secret_key.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        params['signature'] = signature
        
        # Debug info
        print(f"🔍 Debug Info:")
        print(f"   Timestamp: {params['timestamp']}")
        print(f"   Query String: {query_string}")
        print(f"   Signature: {signature[:20]}...{signature[-20:]}")
        print(f"   API Key Length: {len(api_key)}")
        print(f"   Secret Key Length: {len(secret_key)}")
        print()
        
        # Faz a requisição
        headers = {
            'X-MBX-APIKEY': api_key,
            'Content-Type': 'application/json'
        }
        
        response = requests.get(
            f"{base_url}/api/v3/account",
            params=params,
            headers=headers
        )
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📊 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Autenticação bem-sucedida!")
            print(f"📊 Permissões: {data.get('permissions', [])}")
            
            # Mostra alguns saldos
            balances = data.get('balances', [])
            print("\n💰 Saldos da Conta:")
            print("-" * 40)
            
            # Procura especificamente por BRL primeiro
            brl_balance = None
            for balance in balances:
                if balance['asset'] == 'BRL':
                    brl_balance = balance
                    break
            
            # Mostra BRL em destaque se existir
            if brl_balance:
                free_brl = float(brl_balance['free'])
                locked_brl = float(brl_balance['locked'])
                total_brl = free_brl + locked_brl
                print(f"🇧🇷 BRL (Real Brasileiro):")
                print(f"   💰 Livre: R$ {free_brl:,.2f}")
                print(f"   🔒 Bloqueado: R$ {locked_brl:,.2f}")
                print(f"   📊 Total: R$ {total_brl:,.2f}")
                print()
            
            # Mostra outros saldos com valores
            other_balances = []
            for balance in balances:
                free = float(balance['free'])
                locked = float(balance['locked'])
                if free > 0 or locked > 0:
                    other_balances.append((balance['asset'], free, locked))
            
            if other_balances:
                print("💱 Outros Saldos:")
                for asset, free, locked in other_balances:
                    if asset != 'BRL':  # Não mostrar BRL novamente
                        total = free + locked
                        print(f"   {asset}: {free:,.8f} (livre) / {locked:,.8f} (bloqueado) = {total:,.8f}")
            
            # Resumo total em BRL
            if brl_balance:
                print(f"\n📈 Resumo: R$ {total_brl:,.2f} disponível para trading")
            
        elif response.status_code == 401:
            print("❌ Erro 401: Falha na autenticação")
            print(f"📊 Response: {response.text}")
            
            # Sugestões para resolver
            print("\n🔧 Possíveis soluções:")
            print("   1. Verifique se as chaves estão corretas")
            print("   2. Verifique se as chaves têm permissões de trading")
            print("   3. Verifique se está usando a URL correta (testnet vs produção)")
            print("   4. Verifique se o IP está na whitelist (se configurado)")
            print("   5. Aguarde alguns minutos - novas chaves podem demorar para ativar")
            print("   6. Verifique se sua conta Binance está totalmente verificada")
            
        else:
            print(f"❌ Erro {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro ao testar autenticação: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 Testando conexão com Binance API...")
    print("=" * 50)
    
    success = test_binance_connection()
    
    print("=" * 50)
    if success:
        print("✅ Teste concluído com sucesso!")
    else:
        print("❌ Teste falhou!")
        sys.exit(1) 
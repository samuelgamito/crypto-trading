# Sistema de Logging da Binance API

## 📋 Visão Geral

O sistema de logging da Binance API foi implementado para capturar e registrar todas as chamadas da API, incluindo requests, responses e erros, facilitando o debug e monitoramento do bot de trading.

## 🔧 Componentes Implementados

### 1. BinanceLogger (src/utils/binance_logger.py)

Classe especializada para logging da API Binance:

- **Logging detalhado** de requests e responses
- **Sanitização automática** de dados sensíveis
- **Arquivos de erro específicos** para cada falha
- **Estatísticas de API** em tempo real
- **Cleanup automático** de logs antigos

### 2. Integração com BinanceClient

O cliente Binance foi atualizado para usar o sistema de logging:

- **Logging automático** de todas as chamadas
- **Tracking de request ID** para rastreamento
- **Captura de erros** com detalhes completos
- **Estatísticas integradas** no trading bot

### 3. Scripts de Visualização

- **view_binance_logs.py** - Visualizar e analisar logs
- **test_binance_logging.py** - Testar o sistema de logging

## 📁 Estrutura de Arquivos

```
logs/binance/
├── binance_api.log          # Todas as chamadas da API
├── binance_errors.log       # Apenas erros
└── error_<ID>.log          # Arquivos detalhados por erro
```

## 🔒 Segurança e Privacidade

### Sanitização Automática

O sistema remove automaticamente dados sensíveis dos logs:

```python
# Dados originais
{
    "apiKey": "sensitive_api_key_12345",
    "signature": "sensitive_signature_67890",
    "headers": {"X-MBX-APIKEY": "sensitive_header_key"}
}

# Dados sanitizados
{
    "apiKey": "***REDACTED***",
    "signature": "***REDACTED***", 
    "headers": {"X-MBX-APIKEY": "sensit...key"}
}
```

### Campos Sanitizados

- `apiKey` → `***REDACTED***`
- `signature` → `***REDACTED***`
- `secret` → `***REDACTED***`
- `password` → `***REDACTED***`
- `X-MBX-APIKEY` → `primeiros_8...últimos_4`

## 📊 Funcionalidades

### 1. Logging de Requests

```python
# Exemplo de log de request
API REQUEST [20250727_155032_914864_47270811]: GET /api/v3/ticker/price
Request details: {
  "method": "GET",
  "endpoint": "/api/v3/ticker/price",
  "params": {"symbol": "BTCBRL"},
  "headers": {"X-MBX-APIKEY": "uSZjIull...rcxo"}
}
```

### 2. Logging de Responses

```python
# Exemplo de log de response
API RESPONSE [20250727_155032_914864_47270811]: 200 - Success
Response details: {
  "status_code": 200,
  "response": {"symbol": "BTCBRL", "price": "665862.00000000"}
}
```

### 3. Logging de Erros

```python
# Exemplo de log de erro
API ERROR [20250727_155033_237457_9289b464]: 400 - Invalid symbol
Error details: {
  "status_code": 400,
  "response": {"code": -1121, "msg": "Invalid symbol"}
}
```

### 4. Arquivos de Erro Detalhados

Cada erro gera um arquivo específico com:

- **Timestamp** do erro
- **Tipo de erro** (HTTPError, ConnectionError, etc.)
- **Mensagem de erro** completa
- **Parâmetros da request** (sanitizados)
- **Informações de debugging** sugeridas

## 🛠️ Como Usar

### 1. Visualizar Estatísticas

```bash
python3 view_binance_logs.py --stats
```

**Saída:**
```
📊 Estatísticas da API Binance:
========================================
Total de chamadas: 150
Chamadas com erro: 3
Taxa de sucesso: 98.0%
Status: 🟢 Excelente
```

### 2. Visualizar Erros Recentes

```bash
python3 view_binance_logs.py --errors 5
```

**Saída:**
```
🔍 Últimos 5 erros da API Binance:
============================================================
1. API ERROR [20250727_155033_237457_9289b464]: 400 - Invalid symbol
2. API ERROR [20250727_155034_123456_abcdef12]: 401 - Invalid API-key
```

### 3. Visualizar Chamadas Recentes

```bash
python3 view_binance_logs.py --calls 10
```

**Saída:**
```
📞 Últimas 10 chamadas da API:
============================================================
2025-07-27 15:50:32,914 - API REQUEST [ID]: GET /api/v3/ticker/price
2025-07-27 15:50:33,237 - API RESPONSE [ID]: 200 - Success
```

### 4. Ver Detalhes de Erro Específico

```bash
python3 view_binance_logs.py --error 20250727_155033_237457_9289b464
```

**Saída:**
```
📋 Detalhes do erro: 20250727_155033_237457_9289b464
============================================================
Timestamp: 2025-07-27T15:50:33.511840
Error Type: HTTPError
Error Message: 400 Client Error: Bad Request
Method: GET
Endpoint: /api/v3/ticker/price

REQUEST PARAMETERS:
{"symbol": "INVALIDPAIR"}

DEBUGGING INFORMATION:
1. Check if API keys are valid
2. Verify IP whitelist settings
3. Check API permissions
4. Verify request parameters
5. Check Binance API status
```

### 5. Limpar Logs Antigos

```bash
python3 view_binance_logs.py --cleanup 7
```

Remove logs com mais de 7 dias.

## 🧪 Testando o Sistema

### Teste Completo

```bash
python3 test_binance_logging.py
```

**Testa:**
- Chamadas bem-sucedidas
- Chamadas com erro
- Sanitização de dados
- Criação de arquivos de log
- Estatísticas da API

### Teste de Sanitização

O teste verifica se dados sensíveis são removidos corretamente:

```python
# Dados originais
apiKey: sensitive_api_key_12345
signature: sensitive_signature_67890

# Dados sanitizados  
apiKey: ***REDACTED***
signature: ***REDACTED***
```

## 📈 Integração com Trading Bot

### Estatísticas no Resumo

O trading bot agora inclui estatísticas da API:

```
==================================================
TRADING BOT PERFORMANCE SUMMARY
==================================================
Total trades: 15
Win rate: 73.3%
Total P&L: R$ 1,250.50
API Calls: 150 total, 3 errors, 98.0% success rate
==================================================
```

### Logs Automáticos

Todas as operações de trading são automaticamente logadas:

- **Validação de quantidades** antes das ordens
- **Execução de ordens** (compra/venda)
- **Erros de API** com detalhes completos
- **Estatísticas de performance** da API

## 🔍 Debugging com Logs

### 1. Identificar Problemas de API

```bash
# Ver erros recentes
python3 view_binance_logs.py --errors 10

# Ver detalhes de erro específico
python3 view_binance_logs.py --error <ID>
```

### 2. Analisar Performance

```bash
# Ver estatísticas
python3 view_binance_logs.py --stats

# Ver chamadas recentes
python3 view_binance_logs.py --calls 50
```

### 3. Verificar Configuração

```bash
# Ver headers das requests
grep "headers" logs/binance/binance_api.log

# Verificar se API key está sendo enviada
grep "X-MBX-APIKEY" logs/binance/binance_api.log
```

## 🚀 Benefícios

### ✅ Vantagens Implementadas

- **Debugging completo**: Request/response detalhados
- **Segurança**: Sanitização automática de dados sensíveis
- **Rastreabilidade**: Request ID único para cada chamada
- **Monitoramento**: Estatísticas em tempo real
- **Manutenção**: Cleanup automático de logs antigos
- **Flexibilidade**: Múltiplos níveis de log

### 📊 Impacto no Desenvolvimento

- **Debug mais rápido**: Informações completas sobre erros
- **Monitoramento proativo**: Identificação de problemas antes que afetem o trading
- **Histórico completo**: Rastreamento de todas as operações
- **Segurança aprimorada**: Dados sensíveis protegidos
- **Performance tracking**: Métricas de sucesso da API

## 🔄 Manutenção

### Limpeza Automática

O sistema limpa automaticamente logs antigos:

```python
# Limpar logs com mais de 30 dias
client.cleanup_old_logs(30)
```

### Monitoramento de Espaço

Verificar tamanho dos logs periodicamente:

```bash
du -sh logs/binance/
ls -la logs/binance/ | wc -l
```

### Backup de Logs Importantes

Para logs críticos, considere backup:

```bash
# Backup de logs de erro
cp logs/binance/binance_errors.log backup/
cp logs/binance/error_*.log backup/
```

---

## 📞 Suporte

Para problemas com o sistema de logging:

1. **Execute o teste**: `python3 test_binance_logging.py`
2. **Verifique os logs**: `python3 view_binance_logs.py --stats`
3. **Analise erros**: `python3 view_binance_logs.py --errors 10`
4. **Verifique permissões**: `ls -la logs/binance/`
5. **Consulte documentação**: Este arquivo e logs gerados 
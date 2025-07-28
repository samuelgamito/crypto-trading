"""
Binance API logging utilities for debugging
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import hashlib


class BinanceLogger:
    """Specialized logger for Binance API calls with request/response logging"""
    
    def __init__(self, log_dir: str = "logs/binance"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Create main logger
        self.logger = logging.getLogger("binance_api")
        self.logger.setLevel(logging.DEBUG)
        
        # Create file handler for all API calls
        self._setup_file_handlers()
        
        # Track API call statistics
        self.call_count = 0
        self.error_count = 0
    
    def _setup_file_handlers(self):
        """Setup file handlers for different log levels"""
        
        # Handler for all API calls (successful and failed)
        all_handler = logging.FileHandler(self.log_dir / "binance_api.log")
        all_handler.setLevel(logging.DEBUG)
        all_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        all_handler.setFormatter(all_formatter)
        self.logger.addHandler(all_handler)
        
        # Handler for errors only
        error_handler = logging.FileHandler(self.log_dir / "binance_errors.log")
        error_handler.setLevel(logging.ERROR)
        error_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        error_handler.setFormatter(error_formatter)
        self.logger.addHandler(error_handler)
    
    def _sanitize_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive data from logs (API keys, signatures)"""
        sanitized = data.copy()
        
        # Remove sensitive fields
        sensitive_fields = ['apiKey', 'signature', 'secret', 'password']
        for field in sensitive_fields:
            if field in sanitized:
                sanitized[field] = '***REDACTED***'
        
        # Sanitize API key in headers
        if 'headers' in sanitized:
            headers = sanitized['headers'].copy()
            if 'X-MBX-APIKEY' in headers:
                headers['X-MBX-APIKEY'] = f"{headers['X-MBX-APIKEY'][:8]}...{headers['X-MBX-APIKEY'][-4:]}"
            sanitized['headers'] = headers
        
        return sanitized
    
    def create_request_id(self, method: str, endpoint: str) -> str:
        """Create a unique request ID for tracking"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        request_hash = hashlib.md5(f"{method}_{endpoint}_{timestamp}".encode()).hexdigest()[:8]
        return f"{timestamp}_{request_hash}"
    
    def log_api_call(self, method: str, endpoint: str, params: Dict = None, 
                    headers: Dict = None, request_id: str = None) -> str:
        """Log an API call request"""
        
        if request_id is None:
            request_id = self.create_request_id(method, endpoint)
        
        self.call_count += 1
        
        # Prepare request data
        request_data = {
            'request_id': request_id,
            'timestamp': datetime.now().isoformat(),
            'method': method,
            'endpoint': endpoint,
            'params': params or {},
            'headers': headers or {}
        }
        
        # Sanitize sensitive data
        sanitized_request = self._sanitize_sensitive_data(request_data)
        
        # Log the request
        self.logger.info(f"API REQUEST [{request_id}]: {method} {endpoint}")
        self.logger.debug(f"Request details [{request_id}]: {json.dumps(sanitized_request, indent=2)}")
        
        return request_id
    
    def log_api_response(self, request_id: str, response_data: Dict, 
                        status_code: int, success: bool = True):
        """Log an API call response"""
        
        # Prepare response data
        response_log = {
            'request_id': request_id,
            'timestamp': datetime.now().isoformat(),
            'status_code': status_code,
            'success': success,
            'response': response_data
        }
        
        # Log based on success/failure
        if success:
            self.logger.info(f"API RESPONSE [{request_id}]: {status_code} - Success")
            self.logger.debug(f"Response details [{request_id}]: {json.dumps(response_log, indent=2)}")
        else:
            self.error_count += 1
            self.logger.error(f"API ERROR [{request_id}]: {status_code} - {response_data.get('msg', 'Unknown error')}")
            self.logger.error(f"Error details [{request_id}]: {json.dumps(response_log, indent=2)}")
    
    def log_api_error(self, request_id: str, error: Exception, 
                     method: str, endpoint: str, params: Dict = None):
        """Log an API call error"""
        
        self.error_count += 1
        
        error_data = {
            'request_id': request_id,
            'timestamp': datetime.now().isoformat(),
            'method': method,
            'endpoint': endpoint,
            'params': self._sanitize_sensitive_data(params or {}),
            'error_type': type(error).__name__,
            'error_message': str(error)
        }
        
        # Log the error
        self.logger.error(f"API EXCEPTION [{request_id}]: {type(error).__name__}: {str(error)}")
        self.logger.error(f"Exception details [{request_id}]: {json.dumps(error_data, indent=2)}")
        
        # Create detailed error log file
        self._create_error_log_file(request_id, error_data)
    
    def _create_error_log_file(self, request_id: str, error_data: Dict):
        """Create a detailed error log file for debugging"""
        
        error_file = self.log_dir / f"error_{request_id}.log"
        
        with open(error_file, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write(f"BINANCE API ERROR LOG - {request_id}\n")
            f.write("=" * 80 + "\n")
            f.write(f"Timestamp: {error_data['timestamp']}\n")
            f.write(f"Error Type: {error_data['error_type']}\n")
            f.write(f"Error Message: {error_data['error_message']}\n")
            f.write(f"Method: {error_data['method']}\n")
            f.write(f"Endpoint: {error_data['endpoint']}\n")
            f.write("\n" + "=" * 80 + "\n")
            f.write("REQUEST PARAMETERS:\n")
            f.write("=" * 80 + "\n")
            f.write(json.dumps(error_data['params'], indent=2))
            f.write("\n\n" + "=" * 80 + "\n")
            f.write("DEBUGGING INFORMATION:\n")
            f.write("=" * 80 + "\n")
            f.write("1. Check if API keys are valid\n")
            f.write("2. Verify IP whitelist settings\n")
            f.write("3. Check API permissions\n")
            f.write("4. Verify request parameters\n")
            f.write("5. Check Binance API status\n")
            f.write("\n" + "=" * 80 + "\n")
    
    def get_statistics(self) -> Dict[str, int]:
        """Get API call statistics"""
        return {
            'total_calls': self.call_count,
            'error_calls': self.error_count,
            'success_rate': ((self.call_count - self.error_count) / self.call_count * 100) if self.call_count > 0 else 0
        }
    
    def log_statistics(self):
        """Log current statistics"""
        stats = self.get_statistics()
        self.logger.info(f"API Statistics: {stats['total_calls']} calls, {stats['error_calls']} errors, {stats['success_rate']:.1f}% success rate")
    
    def cleanup_old_logs(self, days: int = 30):
        """Clean up old log files"""
        cutoff_date = datetime.now().timestamp() - (days * 24 * 60 * 60)
        
        for log_file in self.log_dir.glob("error_*.log"):
            if log_file.stat().st_mtime < cutoff_date:
                try:
                    log_file.unlink()
                    self.logger.info(f"Cleaned up old log file: {log_file}")
                except Exception as e:
                    self.logger.warning(f"Failed to clean up {log_file}: {e}") 
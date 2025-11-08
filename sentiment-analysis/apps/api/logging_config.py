"""
Structured logging configuration
Provides JSON and text logging with correlation IDs
"""

import logging
import sys
import json
from datetime import datetime
from typing import Any, Dict
from contextvars import ContextVar
from uuid import uuid4

from pythonjsonlogger import jsonlogger
from config import get_settings

settings = get_settings()

# Context variable for correlation ID
correlation_id_ctx: ContextVar[str] = ContextVar('correlation_id', default='')


class CorrelationIdFilter(logging.Filter):
    """Add correlation ID to log records"""

    def filter(self, record: logging.LogRecord) -> bool:
        record.correlation_id = correlation_id_ctx.get() or str(uuid4())
        return True


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter with additional fields"""

    def add_fields(
        self,
        log_record: Dict[str, Any],
        record: logging.LogRecord,
        message_dict: Dict[str, Any]
    ) -> None:
        super().add_fields(log_record, record, message_dict)

        # Add standard fields
        log_record['timestamp'] = datetime.utcnow().isoformat()
        log_record['level'] = record.levelname
        log_record['logger'] = record.name
        log_record['correlation_id'] = getattr(record, 'correlation_id', '')

        # Add service information
        log_record['service'] = 'sentiment-analysis-api'
        log_record['environment'] = settings.ENVIRONMENT
        log_record['version'] = settings.VERSION

        # Add exception info if present
        if record.exc_info:
            log_record['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': self.formatException(record.exc_info)
            }

        # Add custom fields from extra
        if hasattr(record, 'extra_fields'):
            log_record.update(record.extra_fields)


class ColoredFormatter(logging.Formatter):
    """Colored formatter for console output"""

    COLORS = {
        'DEBUG': '\033[36m',  # Cyan
        'INFO': '\033[32m',   # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',  # Red
        'CRITICAL': '\033[35m',  # Magenta
    }
    RESET = '\033[0m'

    def format(self, record: logging.LogRecord) -> str:
        # Add color to level name
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.RESET}"

        # Format the message
        formatted = super().format(record)

        # Reset levelname
        record.levelname = levelname

        return formatted


def setup_logging():
    """Configure logging for the application"""

    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))

    # Remove existing handlers
    root_logger.handlers.clear()

    # Add correlation ID filter
    correlation_filter = CorrelationIdFilter()

    # JSON or text format based on configuration
    if settings.LOG_FORMAT.lower() == 'json':
        # JSON formatter for production
        formatter = CustomJsonFormatter(
            '%(timestamp)s %(level)s %(logger)s %(message)s'
        )
    else:
        # Colored text formatter for development
        formatter = ColoredFormatter(
            '%(asctime)s [%(correlation_id)s] %(levelname)s %(name)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.addFilter(correlation_filter)
    root_logger.addHandler(console_handler)

    # Suppress noisy loggers
    logging.getLogger('uvicorn.access').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)

    logging.info(
        "Logging configured",
        extra={'extra_fields': {
            'log_level': settings.LOG_LEVEL,
            'log_format': settings.LOG_FORMAT
        }}
    )


def set_correlation_id(correlation_id: str):
    """Set correlation ID for current context"""
    correlation_id_ctx.set(correlation_id)


def get_correlation_id() -> str:
    """Get correlation ID for current context"""
    return correlation_id_ctx.get()


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance

    Args:
        name: Logger name (usually __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


# Structured logging helpers
def log_api_request(
    logger: logging.Logger,
    method: str,
    path: str,
    status_code: int,
    duration_ms: float,
    **kwargs
):
    """Log API request with structured data"""
    logger.info(
        f"{method} {path} {status_code} {duration_ms}ms",
        extra={'extra_fields': {
            'event_type': 'api_request',
            'http_method': method,
            'http_path': path,
            'http_status': status_code,
            'duration_ms': duration_ms,
            **kwargs
        }}
    )


def log_prediction(
    logger: logging.Logger,
    text: str,
    predicted_sentiment: str,
    confidence: float,
    duration_ms: float,
    **kwargs
):
    """Log sentiment prediction with structured data"""
    logger.info(
        f"Predicted {predicted_sentiment} with {confidence:.2%} confidence",
        extra={'extra_fields': {
            'event_type': 'prediction',
            'text_length': len(text),
            'predicted_sentiment': predicted_sentiment,
            'confidence': confidence,
            'duration_ms': duration_ms,
            **kwargs
        }}
    )


def log_model_training(
    logger: logging.Logger,
    model_name: str,
    training_samples: int,
    f1_score: float,
    duration_seconds: float,
    **kwargs
):
    """Log model training with structured data"""
    logger.info(
        f"Trained model {model_name} - F1: {f1_score:.3f}",
        extra={'extra_fields': {
            'event_type': 'model_training',
            'model_name': model_name,
            'training_samples': training_samples,
            'f1_score': f1_score,
            'duration_seconds': duration_seconds,
            **kwargs
        }}
    )


def log_celery_task(
    logger: logging.Logger,
    task_name: str,
    task_id: str,
    status: str,
    duration_seconds: float,
    **kwargs
):
    """Log Celery task execution with structured data"""
    logger.info(
        f"Task {task_name} {status}",
        extra={'extra_fields': {
            'event_type': 'celery_task',
            'task_name': task_name,
            'task_id': task_id,
            'status': status,
            'duration_seconds': duration_seconds,
            **kwargs
        }}
    )


def log_error(
    logger: logging.Logger,
    error: Exception,
    context: str,
    **kwargs
):
    """Log error with structured data"""
    logger.error(
        f"Error in {context}: {str(error)}",
        exc_info=True,
        extra={'extra_fields': {
            'event_type': 'error',
            'context': context,
            'error_type': type(error).__name__,
            'error_message': str(error),
            **kwargs
        }}
    )

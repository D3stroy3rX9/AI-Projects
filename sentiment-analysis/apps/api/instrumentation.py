"""
OpenTelemetry instrumentation for the API
Provides distributed tracing, metrics, and logging
"""

import logging
from typing import Optional
from contextlib import asynccontextmanager

from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from prometheus_client import start_http_server, Counter, Histogram, Gauge, Info

from config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


# Prometheus metrics
PREDICTION_COUNTER = Counter(
    'sentiment_predictions_total',
    'Total number of sentiment predictions',
    ['sentiment', 'source']
)

PREDICTION_DURATION = Histogram(
    'sentiment_prediction_duration_seconds',
    'Time spent on sentiment prediction',
    ['model_version'],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0]
)

BATCH_SIZE = Histogram(
    'sentiment_batch_size',
    'Size of batch analysis requests',
    buckets=[1, 5, 10, 25, 50, 100, 250, 500, 1000]
)

MODEL_TRAINING_DURATION = Histogram(
    'model_training_duration_seconds',
    'Time spent training models',
    buckets=[1, 5, 10, 30, 60, 120, 300, 600, 1800, 3600]
)

MODEL_F1_SCORE = Gauge(
    'model_f1_score',
    'F1 score of the active model',
    ['model_name']
)

ACTIVE_REQUESTS = Gauge(
    'http_active_requests',
    'Number of active HTTP requests',
    ['method', 'endpoint']
)

DB_POOL_SIZE = Gauge(
    'database_pool_size',
    'Current database connection pool size'
)

DB_POOL_OVERFLOW = Gauge(
    'database_pool_overflow',
    'Current database connection pool overflow'
)

CELERY_TASK_COUNTER = Counter(
    'celery_tasks_total',
    'Total number of Celery tasks',
    ['task_name', 'status']
)

CELERY_TASK_DURATION = Histogram(
    'celery_task_duration_seconds',
    'Time spent executing Celery tasks',
    ['task_name'],
    buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0]
)

API_INFO = Info(
    'sentiment_api',
    'Sentiment Analysis API information'
)


def setup_tracing() -> Optional[TracerProvider]:
    """
    Set up OpenTelemetry tracing

    Returns:
        TracerProvider or None if disabled
    """
    if not settings.ENABLE_TRACING:
        logger.info("Tracing disabled")
        return None

    # Create resource with service information
    resource = Resource.create({
        SERVICE_NAME: "sentiment-analysis-api",
        SERVICE_VERSION: settings.VERSION,
        "environment": settings.ENVIRONMENT,
    })

    # Create tracer provider
    tracer_provider = TracerProvider(resource=resource)

    # Set up Jaeger exporter
    if settings.JAEGER_ENDPOINT:
        jaeger_exporter = JaegerExporter(
            agent_host_name=settings.JAEGER_ENDPOINT.split(':')[0],
            agent_port=int(settings.JAEGER_ENDPOINT.split(':')[1]) if ':' in settings.JAEGER_ENDPOINT else 6831,
        )
        tracer_provider.add_span_processor(
            BatchSpanProcessor(jaeger_exporter)
        )
        logger.info(f"Jaeger exporter configured: {settings.JAEGER_ENDPOINT}")

    # Set up OTLP exporter (for cloud providers)
    if settings.OTLP_ENDPOINT:
        otlp_exporter = OTLPSpanExporter(
            endpoint=settings.OTLP_ENDPOINT,
            insecure=True  # Use TLS in production
        )
        tracer_provider.add_span_processor(
            BatchSpanProcessor(otlp_exporter)
        )
        logger.info(f"OTLP exporter configured: {settings.OTLP_ENDPOINT}")

    # Set as global tracer provider
    trace.set_tracer_provider(tracer_provider)

    logger.info("Tracing initialized successfully")
    return tracer_provider


def setup_metrics() -> Optional[MeterProvider]:
    """
    Set up OpenTelemetry metrics

    Returns:
        MeterProvider or None if disabled
    """
    if not settings.ENABLE_METRICS:
        logger.info("Metrics disabled")
        return None

    # Create resource
    resource = Resource.create({
        SERVICE_NAME: "sentiment-analysis-api",
        SERVICE_VERSION: settings.VERSION,
    })

    # Create metric readers
    readers = []

    # Prometheus exporter
    if settings.PROMETHEUS_PORT:
        prometheus_reader = PrometheusMetricReader()
        readers.append(prometheus_reader)

        # Start Prometheus HTTP server
        try:
            start_http_server(port=settings.PROMETHEUS_PORT, addr="0.0.0.0")
            logger.info(f"Prometheus metrics server started on port {settings.PROMETHEUS_PORT}")
        except Exception as e:
            logger.error(f"Failed to start Prometheus server: {e}")

    # OTLP exporter
    if settings.OTLP_ENDPOINT:
        otlp_reader = PeriodicExportingMetricReader(
            OTLPMetricExporter(
                endpoint=settings.OTLP_ENDPOINT,
                insecure=True
            ),
            export_interval_millis=60000  # Export every 60 seconds
        )
        readers.append(otlp_reader)

    # Create meter provider
    meter_provider = MeterProvider(
        resource=resource,
        metric_readers=readers
    )

    # Set as global meter provider
    metrics.set_meter_provider(meter_provider)

    # Set API info metric
    API_INFO.info({
        'version': settings.VERSION,
        'environment': settings.ENVIRONMENT,
    })

    logger.info("Metrics initialized successfully")
    return meter_provider


def instrument_fastapi(app):
    """
    Instrument FastAPI application with OpenTelemetry

    Args:
        app: FastAPI application instance
    """
    if not settings.ENABLE_TRACING:
        return

    FastAPIInstrumentor.instrument_app(
        app,
        excluded_urls="health,metrics,docs,openapi.json",
        tracer_provider=trace.get_tracer_provider()
    )
    logger.info("FastAPI instrumented")


def instrument_sqlalchemy(engine):
    """
    Instrument SQLAlchemy engine with OpenTelemetry

    Args:
        engine: SQLAlchemy engine instance
    """
    if not settings.ENABLE_TRACING:
        return

    SQLAlchemyInstrumentor().instrument(
        engine=engine,
        tracer_provider=trace.get_tracer_provider()
    )
    logger.info("SQLAlchemy instrumented")


def instrument_redis():
    """Instrument Redis with OpenTelemetry"""
    if not settings.ENABLE_TRACING:
        return

    RedisInstrumentor().instrument(
        tracer_provider=trace.get_tracer_provider()
    )
    logger.info("Redis instrumented")


def get_tracer(name: str = __name__):
    """
    Get a tracer instance

    Args:
        name: Tracer name

    Returns:
        Tracer instance
    """
    return trace.get_tracer(name)


def get_meter(name: str = __name__):
    """
    Get a meter instance

    Args:
        name: Meter name

    Returns:
        Meter instance
    """
    return metrics.get_meter(name)


# Context manager for tracking active requests
@asynccontextmanager
async def track_request(method: str, endpoint: str):
    """
    Track active HTTP requests

    Args:
        method: HTTP method
        endpoint: API endpoint
    """
    ACTIVE_REQUESTS.labels(method=method, endpoint=endpoint).inc()
    try:
        yield
    finally:
        ACTIVE_REQUESTS.labels(method=method, endpoint=endpoint).dec()


def record_prediction(sentiment: str, source: str, duration: float, model_version: str):
    """
    Record a sentiment prediction

    Args:
        sentiment: Predicted sentiment label
        source: Source of the request
        duration: Prediction duration in seconds
        model_version: Version of the model used
    """
    PREDICTION_COUNTER.labels(sentiment=sentiment, source=source).inc()
    PREDICTION_DURATION.labels(model_version=model_version).observe(duration)


def record_batch_analysis(batch_size: int):
    """
    Record batch analysis

    Args:
        batch_size: Number of texts in the batch
    """
    BATCH_SIZE.observe(batch_size)


def record_model_training(duration: float, f1_score: float, model_name: str):
    """
    Record model training

    Args:
        duration: Training duration in seconds
        f1_score: Model F1 score
        model_name: Name of the model
    """
    MODEL_TRAINING_DURATION.observe(duration)
    MODEL_F1_SCORE.labels(model_name=model_name).set(f1_score)


def record_celery_task(task_name: str, status: str, duration: float):
    """
    Record Celery task execution

    Args:
        task_name: Name of the task
        status: Task status (success, failure, retry)
        duration: Task duration in seconds
    """
    CELERY_TASK_COUNTER.labels(task_name=task_name, status=status).inc()
    CELERY_TASK_DURATION.labels(task_name=task_name).observe(duration)


def update_db_pool_metrics(pool_size: int, pool_overflow: int):
    """
    Update database pool metrics

    Args:
        pool_size: Current pool size
        pool_overflow: Current pool overflow
    """
    DB_POOL_SIZE.set(pool_size)
    DB_POOL_OVERFLOW.set(pool_overflow)


def initialize_instrumentation(app=None, engine=None):
    """
    Initialize all instrumentation

    Args:
        app: FastAPI application (optional)
        engine: SQLAlchemy engine (optional)
    """
    logger.info("Initializing instrumentation...")

    # Set up tracing
    setup_tracing()

    # Set up metrics
    setup_metrics()

    # Instrument components
    if app:
        instrument_fastapi(app)

    if engine:
        instrument_sqlalchemy(engine)

    instrument_redis()

    logger.info("Instrumentation initialized successfully")

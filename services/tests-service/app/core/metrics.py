"""
Prometheus Metrics Configuration
This module provides centralized metrics configuration for the microservice.
"""
from typing import Callable

from prometheus_client import Counter, Histogram, Gauge, Info
from prometheus_fastapi_instrumentator import Instrumentator


# Application info metric
app_info = Info('app', 'Application information')

# Custom metrics for database operations
db_queries_total = Counter(
    'db_queries_total',
    'Total number of database queries',
    ['service', 'operation', 'table']
)

db_query_duration_seconds = Histogram(
    'db_query_duration_seconds',
    'Database query duration in seconds',
    ['service', 'operation', 'table'],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0]
)

db_connections_active = Gauge(
    'db_connections_active',
    'Number of active database connections',
    ['service']
)

# Business logic metrics
business_operations_total = Counter(
    'business_operations_total',
    'Total number of business operations',
    ['service', 'operation', 'status']
)

business_operation_duration_seconds = Histogram(
    'business_operation_duration_seconds',
    'Business operation duration in seconds',
    ['service', 'operation'],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0]
)


def setup_metrics(app, service_name: str, service_version: str) -> Callable:
    """
    Setup Prometheus metrics for the FastAPI application.
    
    Args:
        app: FastAPI application instance
        service_name: Name of the microservice
        service_version: Version of the microservice
    
    Returns:
        Instrumentator instance
    """
    # Set application info
    app_info.info({
        'service': service_name,
        'version': service_version
    })
    
    # Create instrumentator
    instrumentator = Instrumentator(
        should_group_status_codes=False,
        should_ignore_untemplated=True,
        should_respect_env_var=True,
        should_instrument_requests_inprogress=True,
        excluded_handlers=["/metrics", "/health", "/"],
        env_var_name="ENABLE_METRICS",
        inprogress_name="http_requests_in_progress",
        inprogress_labels=True
    )
    
    # Instrument the app
    instrumentator.instrument(app)
    
    return instrumentator


def track_db_query(service_name: str, operation: str, table: str):
    """
    Context manager for tracking database query metrics.
    
    Usage:
        with track_db_query("user-service", "SELECT", "users"):
            # Execute database query
            pass
    
    Args:
        service_name: Name of the microservice
        operation: Database operation (SELECT, INSERT, UPDATE, DELETE)
        table: Database table name
    """
    from contextlib import contextmanager
    import time
    
    @contextmanager
    def _tracker():
        start_time = time.time()
        try:
            yield
            db_queries_total.labels(
                service=service_name,
                operation=operation,
                table=table
            ).inc()
        finally:
            duration = time.time() - start_time
            db_query_duration_seconds.labels(
                service=service_name,
                operation=operation,
                table=table
            ).observe(duration)
    
    return _tracker()


def track_business_operation(service_name: str, operation: str):
    """
    Context manager for tracking business operation metrics.
    
    Usage:
        with track_business_operation("user-service", "user_registration"):
            # Execute business logic
            pass
    
    Args:
        service_name: Name of the microservice
        operation: Business operation name
    """
    from contextlib import contextmanager
    import time
    
    @contextmanager
    def _tracker():
        start_time = time.time()
        status = "success"
        try:
            yield
        except Exception as e:
            status = "error"
            raise
        finally:
            duration = time.time() - start_time
            business_operations_total.labels(
                service=service_name,
                operation=operation,
                status=status
            ).inc()
            business_operation_duration_seconds.labels(
                service=service_name,
                operation=operation
            ).observe(duration)
    
    return _tracker()


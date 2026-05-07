# Gunicorn configuration file
import multiprocessing

# Bind to 0.0.0.0:8000
bind = "0.0.0.0:8000"

# Use Uvicorn's worker class for ASGI applications
worker_class = "uvicorn.workers.UvicornWorker"

# Dynamically calculate the number of workers based on CPU cores.
# For async workloads, 2-4 workers per core is often recommended.
workers = multiprocessing.cpu_count() * 2 + 1

# Limit the maximum number of requests a worker will process before restarting
# This helps prevent memory leaks from accumulating.
max_requests = 1000
max_requests_jitter = 50

# Worker timeouts
timeout = 120
keepalive = 5

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

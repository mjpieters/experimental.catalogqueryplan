import os

# report slow query in event.log to identify queries that are performing badly
log_slow_queries = os.environ.get('LOG_SLOW_QUERIES', None)
if log_slow_queries is None:
    LOG_SLOW_QUERIES = False
else:
    LOG_SLOW_QUERIES = log_slow_queries.lower().strip() == 'true'


# only report slow queries that took more than LONG_QUERY_TIME seconds to execute 
long_query_time = os.environ.get('LONG_QUERY_TIME', None)
if  long_query_time is None:
    LONG_QUERY_TIME = 0.01
else:
    LONG_QUERY_TIME = float(long_query_time.strip())

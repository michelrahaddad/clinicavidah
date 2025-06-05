import psutil
import logging
from datetime import datetime
from flask import jsonify
from main import db

def check_system_health():
    """Monitor system health metrics"""
    try:
        health_status = {
            'timestamp': datetime.now().isoformat(),
            'database': check_database_health(),
            'memory': check_memory_usage(),
            'disk': check_disk_usage(),
            'status': 'healthy'
        }
        
        # Determine overall health
        if (health_status['memory']['percent'] > 90 or 
            health_status['disk']['percent'] > 90 or 
            not health_status['database']['connected']):
            health_status['status'] = 'unhealthy'
        elif (health_status['memory']['percent'] > 80 or 
              health_status['disk']['percent'] > 80):
            health_status['status'] = 'warning'
        
        return health_status
        
    except Exception as e:
        logging.error(f'Health check failed: {e}')
        return {
            'timestamp': datetime.now().isoformat(),
            'status': 'error',
            'error': str(e)
        }

def check_database_health():
    """Check database connectivity and basic metrics"""
    try:
        # Test database connection
        result = db.session.execute(db.text("SELECT 1"))
        connected = True
        
        # Get table counts
        tables_info = {}
        table_names = ['medicos', 'pacientes', 'receitas', 'exames_lab', 'exames_img']
        
        for table in table_names:
            count_result = db.session.execute(db.text(f"SELECT COUNT(*) FROM {table}"))
            tables_info[table] = count_result.scalar()
        
        return {
            'connected': connected,
            'tables': tables_info
        }
        
    except Exception as e:
        logging.error(f'Database health check failed: {e}')
        return {
            'connected': False,
            'error': str(e)
        }

def check_memory_usage():
    """Check system memory usage"""
    memory = psutil.virtual_memory()
    return {
        'total': memory.total,
        'available': memory.available,
        'percent': memory.percent,
        'used': memory.used
    }

def check_disk_usage():
    """Check disk usage"""
    disk = psutil.disk_usage('/')
    return {
        'total': disk.total,
        'used': disk.used,
        'free': disk.free,
        'percent': (disk.used / disk.total) * 100
    }

def log_health_metrics():
    """Log health metrics for monitoring"""
    health = check_system_health()
    
    if health['status'] == 'unhealthy':
        logging.warning(f'System health critical: {health}')
    elif health['status'] == 'warning':
        logging.info(f'System health warning: {health}')
    else:
        logging.debug(f'System health good: {health}')
    
    return health
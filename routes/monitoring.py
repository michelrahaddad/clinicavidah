from flask import redirect, url_for, session, Blueprint, render_template, jsonify, request
from models import Medico, Receita, ExameLab, ExameImg, Agendamento, LogSistema
from app import db
from utils.security import require_admin
import psutil
import time
import os
from datetime import datetime, timedelta
from sqlalchemy import text, func

monitoring_bp = Blueprint('monitoring', __name__, url_prefix='/admin/monitoring')

@monitoring_bp.route('/performance')
@require_admin
def performance_dashboard():
    """Performance monitoring dashboard"""
    return render_template('admin/performance.html')

@monitoring_bp.route('/api/system-metrics')
@require_admin
def system_metrics():
    """Get real-time system metrics"""
    try:
        # CPU and Memory metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Network metrics
        network = psutil.net_io_counters()
        
        # Process metrics
        process = psutil.Process(os.getpid())
        
        metrics = {
            'timestamp': int(time.time() * 1000),
            'cpu': {
                'usage': round(cpu_percent, 2),
                'cores': psutil.cpu_count(),
                'load_avg': os.getloadavg() if hasattr(os, 'getloadavg') else [0, 0, 0]
            },
            'memory': {
                'total': memory.total,
                'used': memory.used,
                'available': memory.available,
                'percent': round(memory.percent, 2)
            },
            'disk': {
                'total': disk.total,
                'used': disk.used,
                'free': disk.free,
                'percent': round((disk.used / disk.total) * 100, 2)
            },
            'network': {
                'bytes_sent': network.bytes_sent,
                'bytes_recv': network.bytes_recv,
                'packets_sent': network.packets_sent,
                'packets_recv': network.packets_recv
            },
            'process': {
                'pid': process.pid,
                'memory_percent': round(process.memory_percent(), 2),
                'cpu_percent': round(process.cpu_percent(), 2),
                'num_threads': process.num_threads()
            }
        }
        
        return jsonify(metrics)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@monitoring_bp.route('/api/database-metrics')
@require_admin
def database_metrics():
    """Get database performance metrics"""
    try:
        # Get table sizes and row counts
        tables_info = []
        
        tables = ['medicos', 'receitas', 'exames_lab', 'exames_img', 'agendamentos', 'logs_sistema']
        
        for table in tables:
            try:
                count_result = db.session.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
                size_result = db.session.execute(text(f"SELECT pg_total_relation_size('{table}')")).scalar()
                
                tables_info.append({
                    'table': table,
                    'rows': count_result or 0,
                    'size_bytes': size_result or 0,
                    'size_mb': round((size_result or 0) / (1024 * 1024), 2)
                })
            except Exception as table_error:
                tables_info.append({
                    'table': table,
                    'rows': 0,
                    'size_bytes': 0,
                    'size_mb': 0,
                    'error': str(table_error)
                })
        
        # Database connection info
        db_stats = db.session.execute(text("""
            SELECT 
                numbackends as active_connections,
                xact_commit as transactions_committed,
                xact_rollback as transactions_rolled_back,
                blks_read as blocks_read,
                blks_hit as blocks_hit
            FROM pg_stat_database 
            WHERE datname = current_database()
        """)).first()
        
        return jsonify({
            'timestamp': int(time.time() * 1000),
            'tables': tables_info,
            'connections': {
                'active': db_stats.active_connections if db_stats else 0,
                'max_connections': 100  # Default PostgreSQL max
            },
            'transactions': {
                'committed': db_stats.transactions_committed if db_stats else 0,
                'rolled_back': db_stats.transactions_rolled_back if db_stats else 0
            },
            'cache': {
                'blocks_read': db_stats.blocks_read if db_stats else 0,
                'blocks_hit': db_stats.blocks_hit if db_stats else 0,
                'hit_ratio': round((db_stats.blocks_hit / max(db_stats.blocks_read + db_stats.blocks_hit, 1)) * 100, 2) if db_stats else 0
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@monitoring_bp.route('/api/application-metrics')
@require_admin
def application_metrics():
    """Get application-specific metrics"""
    try:
        now = datetime.utcnow()
        
        # Activity metrics for the last 24 hours
        last_24h = now - timedelta(hours=24)
        last_hour = now - timedelta(hours=1)
        
        # Recent activity counts
        receitas_24h = Receita.query.filter(Receita.created_at >= last_24h).count()
        receitas_1h = Receita.query.filter(Receita.created_at >= last_hour).count()
        
        exames_lab_24h = ExameLab.query.filter(ExameLab.created_at >= last_24h).count()
        exames_img_24h = ExameImg.query.filter(ExameImg.created_at >= last_24h).count()
        
        agendamentos_24h = Agendamento.query.filter(Agendamento.created_at >= last_24h).count()
        
        # Error logs in last 24h
        errors_24h = LogSistema.query.filter(
            LogSistema.timestamp >= last_24h,
            LogSistema.tipo == 'error'
        ).count()
        
        # Top active users (last 24h)
        top_users = db.session.execute(text("""
            SELECT usuario, COUNT(*) as actions
            FROM logs_sistema
            WHERE timestamp >= :last_24h
            GROUP BY usuario
            ORDER BY actions DESC
            LIMIT 5
        """), {'last_24h': last_24h}).fetchall()
        
        # Response time simulation (in real system, this would come from actual metrics)
        avg_response_time = 120 + (receitas_1h * 5)  # Simulate load impact
        
        return jsonify({
            'timestamp': int(time.time() * 1000),
            'activity': {
                'receitas_24h': receitas_24h,
                'receitas_1h': receitas_1h,
                'exames_lab_24h': exames_lab_24h,
                'exames_img_24h': exames_img_24h,
                'agendamentos_24h': agendamentos_24h
            },
            'performance': {
                'avg_response_time_ms': avg_response_time,
                'errors_24h': errors_24h,
                'uptime_hours': 24,  # Simulated
                'requests_per_minute': receitas_1h + exames_lab_24h//24 + exames_img_24h//24
            },
            'top_users': [{'usuario': row.usuario, 'actions': row.actions} for row in top_users],
            'health_status': 'healthy' if errors_24h < 10 and avg_response_time < 500 else 'warning'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@monitoring_bp.route('/api/alerts')
@require_admin
def system_alerts():
    """Get system alerts and warnings"""
    try:
        alerts = []
        
        # Check CPU usage
        cpu_percent = psutil.cpu_percent()
        if cpu_percent > 80:
            alerts.append({
                'type': 'warning',
                'category': 'system',
                'message': f'High CPU usage: {cpu_percent:.1f}%',
                'timestamp': int(time.time() * 1000)
            })
        
        # Check memory usage
        memory = psutil.virtual_memory()
        if memory.percent > 85:
            alerts.append({
                'type': 'warning',
                'category': 'system',
                'message': f'High memory usage: {memory.percent:.1f}%',
                'timestamp': int(time.time() * 1000)
            })
        
        # Check disk space
        disk = psutil.disk_usage('/')
        disk_percent = (disk.used / disk.total) * 100
        if disk_percent > 90:
            alerts.append({
                'type': 'critical',
                'category': 'storage',
                'message': f'Low disk space: {disk_percent:.1f}% used',
                'timestamp': int(time.time() * 1000)
            })
        
        # Check recent errors
        recent_errors = LogSistema.query.filter(
            LogSistema.timestamp >= datetime.utcnow() - timedelta(minutes=30),
            LogSistema.tipo == 'error'
        ).count()
        
        if recent_errors > 5:
            alerts.append({
                'type': 'warning',
                'category': 'application',
                'message': f'{recent_errors} errors in the last 30 minutes',
                'timestamp': int(time.time() * 1000)
            })
        
        # Check database connections (simulated)
        active_connections = 5  # Would be actual count in real system
        if active_connections > 80:
            alerts.append({
                'type': 'warning',
                'category': 'database',
                'message': f'High database connection usage: {active_connections}',
                'timestamp': int(time.time() * 1000)
            })
        
        return jsonify({
            'alerts': alerts,
            'total_count': len(alerts),
            'critical_count': len([a for a in alerts if a['type'] == 'critical']),
            'warning_count': len([a for a in alerts if a['type'] == 'warning'])
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@monitoring_bp.route('/api/performance-history')
@require_admin
def performance_history():
    """Get historical performance data"""
    try:
        # In a real system, this would come from a time-series database
        # For now, we'll simulate historical data
        
        now = int(time.time() * 1000)
        history = []
        
        for i in range(60):  # Last 60 data points (minutes)
            timestamp = now - (i * 60 * 1000)
            
            # Simulate performance metrics
            cpu_usage = 20 + (i % 10) * 3 + (time.time() % 30)
            memory_usage = 45 + (i % 8) * 2
            response_time = 100 + (i % 15) * 10
            
            history.append({
                'timestamp': timestamp,
                'cpu_usage': round(cpu_usage, 2),
                'memory_usage': round(memory_usage, 2),
                'response_time': round(response_time, 2),
                'active_users': max(1, 10 - (i % 12))
            })
        
        return jsonify({
            'history': list(reversed(history)),
            'interval_minutes': 1
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
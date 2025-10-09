import json
import os
from typing import List, Optional
from app.domain.schemas.logs import AuditLogEntry, LogsQuery


class LogService:
    def __init__(self):
        # Ruta absoluta al archivo de logs
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        self.log_file_path = os.path.join(project_root, "logs", "audit.log")
        print(f"🔍 LogService - Ruta del archivo: {self.log_file_path}")
        print(f"📁 Existe archivo: {os.path.exists(self.log_file_path)}")

    def get_logs(self, query: LogsQuery) -> tuple[List[AuditLogEntry], int]:
        """
        Obtiene logs con filtros y paginación.
        Retorna (logs_filtrados, total_count)
        """
        if not os.path.exists(self.log_file_path):
            print(f"❌ Archivo no encontrado: {self.log_file_path}")
            return [], 0

        all_logs = []
        line_count = 0
        
        try:
            with open(self.log_file_path, 'r', encoding='utf-8') as file:
                for line in file:
                    line_count += 1
                    line = line.strip()
                    if line:
                        try:
                            log_data = json.loads(line)
                            all_logs.append(AuditLogEntry(**log_data))
                        except json.JSONDecodeError as e:
                            print(f"❌ Error JSON en línea {line_count}: {e}")
                            continue  # Skip malformed lines
                        except Exception as e:
                            print(f"❌ Error creando AuditLogEntry en línea {line_count}: {e}")
                            continue
            
            print(f"✅ Cargados {len(all_logs)} logs de {line_count} líneas")
            
        except FileNotFoundError:
            print(f"❌ Archivo no encontrado: {self.log_file_path}")
            return [], 0
        except Exception as e:
            print(f"❌ Error leyendo archivo: {e}")
            return [], 0

        # Aplicar filtros
        filtered_logs = self._apply_filters(all_logs, query)
        
        # Ordenar por timestamp (más recientes primero)
        filtered_logs.sort(key=lambda x: x.timestamp, reverse=True)
        
        # Aplicar paginación
        total = len(filtered_logs)
        start_idx = (query.page - 1) * query.page_size
        end_idx = start_idx + query.page_size
        paginated_logs = filtered_logs[start_idx:end_idx]
        
        return paginated_logs, total

    def _apply_filters(self, logs: List[AuditLogEntry], query: LogsQuery) -> List[AuditLogEntry]:
        """Aplica filtros a la lista de logs"""
        filtered = logs
        
        if query.actor:
            filtered = [log for log in filtered if query.actor.lower() in log.actor.lower()]
        
        if query.action:
            filtered = [log for log in filtered if query.action.lower() in log.action.lower()]
        
        if query.provider:
            filtered = [log for log in filtered if query.provider.lower() in log.provider.lower()]
        
        if query.success is not None:
            filtered = [log for log in filtered if log.success == query.success]
        
        if query.vm_id:
            filtered = [log for log in filtered if query.vm_id.lower() in log.vm_id.lower()]
        
        return filtered

    def get_recent_logs(self, limit: int = 100) -> List[AuditLogEntry]:
        """Obtiene los logs más recientes (para dashboard)"""
        query = LogsQuery(page=1, page_size=limit)
        logs, _ = self.get_logs(query)
        return logs

    def get_stats(self) -> dict:
        """Obtiene estadísticas básicas de logs"""
        if not os.path.exists(self.log_file_path):
            return {
                "total_operations": 0,
                "successful_operations": 0,
                "failed_operations": 0,
                "providers": {},
                "actions": {}
            }

        all_logs = []
        try:
            with open(self.log_file_path, 'r', encoding='utf-8') as file:
                for line in file:
                    line = line.strip()
                    if line:
                        try:
                            log_data = json.loads(line)
                            all_logs.append(AuditLogEntry(**log_data))
                        except json.JSONDecodeError:
                            continue
        except FileNotFoundError:
            pass

        total = len(all_logs)
        successful = len([log for log in all_logs if log.success])
        failed = total - successful

        # Contar por proveedor
        providers = {}
        for log in all_logs:
            providers[log.provider] = providers.get(log.provider, 0) + 1

        # Contar por acción
        actions = {}
        for log in all_logs:
            actions[log.action] = actions.get(log.action, 0) + 1

        return {
            "total_operations": total,
            "successful_operations": successful,
            "failed_operations": failed,
            "providers": providers,
            "actions": actions
        }
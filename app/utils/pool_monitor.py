"""Connection pool monitoring utilities."""

from typing import Any, Dict

from sqlalchemy.ext.asyncio import AsyncEngine

from app.db.session import engine


class PoolMonitor:
    """Monitor connection pool status and performance."""

    def __init__(self, engine: AsyncEngine):
        self.engine = engine

    def get_pool_status(self) -> Dict[str, Any]:
        """Get current pool status information."""
        pool = self.engine.pool

        # Get basic pool information
        pool_size = pool.size()
        checked_out = pool.checkedout()
        overflow = pool.overflow()

        # Calculate derived values
        total_connections = pool_size + max(0, overflow)
        available_connections = max(0, pool_size - checked_out)
        utilization_percentage = round((checked_out / pool_size) * 100, 2) if pool_size > 0 else 0

        return {
            "pool_size": pool_size,
            "checked_out": checked_out,
            "overflow": overflow,
            "total_connections": total_connections,
            "available_connections": available_connections,
            "utilization_percentage": utilization_percentage,
            "pool_class": pool.__class__.__name__,
        }

    def get_pool_health(self) -> Dict[str, Any]:
        """Get pool health indicators."""
        status = self.get_pool_status()

        # Health indicators
        health = {"is_healthy": True, "warnings": [], "critical_issues": []}

        # Check utilization
        utilization = status["utilization_percentage"]
        if utilization > 90:
            health["warnings"].append(f"High pool utilization: {utilization}%")
        elif utilization > 95:
            health["critical_issues"].append(f"Critical pool utilization: {utilization}%")
            health["is_healthy"] = False

        # Check overflow usage
        if status["overflow"] > 0:
            health["warnings"].append(f"Using overflow connections: {status['overflow']}")

        # Check if pool is exhausted
        if status["available_connections"] <= 0:
            health["critical_issues"].append("Pool exhausted - no available connections")
            health["is_healthy"] = False

        return health

    def get_pool_recommendations(self) -> Dict[str, Any]:
        """Get recommendations for pool optimization."""
        status = self.get_pool_status()
        recommendations = []

        utilization = status["utilization_percentage"]

        if utilization > 80:
            recommendations.append(
                {
                    "type": "performance",
                    "message": "Consider increasing DB_POOL_SIZE",
                    "current_value": status["pool_size"],
                    "suggested_value": min(int(status["pool_size"] * 1.5), 100),
                }
            )

        if status["overflow"] > status["pool_size"] * 0.5:
            recommendations.append(
                {
                    "type": "overflow",
                    "message": "Consider increasing DB_MAX_OVERFLOW",
                    "current_value": "unknown",  # We don't have access to max_overflow from pool
                    "suggested_value": "Increase by 50%",
                }
            )

        return {"recommendations": recommendations, "total_recommendations": len(recommendations)}

    def get_pool_metrics(self) -> Dict[str, Any]:
        """Get comprehensive pool metrics."""
        status = self.get_pool_status()
        health = self.get_pool_health()
        recommendations = self.get_pool_recommendations()

        return {
            "status": status,
            "health": health,
            "recommendations": recommendations,
            "timestamp": "2024-01-01T00:00:00Z",  # You can add actual timestamp
            "engine_info": {
                "name": self.engine.name,
                "driver": self.engine.driver,
                "pool_class": self.engine.pool.__class__.__name__,
            },
        }


# Global pool monitor instance
pool_monitor = PoolMonitor(engine)


def get_pool_status() -> Dict[str, Any]:
    """Get current pool status."""
    return pool_monitor.get_pool_status()


def get_pool_health() -> Dict[str, Any]:
    """Get pool health indicators."""
    return pool_monitor.get_pool_health()


def get_pool_metrics() -> Dict[str, Any]:
    """Get comprehensive pool metrics."""
    return pool_monitor.get_pool_metrics()


def is_pool_healthy() -> bool:
    """Check if pool is healthy."""
    return pool_monitor.get_pool_health()["is_healthy"]


# Convenience functions for logging
def log_pool_status():
    """Log current pool status (useful for monitoring)."""
    status = get_pool_status()
    health = get_pool_health()

    print(f"Pool Status: {status['pool_size']} total, {status['checked_out']} in use")
    print(f"Utilization: {status['utilization_percentage']}%")
    print(f"Health: {'✅' if health['is_healthy'] else '❌'}")

    if health["warnings"]:
        print(f"Warnings: {', '.join(health['warnings'])}")

    if health["critical_issues"]:
        print(f"Critical Issues: {', '.join(health['critical_issues'])}")


def get_pool_summary() -> str:
    """Get a human-readable pool summary."""
    status = get_pool_status()
    health = get_pool_health()

    summary = f"Pool: {status['pool_size']} connections, {status['utilization_percentage']}% utilized"

    if health["warnings"]:
        summary += f" (⚠️ {len(health['warnings'])} warnings)"

    if health["critical_issues"]:
        summary += f" (🚨 {len(health['critical_issues'])} critical issues)"

    return summary

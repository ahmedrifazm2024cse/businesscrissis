from apscheduler.schedulers.asyncio import AsyncIOScheduler
import logging
from workflows.crisis_workflow import crisis_graph
from workflows.inventory_monitor import run_inventory_monitor
from workflows.forecast_monitor import run_forecast_monitor
from workflows.supplier_monitor import run_supplier_monitor
from workflows.shipment_monitor import run_shipment_monitor
from workflows.warehouse_monitor import run_warehouse_monitor
from workflows.procurement_monitor import run_procurement_monitor
from workflows.cost_monitor import run_cost_monitor
from workflows.route_monitor import run_route_monitor
from workflows.shortage_monitor import run_shortage_monitor
from workflows.autonomous_orchestrator import run_supply_chain_orchestrator

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()

async def scheduled_inventory_scan():
    logger.info("Running scheduled inventory scan...")
    try:
        await crisis_graph.ainvoke({"trigger_event": "Scheduled Inventory Scan"})
    except Exception as e:
        logger.error(f"Scheduled scan failed: {e}")

def start_scheduler():
    # Run every 4 hours
    scheduler.add_job(scheduled_inventory_scan, 'interval', hours=4, id='inventory_scan', replace_existing=True)
    
    # Autonomous Inventory Monitor - runs every 5 minutes
    scheduler.add_job(run_inventory_monitor, 'interval', minutes=5, id='autonomous_inventory_monitor', replace_existing=True)
    
    # Autonomous Demand Forecasting Monitor - runs every 60 minutes
    scheduler.add_job(run_forecast_monitor, 'interval', minutes=60, id='autonomous_forecast_monitor', replace_existing=True)
    
    # Autonomous Supplier Intelligence Monitor - runs every 60 minutes
    scheduler.add_job(run_supplier_monitor, 'interval', minutes=60, id='autonomous_supplier_monitor', replace_existing=True)
    
    # Autonomous Shipment Intelligence Monitor - runs every 30 minutes
    scheduler.add_job(run_shipment_monitor, 'interval', minutes=30, id='autonomous_shipment_monitor', replace_existing=True)
    
    # Autonomous Warehouse Intelligence Monitor - runs every 60 minutes
    scheduler.add_job(run_warehouse_monitor, 'interval', minutes=60, id='autonomous_warehouse_monitor', replace_existing=True)
    
    # Autonomous Procurement Intelligence Monitor - runs every 60 minutes
    scheduler.add_job(run_procurement_monitor, 'interval', minutes=60, id='autonomous_procurement_monitor', replace_existing=True)
    
    # Autonomous Cost Optimization Agent - runs every 60 minutes
    scheduler.add_job(run_cost_monitor, 'interval', minutes=60, id='autonomous_cost_monitor', replace_existing=True)
    
    # Autonomous Route Optimization Agent - runs every 30 minutes
    scheduler.add_job(run_route_monitor, 'interval', minutes=30, id='autonomous_route_monitor', replace_existing=True)
    
    # Autonomous Product Shortage Prediction Agent - runs every 15 minutes
    scheduler.add_job(run_shortage_monitor, 'interval', minutes=15, id='autonomous_shortage_monitor', replace_existing=True)
    
    # Autonomous Supply Chain Orchestrator (Final Intelligence Layer) - runs every 60 minutes
    scheduler.add_job(run_supply_chain_orchestrator, 'interval', minutes=60, id='autonomous_supply_chain_orchestrator', replace_existing=True)
    
    scheduler.start()
    logger.info("APScheduler started.")

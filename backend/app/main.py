import os
from dotenv import load_dotenv
from app.config import UPLOAD_DIR

load_dotenv()
from fastapi import FastAPI

# ===============================
# Auth
# ===============================
from app.api import auth

# ===============================
# Core
# ===============================
from app.api import cities
from app.api import addresses
from app.api import service_zones
from app.api import zone_check
from app.api import area_requests

# ===============================
# Marketplace + Recycling
# ===============================
from app.api import categories
from app.api import products
from app.api import product_images
from app.api import recycling_hubs

# ===============================
# Orders Workflow
# ===============================
from app.api import orders
from app.api import buyer_orders
from app.api import cancellation
from app.api import recycling_completion

# ===============================
# Delivery
# ===============================
from app.api import delivery_actions
from app.api import delivery_dashboard

# ===============================
# Dashboards
# ===============================
from app.api import dashboard
from app.api import admin_dashboard
from app.api import admin_delivery_dashboard

# ===============================
# Wallet + Settlements
# ===============================
from app.api import wallets
from app.api import seller_settlement

# ===============================
# Logs + History
# ===============================
from app.api import activity_logs
from app.api import order_history

# ===============================
# Social
# ===============================
from app.api import favorites
from app.api import cart
from app.api import order_chat
from app.api import order_chat_ws
from app.api import notifications
from app.api import analytics

# =====================================================
# 🚀 FastAPI Init
# =====================================================
app = FastAPI(
    title="Recycling App API",
    version="Phase 12",
    description="Marketplace + Recycling + Delivery secured with JWT"
)

# =====================================================
# ✅ AUTH FIRST
# =====================================================
app.include_router(auth.router)

# =====================================================
# Core APIs
# =====================================================
app.include_router(cities.router)
app.include_router(addresses.router)
app.include_router(service_zones.router)
app.include_router(zone_check.router)
app.include_router(area_requests.router)

# =====================================================
# Marketplace + Recycling APIs
# =====================================================
app.include_router(categories.router)
app.include_router(products.router)
app.include_router(product_images.router)
app.include_router(recycling_hubs.router)

# =====================================================
# Orders Workflow APIs
# =====================================================
app.include_router(orders.router)
app.include_router(buyer_orders.router)
app.include_router(cancellation.router)
app.include_router(recycling_completion.router)

# =====================================================
# Delivery APIs
# =====================================================
app.include_router(delivery_actions.router)
app.include_router(delivery_dashboard.router)

# =====================================================
# Dashboards
# =====================================================
app.include_router(dashboard.router)
app.include_router(admin_dashboard.router)
app.include_router(admin_delivery_dashboard.router)

# =====================================================
# Wallet + Seller Settlements
# =====================================================
app.include_router(wallets.router)
app.include_router(seller_settlement.router)

# =====================================================
# Logs + Order History
# =====================================================
app.include_router(activity_logs.router)
app.include_router(order_history.router)

# =====================================================
# Favorites + Cart
# =====================================================
app.include_router(favorites.router)
app.include_router(cart.router)
app.include_router(order_chat.router)
app.include_router(order_chat_ws.router)
app.include_router(notifications.router)
app.include_router(analytics.router)

# =====================================================
# Root Endpoint
# =====================================================
@app.get("/")
def root():
    return {
        "status": "Backend running 🚀",
        "phase": "Phase 12 JWT Secured",
        "routers_loaded": True
    }

from fastapi.staticfiles import StaticFiles

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")
# ♻️ Recycling App - Comprehensive Project Overview

This document provides an exhaustive breakdown of the Recycling App, covering its purpose, domain model, functional modules, and data workflows.

---

## 1. Project Purpose & Problem Solved

### The Problem
Traditional waste management often lacks incentives for individuals to recycle, and the process of selling second-hand goods or properly disposing of recyclable materials (plastic, glass, paper) can be fragmented or inaccessible.

### The Solution
The **Recycling App** is a dual-purpose platform that combines a **Marketplace** with a **Recycling Logistics** system. It bridges the gap between:
- **Customers (Buyers/Sellers)**: Who want to buy/sell second-hand items.
- **Recycling Contributors**: Who want to dispose of waste in exchange for rewards.
- **Delivery Personnel**: Who manage the physical transport of goods.
- **Admins**: Who oversee quality control, pricing, and system integrity.

---

## 2. Domain Model (Key Actors & Entities)

### 👥 Key Actors
| Actor | Role |
| :--- | :--- |
| **Buyer** | Purchases marketplace items or requests recycling pickup. |
| **Seller** | Lists marketplace items and approves sales. |
| **Delivery** | Picks up items from sellers/buyers and delivers them to buyers/hubs. |
| **Admin** | Oversees delivery pricing, confirms recycling quality, and manages hubs. |

### 📄 Core Entities
- **User**: Base model for all participants, categorized by `role`.
- **Product**: Items listed for sale (Marketplace) or categories of waste (Recycling).
- **Order**: The central "State Machine" of the app, tracking a transaction from `pending` to `completed`.
- **Wallet**: Stores point balances and tracks financial history.
- **Recycling Hub**: Physical locations where recycling materials are consolidated.
- **Service Zone**: Geographic boundaries (Polygons) defining where the app operates.

---

## 3. Functional Modules Breakdown

### 🔐 Authentication & Security
- **JWT (Json Web Tokens)**: All API calls are secured using bearer tokens.
- **RBAC (Role-Based Access Control)**: Endpoints are protected by specialized decorators (`require_role`) to ensure, for example, only admins can price delivery.

### 🏪 Marketplace Module
- users can list products with images, categories, and locations.
- Supports "Sold" status to prevent double-selling.
- Integrated chat system for buyers and sellers to negotiate.

### ♻️ Recycling Module
- Users request a pickup for material categories (estimated quantity).
- Admins verify the **Actual Quantity** upon arrival at a hub.
- Rewards are calculated based on a configurable conversion rate (e.g., 10 points per 1 EGP value).

### 🚚 Logistics & Delivery Module
- **Distance Calculation**: Uses PostGIS geographic functions to calculate distance between buyer, seller, and available hubs.
- **State Workflow**: 
  1. `pending` → 2. `seller_approved` → 3. `delivery_priced` → 4. `assigned` → 5. `on_the_way` → 6. `collected` → 7. `delivered`.

### 💰 Wallet & Rewards Module
- **Dual Currency**: Supports both **Cash** (EGP) and **Points**.
- **Transactions**: Logs every "Earn" or "Spend" event to prevent balance discrepancies.

---

## 4. The Order Lifecycle (Deep Dive)

The app's complexity lies in its multi-step transition process:

1.  **Creation**: Buyer places an order (Marketplace or Recycling).
2.  **Seller Approval**: The seller (or system for recycling) confirms item availability.
3.  **Admin Pricing**: An admin reviews the delivery request and sets a `delivery_price`.
4.  **Buyer Acceptance**: The buyer sees the delivery price and chooses to `accept` or `cancel`.
5.  **Assignment**: A delivery person is assigned to the physical route.
6.  **Transit**: The order status updates as the items move (`collected`, `on_the_way`).
7.  **Final Confirmation**:
    - **Marketplace**: Buyer confirms receipt and records payment.
    - **Recycling**: Admin confirms weight/count and issues rewards.

---

## 5. Technical Stack Detail

- **Framework**: FastAPI (Asynchronous Python)
- **Database**: PostgreSQL with **PostGIS** extension (Required for coordinate-based logic).
- **ORM**: SQLAlchemy 2.0 (using the new `mapped_column` syntax).
- **Spatial Logic**: GeoAlchemy2 and Shapely for polygon/area checks.
- **Validation**: Pydantic v2 for robust data contract enforcement.
- **Infrastructure**: Dockerized database services for easy local deployment.

---

## 6. Summary of Recent Improvements
During the recent refactoring, we successfully:
- **Extracted a Service Layer**: Moving business logic out of `api/` into `services/` to prevent "Fat Controllers."
- **Centralized Logic**: Reward rates and file upload settings are now in a single `config.py`.
- **Standardized Error Handling**: Integrated `HTTPException` triggers across all services for consistent API responses.



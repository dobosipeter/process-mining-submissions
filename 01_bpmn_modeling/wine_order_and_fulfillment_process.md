# Wine Order and Fulfillment Process

## Motivation

I'm a second semester student, as such I don't have an in-progress thesis process to repurpose for this submission.
However, taking inspiration from my peronsal life, there is a winery business in my family which seemed like a suitable candidate to provide a process to model for this submission. The ordering and fulfillment process seemed like a practical choice to describe and model; as it is an instance of the **Order-to-Cash (O2C)** process, covering the full lifecycle from receiving a customer order through collecting payment.

## Participants

While in reality the roles overlap significantly (my family members can wear many hats), for modeling purposes we define the following clean separation of concerns:

| Participant | Role |
|---|---|
| **Customer** | External party who places and receives orders. Modeled as a separate pool. |
| **Sales Manager** | Receives orders, records them, communicates with customers, generates invoices. |
| **Warehouse Worker** | Checks stock and packaging material availability, transports wine from cellar if needed, procures packaging materials, packages orders. |
| **Delivery Driver** | Loads the delivery van and delivers orders, collects cash payment on delivery. |

The three winery roles (Sales Manager, Warehouse Worker, Delivery Driver) are modeled as lanes within a single **Winery** pool.

## Process Description

### 1. Order Receipt

The process starts when a customer places an order. Orders can arrive through several channels:
- Phone call
- Email
- Facebook message
- In person (at the winery or at a festival/event)

Regardless of the channel, the Sales Manager notices and records the order details (customer name, contact info, wines requested with quantities, delivery address).

### 2. Wine Stock Check

Once the order is recorded, the Warehouse Worker first checks whether all requested wine types and quantities are available:
- If **partially or fully unavailable at the winery but available at the wine cellar**: the missing wine must be transported from the cellar to the winery before proceeding.
- If a wine type is **completely out of stock** (neither at the winery nor at the cellar): the process moves to customer notification (described in section 3). Only once stock availability is confirmed does the process continue.

The wine stock check is performed *before* the parallel split so that the out-of-stock exception path (which may lead to order modification or cancellation) is fully resolved before any downstream work begins.

### 2b. Parallel: Packaging Check and Invoice Generation

Once wine availability is confirmed, two tasks proceed **in parallel**:

**a) Packaging material check and order packaging:**
- The Warehouse Worker checks whether sufficient packaging materials (boxes, padding, etc.) are available.
- If **insufficient**: additional materials must be procured (purchased from a local store or ordered online).
- Once materials are available, the Warehouse Worker packages the order: places the requested wines in the appropriate box and closes it.

**b) Invoice generation:**
- The Sales Manager manually generates and prints the invoice for the order.

Both branches must complete before the process can proceed. The printed invoice is included with the package.

### 3. Out-of-Stock Handling

If any requested wine type is completely unavailable:
- The Sales Manager informs the customer about the unavailability.
- The customer can either:
  - **Modify the order** (substitute wines, adjust quantities) — the process loops back to the order recording step with the updated order details.
  - **Cancel the order** — the process ends.

### 4. Delivery Readiness

Once both the packaging branch and the invoice generation branch complete (as described in section 2b), the order is ready for delivery.

### 5. Delivery Batching

Packaged orders are not delivered immediately. Instead, they are held until a delivery run is justified:
- A delivery run is triggered when **either**:
  - A single order for a delivery zone is large enough to justify the trip on its own (e.g., 6+ bottles or high-value order), **or**
  - Multiple smaller orders for the same delivery zone have accumulated (e.g., 3+ orders for the same area).
- Until a delivery run is triggered, the packaged order waits.

### 6. Loading and Delivery

Once a delivery batch is ready:
- The Delivery Driver loads all orders for that delivery run into the delivery van.
- The Delivery Driver delivers the orders to the respective customers.

### 7. Payment Collection

Payment can occur in different ways:
- **Cash on delivery** (most common): The Delivery Driver collects cash payment from the customer upon delivery.
- **Electronic payment** (bank transfer): The customer may pay electronically at any time up until delivery.

To handle both payment methods robustly, the Sales Manager's payment status check runs **in parallel** with the Delivery Driver's loading and delivery:
- **Branch A (Sales Manager):** The Sales Manager checks whether electronic payment has been received. This check may take time, as it involves verifying bank statements or payment confirmations.
- **Branch B (Delivery Driver):** The Delivery Driver loads the delivery van and delivers the orders to the customers.

Both branches must complete before proceeding. Once the delivery is done and the payment status is known, a decision is made:
- If electronic payment **has been received**: no further action is needed.
- If electronic payment **has not been received**: the Delivery Driver collects cash payment from the customer as a fallback.

This parallel structure ensures that the payment check covers the entire window up to (and including) the delivery itself, avoiding a race condition where a payment arriving after a pre-departure check but before delivery would be missed.

After payment is collected (or confirmed as already received), the order is considered fulfilled and the process ends.

## Summary of Key BPMN Elements

| BPMN Element | Usage in This Process |
|---|---|
| **Pools** | Customer (external), Winery (internal) |
| **Lanes** | Sales Manager, Warehouse Worker, Delivery Driver |
| **Start Event** | Order received |
| **End Events** | Order fulfilled, Order cancelled |
| **Parallel Gateway** | Packaging material check and invoice generation run concurrently (after wine stock confirmed); payment status check runs concurrently with loading and delivery |
| **Exclusive Gateways** | Stock availability decisions, customer modify/cancel decision, payment method, delivery batch threshold |
| **Loop** | Customer modifies order → returns to order recording |
| **Intermediate Event** | Waiting for delivery batch to accumulate |
| **Message Flow** | Communication between Customer pool and Winery pool |
| **Internal Communication** | Payment status determination synchronized with delivery completion |

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

### 2. Stock Availability Check

Once the order is recorded, two checks are performed in parallel by the Warehouse Worker:

**a) Wine stock check:**
- The Warehouse Worker checks whether all requested wine types and quantities are available at the winery.
- If **partially or fully unavailable at the winery but available at the wine cellar**: the missing wine must be transported from the cellar to the winery before proceeding. This is an additional task that must complete before packaging can begin.
- If a wine type is **completely out of stock** (neither at the winery nor at the cellar): the process moves to customer notification (described in section 3).

**b) Packaging material check:**
- The Warehouse Worker checks whether sufficient packaging materials (boxes, padding, etc.) are available.
- If **insufficient**: additional materials must be procured (purchased from a local store or ordered online). This must complete before packaging can begin.

Both checks (and any resulting restocking tasks) must complete before the process can proceed to packaging.

### 3. Out-of-Stock Handling

If any requested wine type is completely unavailable:
- The Sales Manager informs the customer about the unavailability.
- The customer can either:
  - **Modify the order** (substitute wines, adjust quantities) — the process loops back to the order recording step with the updated order details.
  - **Cancel the order** — the process ends.

### 4. Order Packaging

Once all wine and packaging materials are available:
- The Warehouse Worker packages the order: places the requested wines in the appropriate box and closes it.
- The Sales Manager manually generates and prints the invoice for the order.
- The invoice is included with the package.

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
- **Electronic payment** (bank transfer): The customer may pay electronically at any time up until delivery. Before the Delivery Driver departs, the Sales Manager checks whether electronic payment has been received and communicates the payment status to the Delivery Driver. If the payment has already arrived, no collection is needed at delivery. Otherwise, the Delivery Driver collects cash payment upon delivery as a fallback.

After payment is collected (or confirmed as already received), the order is considered fulfilled and the process ends.

## Summary of Key BPMN Elements

| BPMN Element | Usage in This Process |
|---|---|
| **Pools** | Customer (external), Winery (internal) |
| **Lanes** | Sales Manager, Warehouse Worker, Delivery Driver |
| **Start Event** | Order received |
| **End Events** | Order fulfilled, Order cancelled |
| **Parallel Gateway** | Wine stock check and packaging material check run concurrently |
| **Exclusive Gateways** | Stock availability decisions, customer modify/cancel decision, payment method, delivery batch threshold |
| **Loop** | Customer modifies order → returns to order recording |
| **Intermediate Event** | Waiting for delivery batch to accumulate |
| **Message Flow** | Communication between Customer pool and Winery pool |
| **Internal Communication** | Sales Manager confirms payment status to Delivery Driver before departure |

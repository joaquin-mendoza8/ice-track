# FROZEN ASSETS : AN ICE CREAM SHIPPING COMPANY

A complete solution to manage orders, shipping, inventory, and customer issues for your ice cream business. 

# Table of Content
1. Overview
2. Features
3. Quickstart/Installation
4. Usage
5. Tools for Development
6. Tools/Libs for General Requirements

# 1. Overview

## 1.1 Introduction

Frozen Assets is designed to streamline operations for ice cream businesses that need a robust system to sell ice cream. This software aims to automate key processes
by providing the following subsystems.
- Order Entry : Simplifies and automate the order-taking process.
- Inventory Management : Tracks inventory levels and updates in real time.
- Shipment Tracking : Monitors shipment status and handles logistics.
- Trouble Ticket Management : Manages customer and internal issues.

## 1.2 Client Requirements
These are features that the client have requested and have been fulfilled by us. These are the requirements the client has requested
https://github.com/joaquin-mendoza8/ice-track/blob/main/docs/ice-track.pdf


# 2. Features

## 2.1 General Features
- GUI : Intuitive window-based interface with response times under 5 seconds for transactions.
- Role Privileges/Security Access : Role-based access with password protection and detailed user logs.
- Error Handling : Validation of inputs, process blocking, modification consistency checks, restoration of previous data.
- Online Help Function : Context-sensitive help with detailed field descriptions.

## 2.2 Subsystem Features

This software has 4 subsystems that are integrated to provide a robust system with many features that our client has requested. A more detailed
explanation on how to navigate the subsystems will be in chapter 4.

### 2.2.1 Order Entry 
- Maintains customer data, including status(preferred, ok, shaky).
- Supports multi-line order forms with detailed product and shipping information.
- Automatically checks inventory availability and reserves stock.
- Allow user to enter the date payments were recieved.
- Generates printable invoices and reports on outstanding payments.

### 2.2.2 Inventory Management
- Tracks stock by flavor, package size, price, and availability.
- Allow users to manage stock with add/delete features.
- Manages committed inventory to unfulfilled orders.
- Manages planned and actual inventory schedules.
- Logs inventory history with user accountability.
- Generates reports on inventory status and product disposition.

### 2.2.3 Shipment Tracking
- Monitors shipments, including status, dates, and delivery method.
- Maintains a list of shipping vendors with ratings and costs.
- Handles canceled shipments and billing for partialed shipments.
- Handles lost or damaged shipments and supports reshipments.
- Generates shipment reports and logs.

### 2.2.4 Trouble Ticket Management
- Records and categorizes customer and internal issues.
- Supports automated problem reports from other subsystems.
- Allow users to input information to the ttms.
- Generates detailed reports on problem resolution times and trends.
- Exporets data for further analysis.


# 3. Quickstart Installation

- Clone the repo onto your machine
  ```
  git clone https://github.com/joaquin-mendoza8/ice-track.git
  ```

- Enter the project folder
  ```
  cd ice-track
  ```
- Create & activate a virtual environment for dependencies
  ```
  python -m venv venv && source venv/bin/activate
  ```
- Install dependencies in virtual env
  ```
  ./scripts/deps.sh
  ```
- Create the environment variables (fill in missing variables)
  ```
  cp .env.template .env
  ```
- Run the Flask application
  ```
  python run.py
  ```


# 4. Usage

This section will provide a guide to use this software for our clients and their users.


## 4.1 Registration.

### 4.1.1 Admin
- Create a user ID and password and set your user role to admin to access special privileges.

### 4.1.2 Customer 
- Create a user ID and password and provide your personal information to be able to start your order and transaction.


## 4.2 Order Entry
- Navigate to the **Orders** section using the blue tab on the top right.
  
### 4.2.1 Admin
- Navigate to the **Admin Dashboard** section using the blue tab on the top right.
- Set the customer's status (preferred, ok, shaky)
- Access the **Orders** section to manage customer orders

### 4.2.2 Customer
- Access the order entry form by pressing the **+New** button next to Orders.
- Choose your method of preferred shipping.
- Choose the products you want to purchase by setting your preferred flavor, size, and quantity.
- Press the **+** button below to add more products you want to purchase.


## 4.3 Inventory
- Navigate to the **Inventory** section.

### 4.3.1 Admin
- To add item into inventory use the **+New** button next to Products.
- Set the flavor, size, price, quantity, and inventory status.
- To manually adjust products in inventory, click on the product you want to adjust listed on the page and press **Save Changes**.
- To delete a product, you can click on the product listed and press the red "Delete" button and press **Save Changes**.

### 4.3.2 Customer
- Navigate to the **Inventory** section.
- This is where you will see an up-to-date on stock levels of our ice cream inventory.


## 4.4 Shipment Tracking
- Navigate to the shipments tab in the top right.

### 4.4.1 Admin
- Use the 
### 4.4.2 Customer

## 4.5 Trouble Ticket Managemnt
### 4.5.1 Admin
### 4.5.2 Customer
  

# 5. Tools for Development

- **_Back-end_** - Flask
  
- **_Front-end_** - Vue.js, HTML/CSS, Bootstrap
  
- **_Data_** - mySQL, PostGREs

- **_DevOps_** - Git, Docker, K8s?, GitHub Actions

- **_Project Management_** - Asana, GitHub



# 6. Tools/Libs for General Requirements

- **_GUI_** - Vue.js, Bootstrap

- **_Operational Env_** - Gunicorn, Heroku (PostGREs)

- **_Security Access_** - Flask-Login (or JWT)

- **_Roles and Privileges_** - Flask-Login, Flask-Session
  
- **_Auto Timeout Logoff_** - Flask-Login, Flask-Session
  
- **_Single Entry of Information_** - Central DB config
  
- **_Validation of Inputs_** - Flask-WTF, Bootstrap
  
- **_Entry and Processing of Names_** - Flask-WTF, SQLAlchemy (`ilike`)
  
- **_Modular Design_** - FS Organization, Flask-Blueprints, microservices arch (comm over HTTP)
  
- **_Data Structure_** - SQLAlchemy
  
- **_Display Printing_** - `@media print` CSS block, `window.print()` JS func, Flask-WeasyPrint
  
- **_Reporting Requirements_** - Same above ^
  
- **_Online Help Function_** - JSON file -> Jinja2, Tooltips
  
- **_Screens/User Interface_** - HTML, Jinja
  
- **_Ability to Access Any Screen_** - Central menu nav
  
- **_Prototype Design / Process_** - Confluence?
  
- **_Control of Info Entry Sequence_** - Flask-WTF
  
- **_Error Message_** - Bootstrap, JS
  
- **_Processing Block Until Error Corrected_** - Flask-WTF
  
- **_Control Entry Modification_** - Flask-Session
  
- **_Modification Consistency Checks_** - Flask endpoint logic
  
- **_User Cancellation of Action Before Completion_** - Same above ^
  
- **_Restoration of Previous Data_** - Flask-WTF, Flask-Session

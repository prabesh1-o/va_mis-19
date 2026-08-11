# Changelog

All notable changes to this VAMIS project are documented in this file.

---

## [19.0.1.0.0] - 2026-08-02

### Added
- Migrated VAMIS from Odoo 16 to Odoo 19.
- Added compatibility with Odoo 19 framework.
- Introduced new privilege management model to replace deprecated group category implementation.
- Updated security rules and access control for Odoo 19.
- Added support for Odoo 19 menu and view architecture.

### Changed
- Migrated all custom modules to Odoo 19.
- Updated XML views to comply with Odoo 17+ syntax.
- Removed deprecated `attrs` and `states` attributes from views.
- Updated manifest files to Odoo 19 format.
- Updated Python code to support Odoo 19 APIs.
- Updated menu hierarchy and action definitions.
- Improved attendance module compatibility with Odoo 19.
- Updated sales, inventory, CRM, accounting, installation, renewal, complaint, device, SIM, vehicle, and biometric modules.

### Fixed
- Fixed compatibility issues caused by removed models in Odoo 19.
- Fixed security and access-right inconsistencies.
- Fixed XML validation errors during module installation.
- Fixed deprecated field references.
- Fixed menu loading and action issues.
- Fixed module installation and upgrade errors.
- Fixed attendance-related issues after migration.
- Fixed various migration-related bugs and code cleanup.

---

## [1.2.1] - 2024-12-22

### Changed
- Arrange menu items by category.
- Change flow of call campaign.
- Add filter for today's absentees in Employee module.
- Make Salesperson and Tags editable in Sales Order.
- Add Device History in SIM.
- Link SIM and Device during installation from stock.
- Distinguish Installation Orders from Warranty and Sales Orders.

---

## [1.2.0] - 2024-10-28

### Fixed
- Issue while creating invoices for renewals with the same service but different prices.
- Invoice state not updated to **Fully Invoiced** for cancelled installations.
- Restriction on installing devices without inventory validation.

### Added
- Proper renewal log notes.
- Installation Price in Device List View.
- Requirement Collection module.
- Ability to view all associated customers of a device.
- Sales Order disposition.
- Independent Terms & Conditions for Sales Orders.

---

## [1.1.0] - 2024-10-28

### Added
- Customer Reference ID in Customer form.
- Industry field in Customer.
- Call Generation, Call Campaign and Call Assignment.
- WhatsApp integration.
- Blacklist Request moved to Action menu.

---

## [1.0.0] - 2023-12-17

### Added
- Customer & Employee Module
- Device Module
- SIM Module
- Complaint (Ticketing) Module
- Product Module
- Inventory Module
- Call Module
- Service Module
- Vehicle & Driver Module
- Accounting Module
- Biometric / Web Attendance Module
- Installation & Renewal Module
- Device Warranty Module
- Sales Module
- Invoice Module
- CRM Module
- Purchase Module
- Time Off Module

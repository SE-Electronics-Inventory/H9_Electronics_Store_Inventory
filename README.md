# Electronics Store Inventory Management System

A web-based **Electronics Store Inventory Management System** developed using **Python and Django**.
The system is designed to help electronics stores maintain component records, monitor stock levels, check availability, and generate inventory reports.

### Team

- Shriya S R [PES1UG24CS449]
- Simret M Kotian [PES1UG24CS456]
- Ahana S S [PES1UG24CS910]
- Swara Potdar [PES1UG24CS487]

## Phase 1

Phase 1 focuses on **requirements, architecture & design, test planning, and validation specifications**.

### Project Objectives

- Maintain electronic component inventory records
- Add, update, view, and delete/deactivate components
- Search and filter inventory
- Track stock quantities and availability
- Identify low-stock components
- Provide an inventory dashboard
- Generate inventory reports
- Implement authentication and role-based authorization
- Validate user input and handle errors
- Maintain persistent inventory data

The system is intended to provide a centralized, role-controlled and testable approach to inventory management.

## User Roles

| Role | Responsibilities |
|------|------------------|
| **Inventory Administrator** | Manages inventory, users/roles, and permitted inventory operations |
| **Store Staff** | Views inventory, checks availability, and performs permitted operations |
| **Store Manager** | Monitors dashboard, stock levels, availability, and reports |
| **QA / Evaluator** | Validates the system against requirements and acceptance criteria |

The first three roles are operational users, while QA / Evaluator is an external evaluation role.

## Technology Stack

- **Backend:** Python, Django
- **ORM:** Django ORM
- **Database:** SQLite for development; PostgreSQL/MySQL supported for larger deployment
- **Frontend:** HTML, CSS, JavaScript
- **Development Tools:** VS Code, Git
- **Client:** Modern web browsers such as Chrome, Edge, and Firefox

## Core Features

- User authentication and logout
- Role-based authorization
- Component CRUD operations
- Inventory search and filtering
- Availability calculation
- Low-stock identification
- Dashboard with inventory indicators
- Inventory report generation
- Input validation
- Persistent database storage
- Inventory change tracking
- Error handling

## Phase 1 Documentation

The Phase 1 deliverables are organized as follows:

| Document | Description |
|----------|-------------|
| `01_COMPLETE_SRS_IEEE_STYLE.pdf` | Software Requirements Specification |
| `02_COMPLETE_IEEE_TEST_PLAN.pdf` | Test Plan and acceptance strategy |
| `03_COMPLETE_TEST_CASES_15.pdf` | Functional, non-functional, and security test cases |
| `04_COMPLETE_ARCHITECTURE_AND_DESIGN.pdf` | System architecture, UML use cases, and design specifications |

The documents use common requirement, design, and test references such as **ESIM-F-xxx**, **ESIM-NF-xxx**, **ESIM-SR-xxx**, **DS-xx**, and **TC-xx** for traceability.

## Testing

Phase 1 defines functional, non-functional, and security validation.

Key areas include:

- Authentication and session management
- Inventory CRUD operations
- Search and filtering
- Availability and low-stock detection
- Dashboard and reports
- Input validation and error handling
- Authorization
- Performance and scalability
- Browser compatibility
- Database recoverability
- Security and access-control testing

The planned performance criteria include **90% of normal-load inventory requests completing within 2 seconds** and support for at least **1000 component records** in the test database.

### Security Testing

Planned security validation covers:

- Authentication bypass
- Authorization and privilege escalation
- Password/secret exposure
- CSRF protection
- Malicious or invalid input
- Session management
- Access control for inventory-changing operations


---

## Current Submission Index

Start with [docs/README.md](docs/README.md) for revised specifications, the three
formal reports, exact execution evidence, videos and outstanding closure actions.

- [Unit Test Report](docs/01_Unit_Test_Report.md)
- [System Test Report](docs/02_System_Test_Report.md)
- [Code and Branch Coverage Report](docs/03_Code_and_Branch_Coverage_Report.md)
- [Sprint 1](Phase_2/Sprint_1_Demo.mp4)
- [Sprint 2](Phase_2/Sprint_2_Demo.mp4)

Recorded automated baseline: 158 tests passed; 89% statement, 78% branch and 88%
combined coverage. Manual acceptance status is qualified in the system report.

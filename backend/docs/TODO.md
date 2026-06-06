# School ERP System – TODO & Future Enhancements

## ✅ Completed (Core Modules)
- [x] Database schema (28 tables) with UUIDs, soft deletes
- [x] Core models (Student, Staff, Department, Class, Stream, Subject, AcademicYear, Term)
- [x] Custom User model with roles (bursar, admin, principal, teacher, parent)
- [x] JWT authentication, password reset
- [x] Finance API: invoices, payments, overpayments, credits, expenses, reconciliation logs
- [x] M‑Pesa STK Push, callback, PDF receipt with QR code, email receipt logic
- [x] Expense approval workflow
- [x] Role‑based permissions
- [x] Partial payments, payment allocations, duplicate prevention

## ✅ Completed (Payroll)
- [x] Salary structures (CRUD, auto gross, date validation, no negatives)
- [x] Payroll runs (create, process, pay, duplicate prevention)
- [x] Statutory deductions (PAYE, NHIF, NSSF, SHIF, Housing Levy)
- [x] Payroll entries generation and net pay calculation
- [x] Payment logs (for M-Pesa B2C / bank transfer)
- [x] PDF payslips with QR code
- [x] Teacher‑specific endpoints (list own payslips, download PDF)
- [x] Permissions (bursar/admin manage, teacher view own)

## 🚧 Pending / Missing Business Workflows (Finance)
- [ ] Overdue invoice detection (automatic status change)
- [ ] Payment reversal endpoint
- [ ] Audit logging for finance actions (auto-create AuditLog records)
- [ ] Reporting endpoints: student statement, outstanding balances, expense summary, payment collection report

## 🟡 Test & Production Readiness
- [ ] Test M‑Pesa callback end‑to‑end with sandbox test number
- [ ] Configure production email provider (SendGrid / Resend) and test real email delivery
- [ ] Verify all finance permissions

## 🟢 Future Modules (New Apps) – Priority Order

### 1. Payroll API (models exist)
- [ ] Salary structures, payroll runs, deduction calculations
- [ ] M‑Pesa B2C / bank disbursement

### 2. Budget API (models exist)
- [ ] Budget periods, line items, variance reporting

### 3. Integration (LMS)
- [ ] API endpoints for lost book events, clearance status

### 4. Reporting & Audit
- [ ] Aggregated financial reports
- [ ] Full audit log automation

### 5. Exams & Grading (new app `apps.exams`)
- [ ] Exam setup, marks entry, grade calculation, report cards, class rankings, transcripts

### 6. Parent Portal (new app `apps.parent_portal` or frontend)
- [ ] View results, fee balances, attendance, download report cards, receive announcements

### 7. Timetable (new app `apps.timetable`)
- [ ] Manual timetable creation (Phase 1)
- [ ] Automatic generation with Google OR‑Tools (Phase 2)
- [ ] Room allocation, teacher allocation, period management, conflict detection

### 8. E‑Learning / LMS (new app `apps.lms`)
- [ ] Courses, lessons, assignments, quizzes, learning materials, student progress

### 9. Notifications (new app `apps.notifications`)
- [ ] SMS, email, in‑app announcements

### 10. Other possible modules (attendance, transport, hostel, inventory, discipline)
- [ ] Each as a separate app when needed

## 🔑 API Keys & Credentials (never commit!)
- M‑Pesa: Consumer Key, Secret, Passkey, Shortcodes → `.env`
- Email: SendGrid API key or SMTP → `.env`
- Database: PostgreSQL credentials → `.env`
- JWT secret → `settings.py` (keep secret)
- Future: LMS API keys (via `APIKey` model)

## 📌 Branch Strategy for Future Features
Each new module gets its own branch from `develop`:
- `feature/payroll-api`
- `feature/budget-api`
- `feature/exams-models`, `feature/exams-api`
- `feature/timetable-models`, `feature/timetable-api`
- `feature/parent-portal`
- `feature/lms-models`, `feature/lms-api`
- `feature/notifications`

## 📌 Immediate Next Steps
1. Decide whether to tackle missing finance workflows (overdue, reversal, audit, reports) or move directly to Payroll API.
2. If moving to Payroll, I will provide the complete implementation plan and code.
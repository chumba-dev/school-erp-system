# School ERP System – TODO & Future Enhancements

## ✅ Completed (Finance Module – Core Business Workflows)
- [x] Database schema (28 tables) with UUIDs, soft deletes
- [x] Core models (Student, Staff, Department, Class, Stream, Subject, AcademicYear, Term)
- [x] Custom User model with role (bursar, admin, principal, teacher, parent)
- [x] JWT authentication (login, register, profile, token refresh)
- [x] Password reset (request + confirm) – console email works
- [x] Finance API: invoices, payments, overpayments, credits, expenses, reconciliation logs
- [x] M‑Pesa STK Push initiation, callback handling, status check
- [x] PDF receipt generation with QR code (ReportLab)
- [x] Email receipt logic (ready for production provider)
- [x] Overpayment → StudentCredit auto‑creation
- [x] Credit auto‑application on new invoices
- [x] Expense approval workflow (pending → approved → paid)
- [x] Role‑based permissions (bursar, admin, parent, teacher)
- [x] Partial payments and payment allocations
- [x] Duplicate transaction prevention (unique constraint)

## 🚧 Pending / Missing Business Workflows (Finance)
- [ ] **Overdue invoice detection** – automatic status change based on `due_date` (cron or background task)
- [ ] **Payment reversal process** – endpoint to reverse a payment and adjust invoice/credit
- [ ] **Audit logging for finance actions** – automatic creation of `AuditLog` records for invoice/payment/expense changes
- [ ] **Reporting endpoints**:
  - [ ] Student statement (full ledger)
  - [ ] Outstanding balances report (all students)
  - [ ] Expense summary by category/period
  - [ ] Payment collection report

## 🟡 Test & Production Readiness
- [ ] **Test M‑Pesa callback end‑to‑end** with sandbox test number (254708374149)
- [ ] **Configure production email provider** (SendGrid / Resend) and test real email delivery
- [ ] **Add missing `ReconciliationLog` API endpoints** if not fully exposed (models exist)
- [ ] **Verify all finance permissions** – parents see only own invoices/payments/credits

## 🟢 Optional / Future Enhancements
- [ ] **Payroll API** – models exist; implement serializers, views, endpoints for salary structures, payroll runs, deduction calculations, M‑Pesa B2C/bank disbursement
- [ ] **Budget API** – models exist; implement endpoints for budget periods, line items, variance reporting
- [ ] **Frontend (React + Tailwind)** – parent portal, bursar dashboard, admin panel
- [ ] **LMS Integration** – create API endpoints for LMS to push lost book events and check clearance (models `APIKey`, `LostBookEvent` exist)
- [ ] **M‑Pesa B2C / B2B** for payroll and expense payments (separate from STK Push)
- [ ] **Airtel Money / TKash support** (extend payment methods)
- [ ] **Automated bank statement reconciliation** (API/webhook)
- [ ] **Multi‑school support** – add `School` model and tenant isolation (deferred)
- [ ] **Upgrade QR code data to URL** pointing to online receipt

## 🔑 API Keys & Credentials (never commit!)
- **M‑Pesa**: Consumer Key, Consumer Secret, Passkey, Shortcodes (sandbox/production). Stored in `.env`.
- **Email**: SendGrid API key or SMTP credentials (for production). Stored in `.env`.
- **Database**: PostgreSQL credentials.
- **JWT**: Secret key already in `settings.py` (keep secret).
- **Future**: LMS API keys (to be generated via `APIKey` model).

## 📌 Next Steps (immediate)
1. Decide which missing business workflow to tackle first (overdue detection, payment reversal, audit logging, reporting).
2. Or proceed to **Payroll API** / **Budget API** / **Frontend**.
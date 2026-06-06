# School ERP System – TODO & Future Enhancements

## ✅ Completed (Finance Module)
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
- [x] Expense approval workflow

## 🚧 Pending (Critical – do before next major feature)
- [ ] **Test M‑Pesa callback end‑to‑end** with sandbox test number (254708374149). Ensure automatic payment recording works.
- [ ] **Configure production email provider** (SendGrid / Resend) and test real email delivery. Currently using console backend.
- [ ] **Add missing `ReconciliationLog` API endpoints** if not fully exposed (models exist, double‑check views).
- [ ] **Verify all finance permissions** – parents see only own invoices/payments/credits.

## 🟡 Optional / Future Enhancements
- [ ] **Multi‑school support** – add `School` model and tenant isolation (deferred, not in original scope).
- [ ] **Payroll API** – models exist; implement serializers, views, endpoints for salary structures, payroll runs, deduction calculations, M‑Pesa B2C/bank disbursement.
- [ ] **Budget API** – models exist; implement endpoints for budget periods, line items, variance reporting.
- [ ] **Frontend (React + Tailwind)** – parent portal, bursar dashboard, admin panel.
- [ ] **LMS Integration** – create API endpoints for LMS to push lost book events and check clearance (models `APIKey`, `LostBookEvent` exist).
- [ ] **M‑Pesa B2C / B2B** for payroll and expense payments (separate from STK Push).
- [ ] **Airtel Money / TKash support** (extend payment methods).
- [ ] **Automated bank statement reconciliation** (API/webhook).
- [ ] **Receipt email as PDF attachment** – already implemented, but test in production.
- [ ] **QR code data upgrade to URL linking to online receipt** (instead of plain text).
- [ ] **Logging & monitoring** for callback failures.

## 🔑 API Keys & Credentials (never commit!)
- **M‑Pesa**: Consumer Key, Consumer Secret, Passkey, Shortcodes (sandbox/production). Stored in `.env`.
- **Email**: SendGrid API key or SMTP credentials (for production). Stored in `.env`.
- **Database**: PostgreSQL credentials.
- **JWT**: Secret key already in `settings.py` (keep secret).
- **Future**: LMS API keys (to be generated via `APIKey` model).

## 📌 Next Steps (immediate)
1. Test M‑Pesa callback end‑to‑end with sandbox.
2. Decide whether to keep email console or configure production provider.
3. Proceed to **Payroll API** or **Frontend**.
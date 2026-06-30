import { CreditCard, DollarSign, Clock, TrendingUp, AlertCircle, CheckCircle, Download, Plus, LogOut } from 'lucide-react';

interface ParentDashboardProps {
  onLogout?: () => void;
}

export default function ParentDashboard({ onLogout }: ParentDashboardProps) {
  const stats = [
    { label: 'Total Fees', value: 'KES 150,000', status: 'All Fees', icon: DollarSign, color: 'text-blue-400' },
    { label: 'Amount Paid', value: 'KES 120,000', status: 'Completed', icon: CheckCircle, color: 'text-green-400' },
    { label: 'Outstanding', value: 'KES 30,000', status: 'Pending', icon: AlertCircle, color: 'text-orange-400' },
    { label: 'Payment Methods', value: '13+', status: 'Available', icon: CreditCard, color: 'text-purple-400' },
  ];

  const pendingInvoices = [
    { id: 1, name: 'School Fees - Term 1', amount: 'KES 30,000', dueDate: '2024-07-15', status: 'Overdue' },
    { id: 2, name: 'Transport Fees', amount: 'KES 5,000', dueDate: '2024-08-01', status: 'Due Soon' },
  ];

  const paymentMethods = [
    { name: 'M-Pesa', icon: '📱', category: 'Mobile Money', available: true },
    { name: 'Airtel Money', icon: '📱', category: 'Mobile Money', available: true },
    { name: 'Equity Bank', icon: '🏦', category: 'Bank Transfer', available: true },
    { name: 'KCB Bank', icon: '🏦', category: 'Bank Transfer', available: true },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
      {/* Header */}
      <div className="sticky top-0 z-40 border-b border-white/10 bg-white/5 backdrop-blur-3xl shadow-2xl">
        <div className="px-6 py-5">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gradient">Pay School Fees</h1>
              <p className="text-sm text-gray-400 mt-1">Manage your child's fees and payments</p>
            </div>
            <div className="flex items-center gap-3">
              <button className="px-6 py-2 bg-gradient-to-r from-emerald-500 to-green-600 hover:from-emerald-600 hover:to-green-700 text-white font-semibold rounded-xl transition-all shadow-lg hover:shadow-xl">
                <Plus className="w-4 h-4 inline mr-2" />
                Make Payment
              </button>
              {onLogout && (
                <button 
                  onClick={onLogout}
                  className="px-4 py-2 bg-red-500/20 hover:bg-red-500/30 text-red-300 hover:text-red-200 font-semibold rounded-xl transition-all border border-red-400/30 hover:border-red-400/60 flex items-center gap-2"
                >
                  <LogOut className="w-4 h-4" />
                  Logout
                </button>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="p-6">
        <div className="max-w-6xl mx-auto">
          {/* Stats Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {stats.map((stat, idx) => {
              const Icon = stat.icon;
              return (
                <div key={idx} className="card-enhanced p-6 group hover-lift">
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <p className="text-gray-400 text-sm mb-1">{stat.label}</p>
                      <p className="text-2xl font-bold text-white">{stat.value}</p>
                    </div>
                    <Icon className={`w-8 h-8 ${stat.color} opacity-80 group-hover:opacity-100`} />
                  </div>
                  <p className="text-xs text-emerald-400">{stat.status}</p>
                </div>
              );
            })}
          </div>

          {/* Main Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Outstanding Invoices */}
            <div className="lg:col-span-2 card-enhanced p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold text-white flex items-center gap-2">
                  <AlertCircle className="w-5 h-5 text-orange-400" />
                  Outstanding Invoices
                </h2>
                <a href="#" className="text-sm text-emerald-400 hover:text-emerald-300">View All</a>
              </div>
              <div className="space-y-3">
                {pendingInvoices.map((invoice) => (
                  <div key={invoice.id} className="bg-white/5 hover:bg-white/10 p-4 rounded-lg border border-white/10 hover:border-emerald-400/30 transition-all">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-white font-medium">{invoice.name}</p>
                        <p className="text-sm text-gray-400">Due: {invoice.dueDate}</p>
                      </div>
                      <div className="text-right">
                        <p className="text-white font-bold">{invoice.amount}</p>
                        <span className={`text-xs px-2 py-1 rounded ${invoice.status === 'Overdue' ? 'bg-red-500/20 text-red-300' : 'bg-orange-500/20 text-orange-300'}`}>
                          {invoice.status}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Quick Actions */}
            <div className="card-enhanced p-6">
              <h3 className="text-lg font-bold text-white mb-6 flex items-center gap-2">
                <CreditCard className="w-5 h-5 text-emerald-400" />
                Quick Pay
              </h3>
              <div className="space-y-3">
                <button className="w-full btn-primary-enhanced text-sm">
                  <DollarSign className="w-4 h-4" />
                  Pay Now
                </button>
                <button className="w-full btn-secondary-enhanced text-sm">
                  <Download className="w-4 h-4" />
                  Download Invoice
                </button>
                <button className="w-full btn-secondary-enhanced text-sm">
                  <TrendingUp className="w-4 h-4" />
                  Payment History
                </button>
              </div>
            </div>
          </div>

          {/* Payment Methods */}
          <div className="mt-8 card-enhanced p-6">
            <h2 className="text-xl font-bold text-white mb-6">Available Payment Methods</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {paymentMethods.map((method, idx) => (
                <button
                  key={idx}
                  className="group card-enhanced p-4 text-center hover-lift transition-all"
                >
                  <div className="text-4xl mb-3">{method.icon}</div>
                  <p className="font-semibold text-white mb-1">{method.name}</p>
                  <p className="text-xs text-gray-400">{method.category}</p>
                  {method.available && (
                    <div className="mt-3 text-emerald-400 text-xs font-medium">Available</div>
                  )}
                </button>
              ))}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

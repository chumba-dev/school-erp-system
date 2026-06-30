import { BarChart3, DollarSign, Users, AlertCircle, TrendingUp, Eye, Settings, Download, LogOut } from 'lucide-react';

interface AdminDashboardProps {
  onLogout?: () => void;
}

export default function AdminDashboard({ onLogout }: AdminDashboardProps) {
  const stats = [
    { label: 'Total Revenue', value: 'KES 2.4M', change: '+12.5%', icon: DollarSign, color: 'text-green-400' },
    { label: 'Active Students', value: '1,240', change: '+8.2%', icon: Users, color: 'text-blue-400' },
    { label: 'Pending Invoices', value: '48', change: '-3.1%', icon: AlertCircle, color: 'text-orange-400' },
    { label: 'Collected Today', value: 'KES 185K', change: '+5.7%', icon: TrendingUp, color: 'text-purple-400' },
  ];

  const recentTransactions = [
    { id: 1, student: 'John Doe', amount: 'KES 150,000', status: 'Completed', date: '2024-06-28' },
    { id: 2, student: 'Jane Smith', amount: 'KES 45,000', status: 'Pending', date: '2024-06-27' },
    { id: 3, student: 'Mark Johnson', amount: 'KES 280,000', status: 'Processing', date: '2024-06-26' },
  ];

  const adminActions = [
    { label: 'Create Invoices', icon: '📄', action: 'New Fee Invoice' },
    { label: 'View Reports', icon: '📊', action: 'Financial Reports' },
    { label: 'Manage Expenses', icon: '💰', action: 'Track Expenses' },
    { label: 'Payroll Setup', icon: '👥', action: 'Staff Salaries' },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
      {/* Header */}
      <div className="sticky top-0 z-40 border-b border-white/10 bg-white/5 backdrop-blur-3xl shadow-2xl">
        <div className="px-6 py-5">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gradient">Admin Dashboard</h1>
              <p className="text-sm text-gray-400 mt-1">Complete school finance overview</p>
            </div>
            <div className="flex items-center gap-3">
              <button className="px-6 py-2 bg-gradient-to-r from-emerald-500 to-green-600 hover:from-emerald-600 hover:to-green-700 text-white font-semibold rounded-xl transition-all shadow-lg hover:shadow-xl flex items-center gap-2">
                <Download className="w-4 h-4" />
                Export
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
        <div className="max-w-7xl mx-auto">
          {/* Stats Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {stats.map((stat, idx) => {
              const Icon = stat.icon;
              const isPositive = stat.change.includes('+');
              return (
                <div key={idx} className="card-enhanced p-6 group hover-lift">
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <p className="text-gray-400 text-sm mb-1">{stat.label}</p>
                      <p className="text-2xl font-bold text-white">{stat.value}</p>
                    </div>
                    <Icon className={`w-8 h-8 ${stat.color} opacity-80 group-hover:opacity-100`} />
                  </div>
                  <p className={`text-xs ${isPositive ? 'text-green-400' : 'text-red-400'}`}>
                    {stat.change}
                  </p>
                </div>
              );
            })}
          </div>

          {/* Main Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
            {/* Recent Transactions */}
            <div className="lg:col-span-2 card-enhanced p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold text-white">Recent Transactions</h2>
                <a href="#" className="text-sm text-emerald-400 hover:text-emerald-300">View All</a>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-white/10">
                      <th className="text-left py-3 px-4 text-gray-400 font-medium">Student</th>
                      <th className="text-right py-3 px-4 text-gray-400 font-medium">Amount</th>
                      <th className="text-center py-3 px-4 text-gray-400 font-medium">Status</th>
                      <th className="text-right py-3 px-4 text-gray-400 font-medium">Date</th>
                    </tr>
                  </thead>
                  <tbody>
                    {recentTransactions.map((tx) => (
                      <tr key={tx.id} className="border-b border-white/5 hover:bg-white/5 transition-colors">
                        <td className="py-3 px-4 text-white">{tx.student}</td>
                        <td className="py-3 px-4 text-right text-white font-semibold">{tx.amount}</td>
                        <td className="py-3 px-4 text-center">
                          <span className={`text-xs px-2 py-1 rounded ${
                            tx.status === 'Completed' ? 'bg-green-500/20 text-green-300' :
                            tx.status === 'Pending' ? 'bg-orange-500/20 text-orange-300' :
                            'bg-blue-500/20 text-blue-300'
                          }`}>
                            {tx.status}
                          </span>
                        </td>
                        <td className="py-3 px-4 text-right text-gray-400">{tx.date}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Quick Stats */}
            <div className="card-enhanced p-6">
              <h3 className="text-lg font-bold text-white mb-6">Quick Metrics</h3>
              <div className="space-y-4">
                <div className="bg-white/5 p-4 rounded-lg border border-white/10">
                  <p className="text-gray-400 text-sm mb-1">Collection Rate</p>
                  <p className="text-2xl font-bold text-emerald-400">92.4%</p>
                </div>
                <div className="bg-white/5 p-4 rounded-lg border border-white/10">
                  <p className="text-gray-400 text-sm mb-1">Outstanding Balance</p>
                  <p className="text-2xl font-bold text-orange-400">KES 180K</p>
                </div>
                <div className="bg-white/5 p-4 rounded-lg border border-white/10">
                  <p className="text-gray-400 text-sm mb-1">Monthly Expenses</p>
                  <p className="text-2xl font-bold text-blue-400">KES 980K</p>
                </div>
              </div>
            </div>
          </div>

          {/* Admin Actions */}
          <div className="card-enhanced p-6">
            <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
              <Settings className="w-5 h-5 text-emerald-400" />
              Administrative Actions
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {adminActions.map((action, idx) => (
                <button
                  key={idx}
                  className="group card-enhanced p-6 text-center hover-lift transition-all"
                >
                  <div className="text-5xl mb-4">{action.icon}</div>
                  <p className="font-semibold text-white mb-1">{action.label}</p>
                  <p className="text-xs text-emerald-400 group-hover:text-emerald-300">{action.action}</p>
                </button>
              ))}
            </div>
          </div>

          {/* System Health */}
          <div className="mt-8 grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="card-enhanced p-6">
              <h3 className="text-lg font-bold text-white mb-4">System Status</h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                  <span className="text-gray-300">Database</span>
                  <span className="text-emerald-400 text-sm">✓ Healthy</span>
                </div>
                <div className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                  <span className="text-gray-300">API Server</span>
                  <span className="text-emerald-400 text-sm">✓ Active</span>
                </div>
                <div className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                  <span className="text-gray-300">Payment Gateway</span>
                  <span className="text-emerald-400 text-sm">✓ Connected</span>
                </div>
              </div>
            </div>

            <div className="card-enhanced p-6">
              <h3 className="text-lg font-bold text-white mb-4">Alerts</h3>
              <div className="space-y-3">
                <div className="p-3 bg-orange-500/10 border border-orange-500/30 rounded-lg">
                  <p className="text-sm text-orange-300">⚠️ 5 invoices overdue by 30+ days</p>
                </div>
                <div className="p-3 bg-blue-500/10 border border-blue-500/30 rounded-lg">
                  <p className="text-sm text-blue-300">ℹ️ Payroll runs tomorrow at 3 PM</p>
                </div>
                <div className="p-3 bg-green-500/10 border border-green-500/30 rounded-lg">
                  <p className="text-sm text-green-300">✓ Monthly budget reviewed successfully</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

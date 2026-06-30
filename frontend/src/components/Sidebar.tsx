import { LayoutDashboard, Receipt, Wallet, Users, BarChart3, LogOut, Settings, Zap } from 'lucide-react';

const navigation = [
  { name: 'Dashboard', icon: LayoutDashboard, active: true },
  { name: 'Invoices', icon: Receipt, active: false },
  { name: 'Payments', icon: Wallet, active: false },
  { name: 'Payroll', icon: Users, active: false },
  { name: 'Reports', icon: BarChart3, active: false },
];

export default function Sidebar() {
  return (
    <div className="hidden md:flex md:w-64 md:flex-col md:fixed md:inset-y-0 bg-white/5 border-r border-white/15 shadow-2xl backdrop-blur-2xl">
      <div className="flex flex-col flex-grow overflow-y-auto">
        {/* Logo Section */}
        <div className="px-6 py-8 border-b border-white/20 bg-gradient-to-br from-white/10 to-white/5">
          <div className="flex items-center gap-3 group cursor-pointer">
            <div className="w-11 h-11 bg-gradient-to-br from-emerald-400 to-green-600 rounded-lg flex items-center justify-center shadow-xl group-hover:shadow-2xl group-hover:shadow-emerald-500/50 transition-all group-hover:scale-110">
              <span className="text-white font-bold text-lg">K</span>
            </div>
            <div className="flex-1">
              <p className="text-white font-bold text-sm">Kitondo</p>
              <p className="text-emerald-300 text-xs font-bold tracking-wide">FINANCE</p>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-3 py-8 space-y-2">
          {navigation.map((item) => (
            <a
              key={item.name}
              href="#"
              className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-300 group relative ${
                item.active
                  ? 'bg-gradient-to-r from-emerald-500/30 to-emerald-500/10 text-emerald-300 font-semibold border-l-4 border-emerald-400 shadow-lg shadow-emerald-500/20'
                  : 'text-gray-400 hover:bg-white/10 hover:text-gray-200 hover:border-l-4 hover:border-transparent'
              }`}
            >
              {item.active && (
                <div className="absolute right-0 top-1/2 -translate-y-1/2 w-1 h-8 bg-gradient-to-b from-emerald-400 to-emerald-500 rounded-l-full shadow-lg shadow-emerald-500/50"></div>
              )}
              <item.icon className={`w-5 h-5 transition-transform group-hover:scale-110 ${item.active ? 'text-emerald-300' : ''}`} />
              <span className="text-sm font-medium">{item.name}</span>
              {item.active && (
                <div className="ml-auto">
                  <Zap className="w-4 h-4 text-emerald-300" />
                </div>
              )}
            </a>
          ))}
        </nav>

        {/* Footer */}
        <div className="px-3 py-6 border-t border-white/20 bg-gradient-to-br from-white/10 to-white/5 space-y-2">
          <button className="w-full flex items-center gap-3 px-4 py-3 text-gray-400 hover:bg-white/10 rounded-lg transition-all duration-300 text-sm font-medium group hover:text-gray-200">
            <Settings className="w-5 h-5 group-hover:rotate-90 transition-transform duration-300" />
            Settings
          </button>
          <button className="w-full flex items-center gap-3 px-4 py-3 text-gray-400 hover:bg-red-500/20 rounded-lg transition-all duration-300 text-sm font-medium group hover:text-red-300 hover:border-l-4 hover:border-red-400">
            <LogOut className="w-5 h-5 group-hover:translate-x-1 transition-transform duration-200" />
            Logout
          </button>
        </div>
      </div>
    </div>
  );
}
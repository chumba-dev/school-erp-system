import { BookOpen, Users, TrendingUp, BarChart3, Eye, Download, Clock, Award, LogOut } from 'lucide-react';

interface TeacherDashboardProps {
  onLogout?: () => void;
}

export default function TeacherDashboard({ onLogout }: TeacherDashboardProps) {
  const stats = [
    { label: 'Classes Assigned', value: '4', category: 'Form 2-4', icon: BookOpen, color: 'text-blue-400' },
    { label: 'Total Students', value: '156', category: 'All Classes', icon: Users, color: 'text-green-400' },
    { label: 'Payment Rate', value: '92%', category: 'On Time', icon: TrendingUp, color: 'text-emerald-400' },
    { label: 'Reports Generated', value: '12', category: 'This Term', icon: BarChart3, color: 'text-purple-400' },
  ];

  const classData = [
    { name: 'Form 2A', students: 35, collected: 31, percentage: 88, outstanding: 'KES 150K' },
    { name: 'Form 3B', students: 38, collected: 36, percentage: 95, outstanding: 'KES 75K' },
    { name: 'Form 4C', students: 42, collected: 38, percentage: 90, outstanding: 'KES 200K' },
    { name: 'Form 4D', students: 41, collected: 39, percentage: 95, outstanding: 'KES 100K' },
  ];

  const viewTypes = [
    { title: 'Collection Overview', description: 'View fee collection status', icon: '📊' },
    { title: 'Student Payments', description: 'Track individual payments', icon: '💳' },
    { title: 'Class Reports', description: 'Detailed class analytics', icon: '📋' },
    { title: 'Financial Summary', description: 'Overall financial health', icon: '📈' },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
      {/* Header */}
      <div className="sticky top-0 z-40 border-b border-white/10 bg-white/5 backdrop-blur-3xl shadow-2xl">
        <div className="px-6 py-5">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gradient">Financial Reports</h1>
              <p className="text-sm text-gray-400 mt-1">Class and student financial overview</p>
            </div>
            <div className="flex items-center gap-3">
              <button className="px-6 py-2 bg-gradient-to-r from-emerald-500 to-green-600 hover:from-emerald-600 hover:to-green-700 text-white font-semibold rounded-xl transition-all shadow-lg hover:shadow-xl flex items-center gap-2">
                <Download className="w-4 h-4" />
                Export Report
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
              return (
                <div key={idx} className="card-enhanced p-6 group hover-lift">
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <p className="text-gray-400 text-sm mb-1">{stat.label}</p>
                      <p className="text-2xl font-bold text-white">{stat.value}</p>
                    </div>
                    <Icon className={`w-8 h-8 ${stat.color} opacity-80 group-hover:opacity-100`} />
                  </div>
                  <p className="text-xs text-emerald-400">{stat.category}</p>
                </div>
              );
            })}
          </div>

          {/* Class Performance */}
          <div className="card-enhanced p-6 mb-8">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-white flex items-center gap-2">
                <BarChart3 className="w-5 h-5 text-emerald-400" />
                Class Fee Collection
              </h2>
              <a href="#" className="text-sm text-emerald-400 hover:text-emerald-300">View Details</a>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-white/10">
                    <th className="text-left py-3 px-4 text-gray-400 font-medium">Class</th>
                    <th className="text-center py-3 px-4 text-gray-400 font-medium">Total</th>
                    <th className="text-center py-3 px-4 text-gray-400 font-medium">Collected</th>
                    <th className="text-center py-3 px-4 text-gray-400 font-medium">Collection %</th>
                    <th className="text-right py-3 px-4 text-gray-400 font-medium">Outstanding</th>
                  </tr>
                </thead>
                <tbody>
                  {classData.map((classItem, idx) => (
                    <tr key={idx} className="border-b border-white/5 hover:bg-white/5 transition-colors">
                      <td className="py-4 px-4">
                        <div className="flex items-center gap-3">
                          <Award className="w-5 h-5 text-emerald-400" />
                          <span className="font-semibold text-white">{classItem.name}</span>
                        </div>
                      </td>
                      <td className="py-4 px-4 text-center text-white">{classItem.students}</td>
                      <td className="py-4 px-4 text-center text-emerald-400 font-semibold">{classItem.collected}</td>
                      <td className="py-4 px-4 text-center">
                        <div className="flex items-center justify-center gap-2">
                          <div className="w-20 h-2 bg-white/10 rounded-full overflow-hidden">
                            <div className="h-full bg-gradient-to-r from-emerald-500 to-green-500" style={{ width: `${classItem.percentage}%` }}></div>
                          </div>
                          <span className="text-white font-semibold text-sm">{classItem.percentage}%</span>
                        </div>
                      </td>
                      <td className="py-4 px-4 text-right text-orange-400 font-semibold">{classItem.outstanding}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* View Reports Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {viewTypes.map((view, idx) => (
              <button
                key={idx}
                className="group card-enhanced p-6 text-left hover-lift transition-all"
              >
                <div className="text-5xl mb-4">{view.icon}</div>
                <h3 className="font-semibold text-white mb-2">{view.title}</h3>
                <p className="text-sm text-gray-400">{view.description}</p>
                <div className="mt-4 text-emerald-400 text-sm font-medium group-hover:translate-x-1 transition-transform">
                  View Report →
                </div>
              </button>
            ))}
          </div>

          {/* Summary Cards */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Total Enrollment */}
            <div className="card-enhanced p-6">
              <h3 className="text-lg font-bold text-white mb-4">Total Enrollment</h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                  <span className="text-gray-300">Active Students</span>
                  <span className="text-emerald-400 font-bold">156</span>
                </div>
                <div className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                  <span className="text-gray-300">New This Term</span>
                  <span className="text-blue-400 font-bold">12</span>
                </div>
                <div className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                  <span className="text-gray-300">Fee Defaulters</span>
                  <span className="text-orange-400 font-bold">8</span>
                </div>
              </div>
            </div>

            {/* Fee Collection Health */}
            <div className="card-enhanced p-6">
              <h3 className="text-lg font-bold text-white mb-4">Collection Health</h3>
              <div className="space-y-4">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-gray-300 text-sm">On Time</span>
                    <span className="text-emerald-400 font-bold">92%</span>
                  </div>
                  <div className="w-full h-2 bg-white/10 rounded-full overflow-hidden">
                    <div className="h-full bg-emerald-500" style={{ width: '92%' }}></div>
                  </div>
                </div>
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-gray-300 text-sm">Late</span>
                    <span className="text-orange-400 font-bold">5%</span>
                  </div>
                  <div className="w-full h-2 bg-white/10 rounded-full overflow-hidden">
                    <div className="h-full bg-orange-500" style={{ width: '5%' }}></div>
                  </div>
                </div>
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-gray-300 text-sm">Defaulted</span>
                    <span className="text-red-400 font-bold">3%</span>
                  </div>
                  <div className="w-full h-2 bg-white/10 rounded-full overflow-hidden">
                    <div className="h-full bg-red-500" style={{ width: '3%' }}></div>
                  </div>
                </div>
              </div>
            </div>

            {/* Quick Notes */}
            <div className="card-enhanced p-6">
              <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                <Clock className="w-5 h-5 text-emerald-400" />
                Important Dates
              </h3>
              <div className="space-y-3">
                <div className="p-3 bg-white/5 rounded-lg border border-white/10">
                  <p className="text-xs text-gray-400">Fee Deadline</p>
                  <p className="text-white font-semibold">July 30, 2024</p>
                </div>
                <div className="p-3 bg-white/5 rounded-lg border border-white/10">
                  <p className="text-xs text-gray-400">Next Review</p>
                  <p className="text-white font-semibold">August 15, 2024</p>
                </div>
                <div className="p-3 bg-white/5 rounded-lg border border-white/10">
                  <p className="text-xs text-gray-400">Term Ends</p>
                  <p className="text-white font-semibold">September 30, 2024</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

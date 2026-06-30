import { useState } from 'react';
import { Mail, Lock, Eye, EyeOff, ArrowRight, Zap, User, Users, GraduationCap } from 'lucide-react';

type UserType = 'parent' | 'admin' | 'teacher' | null;

interface AuthProps {
  onLogin?: (userType: UserType) => void;
}

export default function Auth({ onLogin }: AuthProps) {
  const [userType, setUserType] = useState<UserType>(null);
  const [showPassword, setShowPassword] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const userTypeOptions = [
    {
      type: 'parent' as UserType,
      label: 'Parent',
      icon: User,
      description: 'Pay fees & track payments',
      color: 'from-blue-500 to-blue-600',
      bgColor: 'bg-blue-50',
    },
    {
      type: 'admin' as UserType,
      label: 'Admin',
      icon: Users,
      description: 'Manage school finance',
      color: 'from-purple-500 to-purple-600',
      bgColor: 'bg-purple-50',
    },
    {
      type: 'teacher' as UserType,
      label: 'Teacher',
      icon: GraduationCap,
      description: 'COMING SOON',
      color: 'from-orange-500 to-orange-600',
      bgColor: 'bg-orange-50',
    },
  ];

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    
    // Simulate login delay
    setTimeout(() => {
      console.log(`Login as ${userType}:`, { email, password });
      setIsLoading(false);
      
      // Call the onLogin callback with the selected user type
      if (onLogin) {
        onLogin(userType);
      }
    }, 1500);
  };

  const handleBackToSelection = () => {
    setUserType(null);
    setEmail('');
    setPassword('');
  };

  const selectedOption = userTypeOptions.find(opt => opt.type === userType);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 relative overflow-hidden flex items-center justify-center p-4">
      {/* Animated Background Elements */}
      <div className="absolute top-0 left-0 w-96 h-96 bg-emerald-500/10 rounded-full blur-3xl -translate-x-1/2 -translate-y-1/2"></div>
      <div className="absolute bottom-0 right-0 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl translate-x-1/2 translate-y-1/2"></div>
      <div className="absolute top-1/2 right-1/4 w-64 h-64 bg-purple-500/5 rounded-full blur-3xl"></div>

      {/* Main Container */}
      <div className="relative z-10 w-full max-w-md">
        {/* Header */}
        <div className="mb-12 text-center">
          <div className="flex items-center justify-center mb-6">
            <div className="w-16 h-16 bg-gradient-to-br from-emerald-400 to-green-600 rounded-2xl flex items-center justify-center shadow-2xl shadow-emerald-500/50 hover:scale-110 transition-transform">
              <span className="text-white font-bold text-2xl">K</span>
            </div>
          </div>
          <h1 className="text-4xl font-bold bg-gradient-to-r from-emerald-300 via-cyan-300 to-blue-300 bg-clip-text text-transparent mb-2">
            Kitondo Finance
          </h1>
          <p className="text-gray-400 text-sm">School Finance Management System</p>
        </div>

        {!userType ? (
          <>
            {/* User Type Selection */}
            <div className="mb-8 text-center">
              <h2 className="text-2xl font-bold text-white mb-2">Select Your Role</h2>
              <p className="text-gray-400 text-sm">Choose how you access the system</p>
            </div>

            <div className="space-y-4 mb-8">
              {userTypeOptions.map((option) => {
                const Icon = option.icon;
                return (
                  <button
                    key={option.type}
                    onClick={() => setUserType(option.type)}
                    className="w-full group card-enhanced p-6 text-left transition-all duration-300 hover:border-emerald-400/60 hover:shadow-emerald-500/30 relative overflow-hidden"
                  >
                    {/* Background glow on hover */}
                    <div className={`absolute inset-0 bg-gradient-to-r ${option.color} opacity-0 group-hover:opacity-5 transition-opacity duration-300`}></div>
                    
                    <div className="relative z-10 flex items-center justify-between">
                      <div className="flex items-center gap-4">
                        <div className={`w-12 h-12 ${option.bgColor} rounded-lg flex items-center justify-center`}>
                          <Icon className={`w-6 h-6 text-${option.type === 'parent' ? 'blue' : option.type === 'admin' ? 'purple' : 'orange'}-600`} />
                        </div>
                        <div>
                          <p className="text-white font-semibold">{option.label}</p>
                          <p className="text-gray-400 text-sm">{option.description}</p>
                        </div>
                      </div>
                      <ArrowRight className="w-5 h-5 text-emerald-400 group-hover:translate-x-2 transition-transform" />
                    </div>
                  </button>
                );
              })}
            </div>

            {/* Features Grid */}
            <div className="grid grid-cols-3 gap-3 mb-8">
              <div className="card-enhanced p-4 text-center group">
                <Zap className="w-6 h-6 text-emerald-400 mx-auto mb-2 group-hover:animate-pulse" />
                <p className="text-xs text-gray-400">Fast</p>
              </div>
              <div className="card-enhanced p-4 text-center group">
                <Lock className="w-6 h-6 text-emerald-400 mx-auto mb-2 group-hover:animate-pulse" />
                <p className="text-xs text-gray-400">Secure</p>
              </div>
              <div className="card-enhanced p-4 text-center group">
                <Users className="w-6 h-6 text-emerald-400 mx-auto mb-2 group-hover:animate-pulse" />
                <p className="text-xs text-gray-400">Trusted</p>
              </div>
            </div>
          </>
        ) : (
          <>
            {/* Login Form */}
            <div className="mb-8 text-center">
              <div className={`w-12 h-12 ${selectedOption?.bgColor} rounded-lg flex items-center justify-center mx-auto mb-4`}>
                {selectedOption && <selectedOption.icon className={`w-6 h-6 text-${selectedOption.type === 'parent' ? 'blue' : selectedOption.type === 'admin' ? 'purple' : 'orange'}-600`} />}
              </div>
              <h2 className="text-2xl font-bold text-white mb-1">{selectedOption?.label} Login</h2>
              <p className="text-gray-400 text-sm">{selectedOption?.description}</p>
            </div>

            <form onSubmit={handleLogin} className="space-y-6 mb-8">
              {/* Email Field */}
              <div className="group">
                <label className="block text-sm font-medium text-gray-300 mb-2">Email Address</label>
                <div className="relative">
                  <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-emerald-400/60 group-focus-within:text-emerald-400 transition-colors" />
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="your.email@example.com"
                    className="w-full pl-12 pr-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-emerald-400/50 focus:ring-1 focus:ring-emerald-400/30 transition-all"
                    required
                  />
                </div>
              </div>

              {/* Password Field */}
              <div className="group">
                <div className="flex items-center justify-between mb-2">
                  <label className="text-sm font-medium text-gray-300">Password</label>
                  <a href="#" className="text-xs text-emerald-400 hover:text-emerald-300 transition-colors">Forgot?</a>
                </div>
                <div className="relative">
                  <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-emerald-400/60 group-focus-within:text-emerald-400 transition-colors" />
                  <input
                    type={showPassword ? 'text' : 'password'}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••"
                    className="w-full pl-12 pr-12 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-emerald-400/50 focus:ring-1 focus:ring-emerald-400/30 transition-all"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-emerald-400 transition-colors"
                  >
                    {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                  </button>
                </div>
              </div>

              {/* Remember Me */}
              <label className="flex items-center gap-3 cursor-pointer">
                <input type="checkbox" className="w-4 h-4 rounded bg-white/10 border border-white/20 accent-emerald-400" />
                <span className="text-sm text-gray-400">Remember me</span>
              </label>

              {/* Login Button */}
              <button
                type="submit"
                disabled={isLoading}
                className="w-full py-3 bg-gradient-to-r from-emerald-500 to-green-600 hover:from-emerald-600 hover:to-green-700 text-white font-bold rounded-lg transition-all duration-300 shadow-lg hover:shadow-xl hover:shadow-emerald-500/50 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {isLoading ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                    Logging in...
                  </>
                ) : (
                  <>
                    Sign In
                    <ArrowRight className="w-4 h-4" />
                  </>
                )}
              </button>
            </form>

            {/* Divider */}
            <div className="relative mb-8">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-white/10"></div>
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-gray-400">or</span>
              </div>
            </div>

            {/* Back Button */}
            <button
              onClick={handleBackToSelection}
              className="w-full py-3 bg-white/5 hover:bg-white/10 text-white font-medium rounded-lg border border-white/20 hover:border-white/30 transition-all"
            >
              Change Role
            </button>

            {/* Support Text */}
            <p className="text-center text-xs text-gray-500 mt-8">
              Need help? <a href="#" className="text-emerald-400 hover:text-emerald-300">Contact Support</a>
            </p>
          </>
        )}

        {/* Footer */}
        <div className="mt-12 pt-8 border-t border-white/10 text-center text-xs text-gray-500">
          <p>© 2026 Kitindo Finance. All rights reserved.</p>
        </div>
      </div>
    </div>
  );
}

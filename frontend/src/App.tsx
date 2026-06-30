import { useState } from 'react';
import Auth from './pages/Auth';
import ParentDashboard from './pages/ParentDashboard';
import AdminDashboard from './pages/AdminDashboard';
import TeacherDashboard from './pages/TeacherDashboard';

type UserRole = 'parent' | 'admin' | 'teacher' | null;

function App() {
  const [userRole, setUserRole] = useState<UserRole>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Callback for Auth component to set user role after successful login
  const handleLogin = (role: UserRole) => {
    setUserRole(role);
    setIsAuthenticated(true);
  };

  // Callback to logout
  const handleLogout = () => {
    setIsAuthenticated(false);
    setUserRole(null);
  };

  // Show Auth page if not authenticated
  if (!isAuthenticated) {
    return <Auth onLogin={handleLogin} />;
  }

  // Route to role-specific dashboard with logout handler
  if (userRole === 'parent') {
    return <ParentDashboard onLogout={handleLogout} />;
  }
  if (userRole === 'teacher') {
    return <TeacherDashboard onLogout={handleLogout} />;
  }

  // Return default admin dashboard
  return <AdminDashboard onLogout={handleLogout} />;
}

export default App;
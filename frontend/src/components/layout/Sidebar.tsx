import { useState } from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard, Users, UserCircle, CalendarCheck, StickyNote,
  Activity, BarChart3, GitBranch, Settings, ChevronLeft, ChevronRight,
  LogOut, Building2,
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';

const navItems = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/leads', label: 'Leads', icon: Users },
  { to: '/customers', label: 'Customers', icon: Building2 },
  { to: '/followups', label: 'Follow Ups', icon: CalendarCheck },
  { to: '/lead-notes', label: 'Lead Notes', icon: StickyNote },
  { to: '/activity-logs', label: 'Activity Logs', icon: Activity },
  { to: '/reports', label: 'Reports', icon: BarChart3 },
  { to: '/lead-sources', label: 'Lead Sources', icon: GitBranch },
  { to: '/profile', label: 'Profile', icon: UserCircle },
];

export function Sidebar({ collapsed, onToggle }: { collapsed: boolean; onToggle: () => void }) {
  const { user, logout } = useAuth();

  return (
    <aside className={`fixed top-0 left-0 h-full bg-white border-r border-gray-200 z-40 transition-all duration-300 flex flex-col ${collapsed ? 'w-16' : 'w-60'}`}>
      <div className="flex items-center h-16 px-4 border-b border-gray-100">
        <div className="flex items-center gap-2.5 min-w-0">
          <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center flex-shrink-0">
            <span className="text-white font-bold text-sm">S</span>
          </div>
          {!collapsed && <span className="font-semibold text-gray-900 truncate">CRM TRacker</span>}
        </div>
      </div>

      <nav className="flex-1 overflow-y-auto py-3 px-2 space-y-0.5">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-blue-50 text-blue-700'
                  : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
              }`
            }
          >
            <item.icon size={20} className="flex-shrink-0" />
            {!collapsed && <span className="truncate">{item.label}</span>}
          </NavLink>
        ))}
      </nav>

      <div className="border-t border-gray-100 p-3">
        {!collapsed && user && (
          <div className="px-3 py-2 mb-1">
            <p className="text-sm font-medium text-gray-900 truncate">{user.first_name} {user.last_name}</p>
            <p className="text-xs text-gray-500 truncate">{user.role.replace(/_/g, ' ')}</p>
          </div>
        )}
        <button
          onClick={logout}
          className="flex items-center gap-3 w-full px-3 py-2.5 rounded-xl text-sm font-medium text-gray-600 hover:bg-gray-100 hover:text-red-600 transition-colors"
        >
          <LogOut size={20} />
          {!collapsed && <span>Logout</span>}
        </button>
        <button
          onClick={onToggle}
          className="flex items-center justify-center w-full mt-1 px-3 py-2 rounded-xl text-gray-400 hover:bg-gray-100 hover:text-gray-600 transition-colors"
        >
          {collapsed ? <ChevronRight size={18} /> : <ChevronLeft size={18} />}
        </button>
      </div>
    </aside>
  );
}

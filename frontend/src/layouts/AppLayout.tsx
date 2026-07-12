import { useState } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import { Sidebar } from '../components/layout/Sidebar';
import { Topbar } from '../components/layout/Topbar';

const titles: Record<string, string> = {
  '/dashboard': 'Dashboard',
  '/leads': 'Leads',
  '/customers': 'Customers',
  '/followups': 'Follow Ups',
  '/lead-notes': 'Lead Notes',
  '/activity-logs': 'Activity Logs',
  '/reports': 'Reports',
  '/lead-sources': 'Lead Sources',
  '/profile': 'Profile',
  '/settings': 'Settings',
};

export function AppLayout() {
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const location = useLocation();
  const basePath = '/' + location.pathname.split('/')[1];
  const title = titles[basePath] || 'CRM';

  return (
    <div className="min-h-screen bg-[#F8FAFC]">
      <Sidebar collapsed={collapsed} onToggle={() => setCollapsed(!collapsed)} />
      <div className={`transition-all duration-300 ${collapsed ? 'ml-16' : 'ml-60'}`}>
        <Topbar title={title} onMenuToggle={() => setMobileOpen(!mobileOpen)} />
        <main className="p-4 lg:p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

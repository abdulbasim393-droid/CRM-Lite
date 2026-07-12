import { Search, Bell, Menu, UserCircle } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { Badge } from '../ui/Badge';

interface TopbarProps {
  title: string;
  onMenuToggle: () => void;
}

export function Topbar({ title, onMenuToggle }: TopbarProps) {
  const { user } = useAuth();

  return (
    <header className="sticky top-0 z-30 h-16 bg-white/80 backdrop-blur-md border-b border-gray-200">
      <div className="flex items-center justify-between h-full px-4 lg:px-6">
        <div className="flex items-center gap-3">
          <button onClick={onMenuToggle} className="lg:hidden p-2 text-gray-500 hover:bg-gray-100 rounded-lg">
            <Menu size={20} />
          </button>
          <h1 className="text-lg font-semibold text-gray-900">{title}</h1>
        </div>

        <div className="flex items-center gap-3">
          <div className="hidden sm:flex items-center gap-2 bg-gray-100 rounded-xl px-3.5 py-2 text-sm text-gray-400">
            <Search size={16} />
            <input type="text" placeholder="Search..." className="bg-transparent border-none outline-none text-gray-700 placeholder-gray-400 w-40 lg:w-60" />
          </div>

          <button className="relative p-2 text-gray-500 hover:bg-gray-100 rounded-lg">
            <Bell size={20} />
            <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full" />
          </button>

          {user && (
            <div className="flex items-center gap-2 pl-2 border-l border-gray-200">
              <UserCircle size={32} className="text-gray-400" />
              <div className="hidden sm:block">
                <p className="text-sm font-medium text-gray-900 leading-tight">{user.first_name} {user.last_name}</p>
                <Badge variant={
                  user.role === 'ADMIN' ? 'danger' : user.role === 'SALES_MANAGER' ? 'warning' : 'info'
                }>
                  {user.role.replace(/_/g, ' ')}
                </Badge>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}

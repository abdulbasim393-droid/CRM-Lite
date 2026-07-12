import { Card, CardBody, CardHeader } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { useAuth } from '../contexts/AuthContext';
import { User, Mail, Calendar, Shield } from 'lucide-react';

export function ProfilePage() {
  const { user } = useAuth();

  if (!user) return null;

  return (
    <div className="max-w-2xl mx-auto">
      <Card>
        <CardHeader>
          <h2 className="text-lg font-semibold text-gray-900">Profile</h2>
        </CardHeader>
        <CardBody>
          <div className="text-center pb-6 border-b border-gray-100 mb-6">
            <div className="w-20 h-20 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center text-3xl font-bold mx-auto mb-3">
              {user.first_name[0]}{user.last_name[0]}
            </div>
            <h3 className="text-xl font-semibold text-gray-900">{user.first_name} {user.last_name}</h3>
            <div className="mt-2">
              <Badge variant={user.role === 'ADMIN' ? 'danger' : user.role === 'SALES_MANAGER' ? 'warning' : 'info'}>
                {user.role.replace(/_/g, ' ')}
              </Badge>
            </div>
          </div>

          <div className="space-y-4">
            <div className="flex items-center gap-4 p-4 bg-gray-50 rounded-xl">
              <Mail size={20} className="text-gray-400" />
              <div><p className="text-sm text-gray-500">Email</p><p className="font-medium text-gray-900">{user.email}</p></div>
            </div>
            <div className="flex items-center gap-4 p-4 bg-gray-50 rounded-xl">
              <User size={20} className="text-gray-400" />
              <div><p className="text-sm text-gray-500">Full Name</p><p className="font-medium text-gray-900">{user.first_name} {user.last_name}</p></div>
            </div>
            <div className="flex items-center gap-4 p-4 bg-gray-50 rounded-xl">
              <Shield size={20} className="text-gray-400" />
              <div><p className="text-sm text-gray-500">Role</p><p className="font-medium text-gray-900">{user.role.replace(/_/g, ' ')}</p></div>
            </div>
            <div className="flex items-center gap-4 p-4 bg-gray-50 rounded-xl">
              <Calendar size={20} className="text-gray-400" />
              <div><p className="text-sm text-gray-500">Member Since</p><p className="font-medium text-gray-900">{new Date(user.created_at).toLocaleDateString()}</p></div>
            </div>
          </div>
        </CardBody>
      </Card>
    </div>
  );
}

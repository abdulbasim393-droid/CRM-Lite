import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { AppLayout } from './layouts/AppLayout';
import { LoginPage } from './pages/LoginPage';
import { DashboardPage } from './pages/DashboardPage';
import { LeadsPage } from './pages/LeadsPage';
import { LeadDetailPage } from './pages/LeadDetailPage';
import { CustomersPage } from './pages/CustomersPage';
import { FollowUpsPage } from './pages/FollowUpsPage';
import { LeadNotesPage } from './pages/LeadNotesPage';
import { ActivityLogsPage } from './pages/ActivityLogsPage';
import { ReportsPage } from './pages/ReportsPage';
import { LeadSourcesPage } from './pages/LeadSourcesPage';
import { ProfilePage } from './pages/ProfilePage';
import { LoadingSpinner } from './components/ui/LoadingSpinner';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();
  if (loading) return <LoadingSpinner />;
  return user ? <>{children}</> : <Navigate to="/login" replace />;
}

function PublicRoute({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();
  if (loading) return <LoadingSpinner />;
  return user ? <Navigate to="/dashboard" replace /> : <>{children}</>;
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<PublicRoute><LoginPage /></PublicRoute>} />
      <Route
        element={
          <ProtectedRoute>
            <AppLayout />
          </ProtectedRoute>
        }
      >
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/leads" element={<LeadsPage />} />
        <Route path="/leads/:id" element={<LeadDetailPage />} />
        <Route path="/customers" element={<CustomersPage />} />
        <Route path="/followups" element={<FollowUpsPage />} />
        <Route path="/lead-notes" element={<LeadNotesPage />} />
        <Route path="/activity-logs" element={<ActivityLogsPage />} />
        <Route path="/reports" element={<ReportsPage />} />
        <Route path="/lead-sources" element={<LeadSourcesPage />} />
        <Route path="/profile" element={<ProfilePage />} />
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
      </Route>
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  );
}

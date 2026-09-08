import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

interface ProtectedRouteProps {
  /** If provided, user's role must be in this list */
  allowedRoles?: string[];
}

export default function ProtectedRoute({ allowedRoles }: ProtectedRouteProps) {
  const { user } = useAuth();

  // Not authenticated → go to login
  if (!user) {
    return <Navigate to="/login" replace />;
  }

  // Authenticated but wrong role → back to chat (graceful degradation)
  if (allowedRoles && !allowedRoles.includes(user.role)) {
    return <Navigate to="/chat" replace />;
  }

  return <Outlet />;
}

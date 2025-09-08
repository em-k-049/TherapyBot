import React from 'react';
import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import LandingPage from './components/LandingPage';
import Dashboard from './components/Dashboard';
import PatientChat from './components/PatientChat';
import ConsultantDashboard from './components/ConsultantDashboard';
import AdminPanel from './components/AdminPanel';

const router = createBrowserRouter([
  { path: "/", element: <LandingPage /> },
  { path: "/dashboard", element: <Dashboard /> },
  { path: "/chat", element: <PatientChat /> },
  { path: "/consultant", element: <ConsultantDashboard /> },
  { path: "/admin", element: <AdminPanel /> }
], {
  future: {
    v7_startTransition: true,
    v7_relativeSplatPath: true,
  }
});

function App() {
  return <RouterProvider router={router} />;
}

export default App;
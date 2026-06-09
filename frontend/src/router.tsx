import { createBrowserRouter, Navigate } from 'react-router-dom'
import PrivateRoute from './components/PrivateRoute'
import AppLayout from './components/AppLayout'
import Login from './pages/Login'
import AppList from './pages/AppList'
import TestCases from './pages/TestCases'
import DefectList from './pages/Defects'
import DefectDetail from './pages/Defects/DefectDetail'
import TestTaskList from './pages/TestTasks'
import TestTaskDetail from './pages/TestTasks/TestTaskDetail'

export const router = createBrowserRouter([
  { path: '/login', element: <Login /> },
  {
    path: '/',
    element: <PrivateRoute />,
    children: [
      { index: true, element: <Navigate to="/apps" replace /> },
      { path: 'apps', element: <AppList /> },
      {
        path: 'apps/:appId',
        element: <AppLayout />,
        children: [
          { index: true, element: <Navigate to="defects" replace /> },
          { path: 'test-cases', element: <TestCases /> },
          { path: 'defects', element: <DefectList /> },
          { path: 'defects/:defectId', element: <DefectDetail /> },
          { path: 'test-tasks', element: <TestTaskList /> },
          { path: 'test-tasks/:taskId', element: <TestTaskDetail /> },
        ],
      },
    ],
  },
])

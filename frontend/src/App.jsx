import { BrowserRouter, Routes, Route, Outlet } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import ProtectedRoute from "./components/ProtectedRoute";

import LoginPage from "./pages/LoginPage";
import HomePage from "./pages/HomePage";
import TasksPage from "./pages/TasksPage";
import ProjectsPage from "./pages/ProjectsPage";
import CalendarPage from "./pages/CalendarPage";
import KnowledgePage from "./pages/KnowledgePage";
import NotificationsPage from "./pages/NotificationsPage";

import "./css/App.css";

// Khung có Sidebar, chỉ dùng cho các trang sau khi đăng nhập
function AppLayout() {
  return (
    <div className="app">
      <Sidebar />
      <main className="main">
        <Outlet />
      </main>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Không Sidebar */}
        <Route path="/login" element={<LoginPage />} />

        {/* Phải đăng nhập mới vào được */}
        {/* <Route element={<ProtectedRoute />}> */}
          <Route element={<AppLayout />}>
            <Route path="/" element={<HomePage />} />
            <Route path="/home" element={<HomePage />} />
            <Route path="/tasks" element={<TasksPage />} />
            <Route path="/projects" element={<ProjectsPage />} />
            <Route path="/calendar" element={<CalendarPage />} />
            <Route path="/knowledge" element={<KnowledgePage />} />
            <Route path="/notifications" element={<NotificationsPage />} />
          {/* </Route> */}
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
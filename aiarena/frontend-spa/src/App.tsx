import { Route, Routes } from "react-router";
import NotImplemented from "@/NotImplemented.tsx";
import Layout from "@/Layout.tsx";
import Profile from "./_pages/Profile";

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />} path="spa-frontend">
        <Route index element={<NotImplemented />} />
        <Route path="competitions" element={<NotImplemented />} />
        <Route path="about" element={<NotImplemented />} />
        <Route path="status" element={<NotImplemented />} />
        <Route path="profile" element={<Profile />} />
      </Route>
    </Routes>
  );
}

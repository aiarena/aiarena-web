import { Route, Routes } from "react-router";
import NotImplemented from "@/NotImplemented.tsx";
import Layout from "@/Layout.tsx";
import User from "./_pages/User";
import UserBots from "./_pages/UserBots";
import MatchRequests from "./_pages/MatchRequests";
import Dashboard from "./_pages/Dashboard";
import { getFeatureFlags } from "./_data/featureFlags";
import Examples from "./_pages/Examples";
import PageNotFound from "./_pages/PageNotFound";

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />} path="dashboard">
        <Route index element={<Dashboard />} />
        <Route path="competitions" element={<NotImplemented />} />
        <Route path="about" element={<NotImplemented />} />
        <Route path="status" element={<NotImplemented />} />
        <Route path="userbots" element={<UserBots />} />
        <Route path="matchrequests" element={<MatchRequests />} />
        <Route path="user" element={<User />} />
        {getFeatureFlags().examples && (
          <Route path="examples" element={<Examples />} />
        )}
        <Route path="*" element={<PageNotFound />} />
      </Route>
    </Routes>
  );
}

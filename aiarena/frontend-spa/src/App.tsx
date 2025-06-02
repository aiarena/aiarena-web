import { Route, Routes } from "react-router";
import NotImplemented from "@/NotImplemented.tsx";
import Layout from "@/Layout.tsx";
import UserRoot from "./_pages/UserRoot";
import { getFeatureFlags } from "./_data/featureFlags";
import Examples from "./_pages/Examples";
import PageNotFound from "./_pages/PageNotFound";

import UserMatchRequestsPage from "./_pages/UserMatchRequests/UserMatchRequestsPage";
import UserBotsPage from "./_pages/UserBots/UserBotsPage";
import UserSettingsPage from "./_pages/UserSettings/UserSettingsPage";

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />} path="dashboard">
        <Route index element={<UserRoot />} />
        <Route path="competitions" element={<NotImplemented />} />
        <Route path="about" element={<NotImplemented />} />
        <Route path="status" element={<NotImplemented />} />
        <Route path="bots" element={<UserBotsPage />} />
        <Route path="match-requests" element={<UserMatchRequestsPage />} />
        <Route path="profile" element={<UserSettingsPage />} />
        {getFeatureFlags().examples && (
          <Route path="examples" element={<Examples />} />
        )}
        <Route path="*" element={<PageNotFound />} />
      </Route>
    </Routes>
  );
}

import { Route, Routes } from "react-router";
import NotImplemented from "@/NotImplemented.tsx";
import Layout from "@/Layout.tsx";
import UserSettings from "./_pages/UserSettings";
import UserBots from "./_pages/UserBots";
import MatchRequests from "./_pages/UserMatchRequests";
import UserRoot from "./_pages/UserRoot";
import { getFeatureFlags } from "./_data/featureFlags";
import Examples from "./_pages/Examples";
import PageNotFound from "./_pages/PageNotFound";

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />} path="dashboard">
        <Route index element={<UserRoot />} />
        <Route path="competitions" element={<NotImplemented />} />
        <Route path="about" element={<NotImplemented />} />
        <Route path="status" element={<NotImplemented />} />
        <Route path="userbots" element={<UserBots />} />
        <Route path="matchrequests" element={<MatchRequests />} />
        <Route path="user" element={<UserSettings />} />
        {getFeatureFlags().examples && (
          <Route path="examples" element={<Examples />} />
        )}
        <Route path="*" element={<PageNotFound />} />
      </Route>
    </Routes>
  );
}

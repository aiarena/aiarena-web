import { Route, Routes } from "react-router";
import DashboardLayout from "@/DashboardLayout";
import UserRoot from "./_pages/UserRoot";
import { getFeatureFlags } from "./_data/featureFlags";
import Examples from "./_pages/Examples";
import PageNotFound from "./_pages/PageNotFound";

import UserMatchRequestsPage from "./_pages/UserMatchRequests/UserMatchRequestsPage";
import UserBotsPage from "./_pages/UserBots/UserBotsPage";
import UserSettingsPage from "./_pages/UserSettings/UserSettingsPage";
import AuthorsPage from "./_pages/Rework/Authors/Page";
import BotsPage from "./_pages/Rework/Bots/Page";
import CompetitionsPage from "./_pages/Rework/Competitions/Page";
import RootLayout from "./RootLayout";
import ResultsPage from "./_pages/Rework/Results/Page";

export default function App() {
  return (
    <Routes>
      <Route element={<RootLayout />} path="dashboard/rework">
        <Route path="competitions" element={<CompetitionsPage />} />
        <Route path="bots" element={<BotsPage />} />
        <Route path="authors" element={<AuthorsPage />} />
        <Route path="results" element={<ResultsPage />} />
      </Route>

      <Route element={<DashboardLayout />} path="dashboard">
        <Route index element={<UserRoot />} />
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

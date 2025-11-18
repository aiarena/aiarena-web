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
import RootLayout from "./RootLayout";
import ResultsPage from "./_pages/Rework/Results/Page";
import CompetitionsPage from "./_pages/Rework/Competitions/Page";
import CompetitionPage from "./_pages/Rework/Competition/Page";
import LandingPage from "./_pages/Rework/Landing/Page";
import RootWithPaddingLayout from "./RootWithPaddingLayout";
import BotPage from "./_pages/Rework/Bot/Page";
import RoundsPage from "./_pages/Rework/_Round/Page";
import AuthorPage from "./_pages/Rework/_Author/Page";

export default function App() {
  return (
    <Routes>
      <Route path="dashboard/rework">
        <Route element={<RootLayout />}>
          <Route path="landing" element={<LandingPage />} />
        </Route>

        <Route element={<RootWithPaddingLayout />}>
          <Route path="competitions" element={<CompetitionsPage />} />
          <Route
            path="competitions/:competitionId"
            element={<CompetitionPage />}
          />
          <Route path="bots" element={<BotsPage />} />
          <Route path="bots/:botId" element={<BotPage />} />
          <Route path="rounds/:roundId" element={<RoundsPage />} />
          <Route path="authors" element={<AuthorsPage />} />
          <Route path="authors/:userId" element={<AuthorPage />} />
          <Route path="results" element={<ResultsPage />} />
        </Route>
      </Route>

      <Route element={<RootWithPaddingLayout />} path="dashboard/rework">
        <Route path="landing" element={<LandingPage />} />
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

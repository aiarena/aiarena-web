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
import MatchPage from "./_pages/Rework/_Match/Page";
import CompetitionParticipationPage from "./_pages/Rework/CompetitionParticipation/Page";

export default function App() {
  return (
    <Routes>
      <Route element={<RootLayout />}>
        <Route index element={<LandingPage />} />
        <Route
          path="competitions/stats/:id/:slug?"
          element={<CompetitionParticipationPage />}
        />
      </Route>
      <Route element={<RootWithPaddingLayout />}>
        <Route path="authors" element={<AuthorsPage />} />
        <Route path="authors/:userId" element={<AuthorPage />} />
        <Route path="competitions" element={<CompetitionsPage />} />
        <Route
          path="competitions/:competitionId"
          element={<CompetitionPage />}
        />
        <Route path="rounds/:roundId" element={<RoundsPage />} />
        <Route path="bots" element={<BotsPage />} />
        <Route path="matches/:matchId" element={<MatchPage />} />
        <Route path="results" element={<ResultsPage />} />
        <Route path="bots/:botId" element={<BotPage />} />
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

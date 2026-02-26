import { Navigate, Route, Routes } from "react-router";
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
import Maps from "./_pages/Rework/CompetitionParticipation/Pages/Maps";
import EloGraph from "./_pages/Rework/CompetitionParticipation/Pages/EloGraph";
import WinsByRace from "./_pages/Rework/CompetitionParticipation/Pages/WinsByRace";
import WinsByTime from "./_pages/Rework/CompetitionParticipation/Pages/WinsByTime";
import CompetitionParticipationSideNav from "./_pages/Rework/CompetitionParticipation/CompetitionParticipationSideNav";
import CompetitionParticipationTopNav from "./_components/_nav/CompetitionParticipationTopNav";
import Matchups from "./_pages/Rework/CompetitionParticipation/Pages/Matchups";

export default function App() {
  return (
    <Routes>
      <Route element={<RootLayout />}>
        <Route index element={<LandingPage />} />
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
      <Route path="dashboard/rework">
        <Route element={<RootLayout />}>
          <Route
            path="competitions/stats/:id"
            element={<CompetitionParticipationSideNav />}
          >
            <Route index element={<Navigate to="overview" replace />} />
            <Route
              path="overview"
              element={
                <CompetitionParticipationTopNav
                  pages={[
                    { name: "ELO Graph", to: "elograph" },
                    { name: "Wins By Time", to: "winsbytime" },
                    { name: "Wins By Race", to: "winsbyrace" },
                  ]}
                />
              }
            >
              <Route index element={<Navigate to="elograph" replace />} />
              <Route path="elograph" element={<EloGraph />} />
              <Route path="winsbytime" element={<WinsByTime />} />
              <Route path="winsbyrace" element={<WinsByRace />} />
            </Route>

            <Route path="maps" element={<Maps />} />
            <Route path="matchups" element={<Matchups />} />
          </Route>
        </Route>

        <Route element={<RootWithPaddingLayout />}>
          <Route path="results" element={<ResultsPage />} />
          <Route path="bots/:botId" element={<BotPage />} />
        </Route>
      </Route>
    </Routes>
  );
}

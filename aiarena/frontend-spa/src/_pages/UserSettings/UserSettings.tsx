import { graphql, useLazyLoadQuery } from "react-relay";

import { UserSettingsQuery } from "./__generated__/UserSettingsQuery.graphql";
import UserSettingsSection from "./UserSettingsSection";
import { reverseUrl } from "@/_lib/reverseUrl";

export default function UserSettings() {
  const data = useLazyLoadQuery<UserSettingsQuery>(
    graphql`
      query UserSettingsQuery {
        viewer {
          ...UserSettingsSection_viewer
        }
      }
    `,
    {}
  );

  if (!data.viewer) {
    window.location.replace(reverseUrl("login"));
    return null;
  }

  return (
    <>
      <UserSettingsSection viewer={data.viewer} />
    </>
  );
}

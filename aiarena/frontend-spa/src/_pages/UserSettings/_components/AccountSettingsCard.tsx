import { graphql, useFragment, useMutation } from "react-relay";

import SquareButton from "@/_components/_actions/SquareButton";
import useSnackbarErrorHandlers from "@/_lib/useSnackbarErrorHandlers";
import { reverseUrl } from "@/_lib/reverseUrl";
import { footerLinks } from "@/_data/footerLinks";
import SettingsCard from "./SettingsCard";
import SettingsGroup from "./SettingsGroup";
import LinkedAccountRow from "./LinkedAccountRow";
import SettingsToggleRow from "./SettingsToggleRow";
import { AccountSettingsCard_viewer$key } from "./__generated__/AccountSettingsCard_viewer.graphql";
import { AccountSettingsCardUpdateMutation } from "./__generated__/AccountSettingsCardUpdateMutation.graphql";
import { AccountSettingsCardSignOutMutation } from "./__generated__/AccountSettingsCardSignOutMutation.graphql";
import { AccountSettingsCardUnlinkDiscordMutation } from "./__generated__/AccountSettingsCardUnlinkDiscordMutation.graphql";
import { AccountSettingsCardUnlinkPatreonMutation } from "./__generated__/AccountSettingsCardUnlinkPatreonMutation.graphql";

interface AccountSettingsCardProps {
  viewer: AccountSettingsCard_viewer$key;
}

export default function AccountSettingsCard(props: AccountSettingsCardProps) {
  const viewer = useFragment(
    graphql`
      fragment AccountSettingsCard_viewer on Viewer {
        id
        receiveEmailComms
        linkedDiscord
        linkedPatreon
      }
    `,
    props.viewer,
  );

  const [updateSettings, updatingSettings] =
    useMutation<AccountSettingsCardUpdateMutation>(graphql`
      mutation AccountSettingsCardUpdateMutation(
        $input: UpdateAccountSettingsInput!
      ) {
        updateAccountSettings(input: $input) {
          viewer {
            ...AccountSettingsCard_viewer
          }
          errors {
            messages
            field
          }
        }
      }
    `);

  const [signOut, signingOut] =
    useMutation<AccountSettingsCardSignOutMutation>(graphql`
      mutation AccountSettingsCardSignOutMutation {
        signOut {
          errors {
            messages
            field
          }
        }
      }
    `);

  const [unlinkDiscord] =
    useMutation<AccountSettingsCardUnlinkDiscordMutation>(graphql`
      mutation AccountSettingsCardUnlinkDiscordMutation {
        unlinkDiscord {
          viewer {
            ...AccountSettingsCard_viewer
          }
          errors {
            messages
            field
          }
        }
      }
    `);

  const [unlinkPatreon] =
    useMutation<AccountSettingsCardUnlinkPatreonMutation>(graphql`
      mutation AccountSettingsCardUnlinkPatreonMutation {
        unlinkPatreon {
          viewer {
            ...AccountSettingsCard_viewer
          }
          errors {
            messages
            field
          }
        }
      }
    `);

  const unlinkDiscordHandlers = useSnackbarErrorHandlers(
    "unlinkDiscord",
    "Discord unlinked.",
  );
  const unlinkPatreonHandlers = useSnackbarErrorHandlers(
    "unlinkPatreon",
    "Patreon unlinked.",
  );

  const updateHandlers = useSnackbarErrorHandlers(
    "updateAccountSettings",
    "Email preference saved.",
  );
  const signOutHandlers = useSnackbarErrorHandlers(
    "signOut",
    "Successfully logged out! Redirecting...",
  );

  const handleReceiveEmailsChange = (receiveEmailComms: boolean) => {
    updateSettings({
      variables: { input: { receiveEmailComms } },
      optimisticResponse: {
        updateAccountSettings: {
          viewer: { id: viewer.id, receiveEmailComms },
          errors: [],
        },
      },
      onCompleted: (...args) => {
        updateHandlers.onCompleted(...args);
      },
      onError: updateHandlers.onError,
    });
  };

  const handleSignOut = () => {
    signOut({
      variables: {},
      onCompleted: (...args) => {
        if (signOutHandlers.onCompleted(...args)) {
          // Full navigation, not client-side routing: the session (and its
          // CSRF token) is gone, so the SPA must reload from scratch.
          window.location.href = reverseUrl("home");
        }
      },
      onError: signOutHandlers.onError,
    });
  };

  // Linking is a server-rendered OAuth round trip: leave the SPA for it, and
  // the server redirects back here, so the page reloads with the new status.
  const navigateTo = (url: string) => () => {
    window.location.href = url;
  };
  const socialIcon = (name: string) =>
    footerLinks.socialLinks.find((it) => it.name == name)?.icon;

  return (
    <SettingsCard title="Account settings">
      <SettingsGroup title="Email">
        <SettingsToggleRow
          label="Receive emails"
          enabled={viewer.receiveEmailComms ?? false}
          onChange={handleReceiveEmailsChange}
          disabled={updatingSettings}
        />
      </SettingsGroup>

      <SettingsGroup title="Linked accounts">
        <LinkedAccountRow
          name="Discord"
          iconPath={socialIcon("Discord")}
          linked={Boolean(viewer.linkedDiscord)}
          onLink={navigateTo(reverseUrl("discord_bind_index"))}
          onUnlink={() =>
            unlinkDiscord({
              variables: {},
              onCompleted: (...args) => {
                unlinkDiscordHandlers.onCompleted(...args);
              },
              onError: unlinkDiscordHandlers.onError,
            })
          }
        />
        <LinkedAccountRow
          name="Patreon"
          iconPath={socialIcon("Patreon")}
          invertIcon
          linked={Boolean(viewer.linkedPatreon)}
          onLink={navigateTo(reverseUrl("patreon_bind_index"))}
          onUnlink={() =>
            unlinkPatreon({
              variables: {},
              onCompleted: (...args) => {
                unlinkPatreonHandlers.onCompleted(...args);
              },
              onError: unlinkPatreonHandlers.onError,
            })
          }
        />
      </SettingsGroup>

      <SettingsGroup title="Security">
        <div className="flex flex-wrap gap-3">
          <SquareButton
            href={reverseUrl("password_change")}
            text="Change password"
          />
          <SquareButton
            onClick={handleSignOut}
            isLoading={signingOut}
            disabled={signingOut}
            color="red"
            text="Log out"
          />
        </div>
      </SettingsGroup>
    </SettingsCard>
  );
}

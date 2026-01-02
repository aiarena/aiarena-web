import { getIDFromBase64, getNodes } from "@/_lib/relayHelpers";
import {
  graphql,
  useFragment,
  useLazyLoadQuery,
  useMutation,
} from "react-relay";
import { JoinCompetitionModal_bot$key } from "./__generated__/JoinCompetitionModal_bot.graphql";
import { JoinCompetitionModalCompetitionsQuery } from "./__generated__/JoinCompetitionModalCompetitionsQuery.graphql";
import Modal from "@/_components/_actions/Modal";
import { JoinCompetitionModalMutation } from "./__generated__/JoinCompetitionModalMutation.graphql";
import SimpleToggle from "@/_components/_actions/_toggle/SimpleToggle";
import useSnackbarErrorHandlers from "@/_lib/useSnackbarErrorHandlers";
import { Link } from "react-router";

interface JoinCompetitionModalProps {
  bot: JoinCompetitionModal_bot$key;
  isOpen: boolean;
  onClose: () => void;
}

export default function JoinCompetitionModal({
  isOpen,
  onClose,
  ...props
}: JoinCompetitionModalProps) {
  const bot = useFragment(
    graphql`
      fragment JoinCompetitionModal_bot on BotType {
        id
        name
        competitionParticipations {
          edges {
            node {
              active
              id
              competition {
                id
                name
                status
              }
            }
          }
        }
      }
    `,
    props.bot
  );

  // TODO
  // maybe theres a better way to fetch this
  const competition_data =
    useLazyLoadQuery<JoinCompetitionModalCompetitionsQuery>(
      graphql`
        query JoinCompetitionModalCompetitionsQuery {
          competitions(last: 20) {
            edges {
              node {
                id
                name
                dateCreated
                status
              }
            }
          }
        }
      `,
      {}
    );

  const [updateCompetitionparticipation, updating] =
    useMutation<JoinCompetitionModalMutation>(graphql`
      mutation JoinCompetitionModalMutation(
        $input: UpdateCompetitionParticipationInput!
        $botId: ID!
      ) {
        updateCompetitionParticipation(input: $input) {
          viewer {
            activeBotParticipations
          }
          node(id: $botId) {
            ... on BotType {
              ...UserBot_bot
            }
          }
          errors {
            field
            messages
          }
        }
      }
    `);
  const { onCompleted, onError } = useSnackbarErrorHandlers(
    "updateCompetitionParticipation",
    "Bot Participation Updated!"
  );

  const joinableCompetitions = getNodes(competition_data.competitions).filter(
    (comp) => comp.status != "CLOSING" && comp.status != "CLOSED"
  );

  const botCompetitionParticipations = getNodes(bot.competitionParticipations);

  const hasActiveCompetitionParticipation = (competitionId: string) => {
    return (
      botCompetitionParticipations?.some(
        (participation) =>
          competitionId === participation.competition.id &&
          participation.active === true
      ) || false
    );
  };

  const handleToggleCompetitionParticipation = (compID: string) => {
    updateCompetitionparticipation({
      variables: {
        input: {
          active: !hasActiveCompetitionParticipation(compID) ? true : false,
          bot: bot.id,
          competition: compID,
        },
        botId: bot.id,
      },
      onCompleted: (...args) => {
        onCompleted(...args);
      },
      onError,
    });
  };

  return (
    <Modal
      onClose={onClose}
      isOpen={isOpen}
      title={`Edit Competitions - ${bot.name}`}
    >
      <div className="space-y-4">
        {joinableCompetitions &&
          joinableCompetitions.length > 0 &&
          joinableCompetitions.map((comp) => (
            <div
              className="flex items-center space-x-2 border border-neutral-600 shadow-lg shadow-black rounded-md p-3 justify-between bg-darken-4"
              key={comp.id}
            >
              <div className="block">
                <div>
                  <Link
                    to={`/competitions/${getIDFromBase64(comp.id, "CompetitionType")}`}
                    className="font-bold"
                  >
                    {comp.name}
                  </Link>
                  <p>{comp.status}</p>
                </div>
              </div>
              <SimpleToggle
                enabled={hasActiveCompetitionParticipation(comp.id)}
                onChange={() => handleToggleCompetitionParticipation(comp.id)}
                disabled={updating}
              />
            </div>
          ))}
      </div>
    </Modal>
  );
}

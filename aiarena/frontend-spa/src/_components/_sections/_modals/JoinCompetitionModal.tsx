import { extractRelayID, getNodes } from "@/_lib/relayHelpers";
import {
  graphql,
  useFragment,
  useLazyLoadQuery,
  useMutation,
} from "react-relay";
import { JoinCompetitionModal_bot$key } from "./__generated__/JoinCompetitionModal_bot.graphql";
import { JoinCompetitionModalCompetitionsQuery } from "./__generated__/JoinCompetitionModalCompetitionsQuery.graphql";
import Modal from "@/_components/_props/Modal";
import { JoinCompetitionModalMutation } from "./__generated__/JoinCompetitionModalMutation.graphql";
import SimpleToggle from "@/_components/_props/_toggle/SimpleToggle";
import useSnackbarErrorHandlers from "@/_lib/useSnackbarErrorHandlers";

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
                type
                dateCreated
                status
              }
            }
          }
        }
      `,
      {}
    );

  const [updateCompetitionparticipation] =
    useMutation<JoinCompetitionModalMutation>(graphql`
      mutation JoinCompetitionModalMutation(
        $input: UpdateCompetitionParticipationInput!
      ) {
        updateCompetitionParticipation(input: $input) {
          competitionParticipation {
            active
            id
            bot {
              id
            }
          }
          errors {
            field
            messages
          }
        }
      }
    `);
  const handlers = useSnackbarErrorHandlers(
    "updateCompetitionParticipation",
    "Bot Participation Updated!"
  );

  const openCompetitions = getNodes(competition_data.competitions).filter(
    (comp) => comp.status == "OPEN"
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
      },
      ...handlers,
    });
  };

  return isOpen ? (
    <Modal onClose={onClose} title={`Edit Competitions - ${bot.name}`}>
      <div className="space-y-4">
        {openCompetitions &&
          openCompetitions.length > 0 &&
          openCompetitions.map((comp) => (
            <div
              className="flex items-center space-x-2 border border-gray-600 rounded-md p-2 justify-between"
              key={comp.id}
            >
              <div className="block">
                <div>
                  <a
                    href={`/competitions/${extractRelayID(comp.id, "CompetitionType")}`}
                    className="text-sm font-semibold"
                  >
                    {comp.name}
                  </a>
                </div>
              </div>
              <SimpleToggle
                enabled={hasActiveCompetitionParticipation(comp.id)}
                onChange={() => handleToggleCompetitionParticipation(comp.id)}
              />
            </div>
          ))}
      </div>
    </Modal>
  ) : null;
}

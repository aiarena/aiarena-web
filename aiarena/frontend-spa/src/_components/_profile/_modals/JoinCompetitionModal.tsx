import { getNodes } from "@/_lib/relayHelpers";
import {
  graphql,
  useFragment,
  useLazyLoadQuery,
  useMutation,
} from "react-relay";
import { JoinCompetitionModal_bot$key } from "./__generated__/JoinCompetitionModal_bot.graphql";
import { JoinCompetitionModalCompetitionsQuery } from "./__generated__/JoinCompetitionModalCompetitionsQuery.graphql";
// import { useUpdateCompetitionParticipation } from "@/_components/_hooks/useUpdateCompetitionParticipation";
import Modal from "@/_components/_props/Modal";
import { JoinCompetitionModalMutation } from "./__generated__/JoinCompetitionModalMutation.graphql";
import SimpleToggle from "@/_components/_props/_toggle/SimpleToggle";

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
        }
      }
    `);

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
    });
  };

  return isOpen ? (
    <Modal onClose={onClose} title={`${bot.name} - Edit competitions`}>
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
                  <span className="text-gray-300">{comp.name}</span>
                </div>
                <div className="text-left">
                  {hasActiveCompetitionParticipation(comp.id) ? (
                    <span className="text-customGreen">Currently Active</span>
                  ) : (
                    <span className="text-red-400">Currently Inactive</span>
                  )}
                </div>
              </div>
              <SimpleToggle
                enabled={hasActiveCompetitionParticipation(comp.id)}
                setEnabled={() => handleToggleCompetitionParticipation(comp.id)}
              />
            </div>
          ))}
      </div>
    </Modal>
  ) : null;
}

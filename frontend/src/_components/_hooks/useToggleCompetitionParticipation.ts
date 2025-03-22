import { useMutation, graphql } from 'react-relay';
import { useState } from 'react';
import { useToggleCompetitionParticipationMutation } from './__generated__/useToggleCompetitionParticipationMutation.graphql';

export interface CompetitionParticipationResponse {
  active: boolean;
  id: string;
  bot: { id: string };
}

export type ToggleCompetitionParticipationFunction = (
  bot: string,
  competition: string,
  onSuccess?: (result?: CompetitionParticipationResponse | null) => void
) => void;



export const useToggleCompetitionParticipation = () => {
  const [error, setError] = useState<string | null>(null);

  const [commit, isInFlight] = useMutation<useToggleCompetitionParticipationMutation>(graphql`
    mutation useToggleCompetitionParticipationMutation($input: ToggleCompetitionParticipationInput!) {
      toggleCompetitionParticipation(input: $input) {
        errors { messages, field }
        competitionParticipation { active, id, bot { id } }
      }
    }
  `);

  const toggleParticipation: ToggleCompetitionParticipationFunction = (bot, competition, onSuccess) => {
    commit({
      variables: { input: { bot, competition } },
      onCompleted: ({ toggleCompetitionParticipation }) => {
        const errors = toggleCompetitionParticipation?.errors;

        if (errors?.length) {
          setError(errors[0]?.messages?.[0] ?? 'An unknown error occurred.');
        } else {
          setError(null);
          onSuccess?.(toggleCompetitionParticipation?.competitionParticipation);
        }
      },
      onError: () => setError('Something went wrong. Please try again.')
    });
  };

  const result: [ToggleCompetitionParticipationFunction, boolean, string | null] = [
    toggleParticipation,
    isInFlight,
    error
  ];

  return result;
};

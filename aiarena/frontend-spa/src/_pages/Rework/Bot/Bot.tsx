import { graphql, useLazyLoadQuery } from "react-relay";
import InformationSection from "./InformationSection";
import { BotQuery } from "./__generated__/BotQuery.graphql";
import { useParams } from "react-router";

import { useState } from "react";
import { getBase64FromID } from "@/_lib/relayHelpers";
import BotCompetitionsTable from "./BotCompetitionsTable";
import FetchError from "@/_components/_display/FetchError";

import SimpleToggle from "@/_components/_actions/_toggle/SimpleToggle";

export default function Bot() {
  const { botId } = useParams<{ botId: string }>();
  const [onlyActive, setOnlyActive] = useState(false);

  const data = useLazyLoadQuery<BotQuery>(
    graphql`
      query BotQuery($id: ID!) {
        node(id: $id) {
          ... on BotType {
            ...InformationSection_bot
            ...BotCompetitionsTable_bot
          }
        }
      }
    `,
    { id: getBase64FromID(botId!, "BotType") || "" },
  );

  if (!data.node) {
    return <FetchError type="bot" />;
  }

  return (
    <>
      <div className="mb-8">
        <h4 className="mb-4">Bot information</h4>
        <InformationSection bot={data.node} />
      </div>

      <div>
        <h4 className="mb-4">Competition Participations</h4>
        <BotCompetitionsTable
          bot={data.node}
          onlyActive={onlyActive}
          appendHeader={
            <div
              className="flex gap-4 items-center"
              role="group"
              aria-label="Bot filtering controls"
            >
              <div className="flex items-center gap-2">
                <label
                  htmlFor="downloadable-toggle"
                  className="text-sm font-medium text-gray-300"
                >
                  Only active
                </label>
                <SimpleToggle
                  enabled={onlyActive}
                  onChange={() => setOnlyActive(!onlyActive)}
                />
              </div>
            </div>
          }
        />
      </div>
    </>
  );
}

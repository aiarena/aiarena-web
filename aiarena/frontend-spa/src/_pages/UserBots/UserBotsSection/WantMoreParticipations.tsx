import { useState } from "react";
import { graphql, useFragment } from "react-relay";

import MoreParticipationsModal from "./_modals/MoreParticipationsModal";
import { WantMoreParticipations_viewer$key } from "./__generated__/WantMoreParticipations_viewer.graphql";

interface WantMoreParticipationsProps {
  viewer: WantMoreParticipations_viewer$key;
}

export default function WantMoreParticipations(
  props: WantMoreParticipationsProps,
) {
  const viewer = useFragment(
    graphql`
      fragment WantMoreParticipations_viewer on Viewer {
        ...MoreParticipationsModal_viewer
      }
    `,
    props.viewer,
  );

  const [isModalOpen, setModalOpen] = useState(false);

  return (
    <>
      <p>
        <i>
          <button
            className="cursor-pointer text-customGreen hover:text-white"
            onClick={() => setModalOpen(true)}
          >
            Get more active participations
          </button>
        </i>
      </p>

      <MoreParticipationsModal
        viewer={viewer}
        isOpen={isModalOpen}
        onClose={() => setModalOpen(false)}
      />
    </>
  );
}

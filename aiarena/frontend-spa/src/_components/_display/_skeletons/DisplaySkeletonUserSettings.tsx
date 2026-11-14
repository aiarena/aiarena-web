import SectionDivider from "../SectionDivider";
import DisplaySkeleton from "./DisplaySkeleton";

// The cards are the same translucent dark as the real ones, which is about the
// default bar colour, so bars drawn straight on a card use a lighter tone.
// Bars inside the black rows keep the default.
const ON_CARD = { baseColor: "#33343c", highlightColor: "#3f4049" };

/** One settings group inside a card: its small label, then its content. */
type GroupShape =
  | { rows: number; buttons?: number[] } // full-width rows (toggles, linked accounts), then buttons by width
  | { buttons: number[] } // just a row of buttons, by width
  | { text: number; button: number }; // a short paragraph and a button

function Buttons({ widths }: { widths: number[] }) {
  return (
    <div className="flex flex-wrap gap-3">
      {widths.map((width, i) => (
        <DisplaySkeleton key={i} height={36} width={width} {...ON_CARD} />
      ))}
    </div>
  );
}

function CardSkeleton({
  titleWidth,
  groups,
}: {
  titleWidth: number;
  groups: GroupShape[];
}) {
  return (
    // Same card as the real SettingsCard, so nothing moves or changes colour
    // when it loads.
    <section className="bg-darken-2 border border-neutral-600 shadow-lg shadow-black rounded-md backdrop-blur-sm">
      <div className="px-4 py-2 border-b border-neutral-600">
        <DisplaySkeleton height={20} width={titleWidth} {...ON_CARD} />
      </div>
      <div className="p-4 flex flex-col gap-5 divide-y divide-neutral-700 [&>*:not(:first-child)]:pt-5">
        {groups.map((group, i) => (
          <div key={i}>
            <div className="mb-2">
              <DisplaySkeleton height={12} width={90} {...ON_CARD} />
            </div>
            <div className="flex flex-col gap-2">
              {"rows" in group &&
                Array.from({ length: group.rows }).map((_, r) => (
                  // The real rows are black boxes (toggle / linked account rows).
                  <div
                    key={r}
                    className="flex h-10 items-center rounded bg-darken-2 px-2"
                  >
                    <DisplaySkeleton height={12} width={120} />
                  </div>
                ))}
              {"buttons" in group && group.buttons && (
                <Buttons widths={group.buttons} />
              )}
              {"text" in group && (
                <>
                  <DisplaySkeleton
                    height={14}
                    count={group.text}
                    {...ON_CARD}
                  />
                  <Buttons widths={[group.button]} />
                </>
              )}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

function StatusInfoSkeleton() {
  return (
    <div className="ml-4 space-y-2">
      {[0, 1].map((i) => (
        <div key={i} className="flex gap-6">
          <DisplaySkeleton height={14} width={110} />
          <DisplaySkeleton height={14} width={80} />
        </div>
      ))}
    </div>
  );
}

/** Loading state for the profile page, laid out with the same classes as the
 * real page (avatar column beside the main column, cards in columns). */
export default function DisplaySkeletonUserSettings() {
  return (
    <div
      aria-busy="true"
      aria-label="Loading your profile"
      className="lg:flex lg:flex-row lg:gap-4"
    >
      <div className="relative m-0 md:m-3 lg:shrink-0">
        <div className="flex justify-center">
          <DisplaySkeleton height={205} width={205} />
        </div>
        <div className="hidden lg:block mt-4">
          <StatusInfoSkeleton />
        </div>
      </div>

      <div className="min-w-0 lg:flex-1">
        <div className="py-4 flex flex-col items-center lg:items-start gap-4 mb-4">
          <DisplaySkeleton height={30} width={160} />
          <div className="lg:hidden">
            <StatusInfoSkeleton />
          </div>
        </div>
        <SectionDivider className="pb-4" />
        <div className="columns-1 xl:columns-2 2xl:columns-3 gap-6 [&>*]:mb-6 [&>*]:break-inside-avoid">
          {/* Account settings: email toggle, linked accounts, security buttons */}
          <CardSkeleton
            titleWidth={140}
            groups={[{ rows: 1 }, { rows: 2 }, { buttons: [150, 90] }]}
          />
          {/* API token: token row + Regenerate, then GraphQL blurb + API docs */}
          <CardSkeleton
            titleWidth={90}
            groups={[
              { rows: 1, buttons: [110] },
              { text: 2, button: 110 },
            ]}
          />
          {/* Website settings: hide spoilers toggle */}
          <CardSkeleton titleWidth={130} groups={[{ rows: 1 }]} />
        </div>
      </div>
    </div>
  );
}

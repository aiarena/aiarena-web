import ActiveDot from "@/_components/_display/ActiveDot";
import LoadingSpinner from "@/_components/_display/LoadingSpinnerGray";
import SectionDivider from "@/_components/_display/SectionDivider";
import WrappedTitle from "@/_components/_display/WrappedTitle";
import SimpleToggle from "@/_components/_actions/_toggle/SimpleToggle";
import MainButton from "@/_components/_actions/MainButton";
import SquareButton from "@/_components/_actions/SquareButton";
import ProfileBot from "@/_components/_display/userbot/UserBot";
import { useState } from "react";
import MDEditor from "@uiw/react-md-editor";
import rehypeSanitize from "rehype-sanitize";
import { graphql, useLazyLoadQuery } from "react-relay";
import { ExamplesQuery } from "./__generated__/ExamplesQuery.graphql";

export default function Examples() {
  const [toggle, setToggle] = useState(true);
  const [markdown, setMarkdown] = useState<string | undefined>(
    `**Hello world!!!**`
  );

  const bot = useLazyLoadQuery<ExamplesQuery>(
    graphql`
      query ExamplesQuery($id: ID!) {
        node(id: $id) {
          ... on BotType {
            ...UserBot_bot
          }
        }
      }
    `,
    { id: decodeURIComponent("Qm90VHlwZToyNDg=") }
  );

  return (
    <div>
      <h1>Examples</h1>
      <div className="p-10 space-y-4">
        <h4>Fonts</h4>
        <p className="text-xl font-quicksand">This is Quicksand</p>
        <p className="text-xl font-gugi">This is Gugi</p>
        <p className="text-xl">This is default sans-serif</p>
      </div>
      <div className="p-10 space-y-4 max-w-160">
        <h4>Sections</h4>

        <SectionDivider />
        <WrappedTitle title="A Wrapped Title" />
      </div>
      <div className="p-10 space-y-4">
        <h4>Toggles</h4>
        <SimpleToggle enabled={toggle} onChange={setToggle} />
      </div>
      <div className="p-10 space-y-4">
        <h4>Buttons</h4>
        <SquareButton text="Square Button" />
        <br />
        <MainButton text="Main Button" />
      </div>
      <div className="p-10 space-y-4">
        <h4>Loading Spinners</h4>
        <LoadingSpinner color="white" />
        <LoadingSpinner color="light-gray" />
        <LoadingSpinner color="gray" />
        <LoadingSpinner color="black" />
      </div>

      <div className="p-10 space-y-4">
        <h4>Decoration</h4>
        <ActiveDot />
      </div>

      <div className="p-10 space-y-4">
        <h4>Markdown</h4>
        <h3>Editor</h3>
        <MDEditor
          value={markdown}
          onChange={setMarkdown}
          previewOptions={{
            rehypePlugins: [[rehypeSanitize]],
          }}
        />
      </div>
      <div>
        <h4>Eris - as appears on console.</h4>
        {bot.node && <ProfileBot bot={bot.node} />}
      </div>
    </div>
  );
}

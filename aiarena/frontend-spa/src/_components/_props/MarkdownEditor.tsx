import MDEditor from "@uiw/react-md-editor";
import rehypeSanitize from "rehype-sanitize";

interface MarkDownEditorProps {
  value: string;
  setValue: (value: string) => void;
}

export default function MarkdownEditor({
  value,
  setValue,
}: MarkDownEditorProps) {
  return (
    <MDEditor
      style={{ minHeight: "100%", flex: 1 }}
      value={value}
      onChange={(val) => setValue(val ?? "")}
      previewOptions={{
        rehypePlugins: [[rehypeSanitize]],
      }}
    />
  );
}

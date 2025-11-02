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
    <div data-color-mode="dark" className="h-full w-full">
      <MDEditor
        style={{ minHeight: "100%", flex: 1 }}
        value={value}
        onChange={(val) => setValue(val ?? "")}
        textareaProps={{
          placeholder:
            "Start writing your biography here — a preview will be appear to the right",
        }}
        previewOptions={{
          rehypePlugins: [[rehypeSanitize]],
        }}
      />
    </div>
  );
}

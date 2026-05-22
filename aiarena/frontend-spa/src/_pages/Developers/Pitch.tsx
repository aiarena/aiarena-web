interface PitchProps {
  title: string;
  body: string;
  href?: string;
  linkText?: string;
}

export default function Pitch({ title, body, href, linkText }: PitchProps) {
  return (
    <div className="bg-darken-2 border border-neutral-600 rounded-md p-3 flex flex-col">
      <h4 className="font-semibold mb-1">{title}</h4>
      <p className="text-gray-300 text-sm flex-1">{body}</p>
      {href && linkText ? (
        <a
          href={href}
          target="_blank"
          rel="noopener"
          className="text-customGreen underline text-sm mt-2"
        >
          {linkText}
        </a>
      ) : null}
    </div>
  );
}

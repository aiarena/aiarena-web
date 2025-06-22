import { socialLinks } from "@/_data/socialLinks";

export default function WantMore() {
  return (
    <p>
      <i>
        Want more? Consider{" "}
        <a
          className="cursor-pointer"
          target="_blank"
          href={socialLinks["patreon"]}
        >
          supporting us
        </a>
        .
      </i>
    </p>
  );
}

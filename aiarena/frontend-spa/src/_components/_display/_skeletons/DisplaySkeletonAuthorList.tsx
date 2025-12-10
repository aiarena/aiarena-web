import DisplaySkeletonAuthor from "./DisplaySkeletonAuthor";

export default function DisplaySkeletonAuthorList() {
  return (
    <ul
      className="
        grid gap-12
        justify-items-center
        [grid-template-columns:repeat(auto-fill,minmax(20rem,1fr))]
      "
    >
      {Array.from({ length: 40 }).map((_, i) => (
        <li key={i} role="listitem" className="w-full max-w-[42rem]">
          <DisplaySkeletonAuthor />
        </li>
      ))}
    </ul>
  );
}

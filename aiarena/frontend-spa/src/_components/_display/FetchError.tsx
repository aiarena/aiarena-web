interface FetchErrorProps {
  type: string;
}

export default function FetchError(props: FetchErrorProps) {
  return <span>Unable to fetch {props.type}...</span>;
}

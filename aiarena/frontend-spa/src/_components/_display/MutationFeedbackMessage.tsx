export default function MutationFeedbackMessage({
  onSuccess,
  onError,
}: {
  onSuccess?: string | null;
  onError?: string | null;
}) {
  return (
    <>
      {onSuccess ? <p className="text-customGreen">{onSuccess}</p> : <></>}
      {onError ? <p className="text-red-500">{onError}</p> : <></>}
    </>
  );
}

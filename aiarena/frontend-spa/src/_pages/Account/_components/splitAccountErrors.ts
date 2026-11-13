import { BackendErrors } from "@/_lib/useBackendErrors";

/**
 * Split backend errors for a form: messages for fields the form renders go
 * under their input; everything else (`__all__`, fields like an expired
 * `token`, GraphQL/network failures) is shown at the top of the form.
 */
export function splitAccountErrors(
  backendErrors: BackendErrors,
  formFields: readonly string[],
) {
  const byField: Record<string, readonly string[]> = {};
  const general: string[] = [];

  for (const error of backendErrors.formErrors ?? []) {
    if (!error) continue;
    if (formFields.includes(error.field)) {
      byField[error.field] = error.messages;
    } else {
      general.push(...error.messages);
    }
  }
  for (const error of backendErrors.graphqlErrors ?? []) {
    general.push(error.message);
  }
  if (backendErrors.failError) {
    general.push("Something went wrong. Please try again.");
  }

  return { byField, general };
}

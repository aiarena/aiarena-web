import {
  Variables, UploadableMap,
} from "relay-runtime";


export default async function fetchGraphQL(text: string | null, variables: Variables, uploadables: UploadableMap | null | undefined) {
  let body;
  const headers: { [key: string]: string } = {};
  if (uploadables && Object.keys(uploadables).length !== 0) {
    // https://github.com/jaydenseric/graphql-multipart-request-spec

    if (!window.FormData) {
      throw new Error("Uploading files without `FormData` not supported.");
    }

    const formData = new FormData();
    formData.append(
      "operations",
      JSON.stringify({
        query: text,
        variables,
      }),
    );
    const map: { [key: string]: string[] } = {};
    Object.keys(uploadables).forEach((key) => {
      if (Object.prototype.hasOwnProperty.call(uploadables, key)) {
        const forUpload = uploadables[key];
        if (Array.isArray(forUpload)) {
          forUpload.forEach((file, fileIndex) => {
            const fileKey = `${key}.${fileIndex}`;
            formData.append(fileKey, file);
            map[fileKey] = [`variables.${fileKey}`];
          });
        } else {
          formData.append(key, forUpload);
          map[key] = [`variables.${key}`];
        }
      }
    });
    formData.append("map", JSON.stringify(map));

    body = formData;
  } else {
    body = JSON.stringify({
      query: text,
      variables,
    });
    headers["Content-Type"] = "application/json";
  }

  const response = await fetch("/graphql/", {
    method: "POST",
    headers: headers,
    body: body,
  });

  if (response.status >= 500) {
    throw new Error(`Error code ${response.status} when fetching graphql`);
  }

  return response.json();
}

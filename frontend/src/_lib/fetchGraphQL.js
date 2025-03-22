export default async function fetchGraphQL(text, variables, uploadables) {
  let body;
  const headers = {};
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
    const map = {};
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

  let apiUrl;
  if (typeof window === "undefined") {
    // eslint-disable-next-line @typescript-eslint/no-require-imports
    const cookieStore = await require("next/headers").cookies();
    const cookiesToPass = ["csrftoken", "sessionid"];
    headers["Cookie"] = cookiesToPass
      .filter((cookieName) => cookieStore.has(cookieName))
      .map(
        (cookieName) => `${cookieName}=${cookieStore.get(cookieName).value};`,
      )
      .join(" ");
    apiUrl = `${process.env.API_URL}/graphql/`;
  } else {
    apiUrl = "/graphql/";
  }

  const response = await fetch(apiUrl, {
    method: "POST",
    headers: headers,
    body: body,
  });

  if (response.status >= 500) {
    throw new Error(`Error code ${response.status} when fetching graphql`);
  }

  return response.json();
}

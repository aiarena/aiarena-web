import { getJWTToken, userPool } from "./cognito";
import axios, { AxiosResponse } from "axios";
import { getSecurePresignedUrl } from "./presignedUrl";

interface PostFileOptions {
  file: any;
}

export async function postFile({
  
  file,
}: PostFileOptions): Promise<AxiosResponse<any>> {
    console.log(file)
    const presignedUrl = await getSecurePresignedUrl();
    return axios
      .put(`${presignedUrl.url}`, file.current, {
        headers: {
          //bugs when sending auth token... look into this...
          "Content-Type": file.current.type,
          "Content-Disposition": `attachment; filename="${file.current.name}"`,
        },
      })
      .then((response) => {
        console.log("response", response)
        if (response.status === 200) {
          return {
            data: { response: "success", key: presignedUrl.key, user: presignedUrl.user, id: presignedUrl.id },
            status: 200,
            statusText: 'OK',
            headers: {},
            config: {}
          } as AxiosResponse;
        } else {
          throw new Error(`An error occurred: ${response.statusText}`);
        }
      });
  // });
}

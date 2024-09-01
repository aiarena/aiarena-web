export function CheckGetBase64(event) {
  try {
    if (event.isBase64Encoded) {
      const base64String = event.body;
      const decodedString = Buffer.from(base64String, "base64").toString(
        "utf-8"
      );
      return decodedString;
    } else {
      return event.body;
    }
  } catch (error) {
    console.log("decoding error");
    return "Decoding Error";
  }
}

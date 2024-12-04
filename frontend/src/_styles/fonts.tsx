import localFont from "next/font/local";

// Gugi font configuration
export const gugi = localFont({
  src: "../../public/fonts/Gugi/Gugi-Regular.ttf",
  weight: "400",
  style: "normal",
  variable: "--font-gugi",
  display: "swap",
});
// Quicksand font configuration
export const quicksand = localFont({
    src: [
      {
        path: "../../public/fonts/Quicksand/Quicksand-Light.ttf",
        weight: "300",
        style: "normal",
      },
      {
        path: "../../public/fonts/Quicksand/Quicksand-Regular.ttf",
        weight: "400",
        style: "normal",
      },
      {
        path: "../../public/fonts/Quicksand/Quicksand-Medium.ttf",
        weight: "500",
        style: "normal",
      },
      {
        path: "../../public/fonts/Quicksand/Quicksand-SemiBold.ttf",
        weight: "600",
        style: "normal",
      },
      {
        path: "../../public/fonts/Quicksand/Quicksand-Bold.ttf",
        weight: "700",
        style: "normal",
      },
    ],
    variable: "--font-quicksand",
    display: "swap",
  });
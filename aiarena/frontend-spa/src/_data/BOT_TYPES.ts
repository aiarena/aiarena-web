import { getPublicPrefix } from "@/_lib/getPublicPrefix";

interface BOT_TYPE {
    name: string;
    image: string;
}

export const BOT_TYPES: Record<string, BOT_TYPE> = {
    PYTHON: { name: "Python", image: `${getPublicPrefix()}/programming_language_icons/python.svg` },
    JAVA: { name: "Java", image: `${getPublicPrefix()}/programming_language_icons/java.svg` },
    CPPLINUX: {
        name: "C++ (Linux)", image: `${getPublicPrefix()}/programming_language_icons/cpp.svg`
    },
    CPPWIN32: { name: "C++ (Windows)", image: `${getPublicPrefix()}/programming_language_icons/cpp.svg` },
    DOTNETCORE: { name: ".NET Core", image: `${getPublicPrefix()}/programming_language_icons/net.svg` },
    NODEJS: { name: "Node.JS", image: `${getPublicPrefix()}/programming_language_icons/nodejs_js.svg` },
};



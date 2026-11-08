// React
import React from "react";
import ReactDOM from "react-dom/client";

// Third Party
import i18n from "i18next";
import Backend from "i18next-http-backend";
import { initReactI18next } from "react-i18next";

// Styles
import "@/index.css";

import { AppName, ProjectName } from "@/constants";
import Routing from "@/Routing";
export { AppName, ProjectName };

// Read language directly from Django's LANGUAGE_CODE (set as lang="..." on root div)
const djangoLanguage =
    typeof document !== "undefined"
        ? document.getElementById(`${AppName}-root`)?.getAttribute("lang") ?? "en"
        : "en";

i18n
    .use(Backend)
    .use(initReactI18next)
    .init({
        lng: djangoLanguage,
        fallbackLng: "en",
        ns: ["translation"],
        defaultNS: "translation",
        // Untranslated strings are empty in the language files; show the English fallback instead.
        returnEmptyString: false,
        keySeparator: false,
        nsSeparator: false,
        interpolation: {
            escapeValue: false,
        },
        react: {
            useSuspense: false,
        },
        backend: {
            loadPath: `/static/${ProjectName}/i18n/{{lng}}/{{ns}}.json`,
        },
    });

const container =
    typeof document !== "undefined" ? document.getElementById(`${AppName}-root`) : null;

if (!container) {
    throw new Error("AA Killstats React mount point was not found.");
}

ReactDOM.createRoot(container).render(
    <React.StrictMode>
        <Routing />
    </React.StrictMode>,
);

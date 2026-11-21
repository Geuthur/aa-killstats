/* eslint-disable import-headings/import-headings -- the global index.css must load before the CSS modules */
// React
import React from "react";
import ReactDOM from "react-dom/client";

// Third Party
import { initI18n } from "aa-geuthur-react";

// Styles
import "@/index.css";

import { AppName, ProjectName } from "@/constants";
import Routing from "@/Routing";
export { AppName, ProjectName };

initI18n(ProjectName, `${AppName}-root`);

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

// React
import React from "react";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

// Third Party
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import i18n from "i18next";
import Backend from "i18next-http-backend";
import { NuqsAdapter } from "nuqs/adapters/react-router/v8";
import { initReactI18next } from "react-i18next";

// Styles
import "@/App.css";

import AuthBase from "@/Pages/Base";
import { KillboardPage } from "@/Pages/Killboard";
import { OverviewPage } from "@/Pages/OverviewPage";

const queryClient = new QueryClient();
export const AppName = "aa-killstats";
export const ProjectName = "killstats";

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

function App() {
    return (
        <React.StrictMode>
            <QueryClientProvider client={queryClient}>
                <BrowserRouter>
                    <NuqsAdapter>
                        <Routes>
                            <Route path={`/${ProjectName}/`} element={<AuthBase />}>
                                <Route index element={<KillboardPage />} />
                                <Route
                                    path="v2/corporation/:entityId/"
                                    element={<KillboardPage />}
                                />
                                <Route
                                    path="v2/alliance/:entityId/"
                                    element={<KillboardPage />}
                                />
                                <Route
                                    path="v2/:entityType/:entityId/"
                                    element={<KillboardPage />}
                                />
                                <Route
                                    path="corporation/:entityId/"
                                    element={<KillboardPage />}
                                />
                                <Route
                                    path="alliance/:entityId/"
                                    element={<KillboardPage />}
                                />
                                <Route
                                    path="overview/corporations/"
                                    element={<OverviewPage entityType="corporation" />}
                                />
                                <Route
                                    path="overview/alliances/"
                                    element={<OverviewPage entityType="alliance" />}
                                />
                                <Route
                                    path="corporation_admin/"
                                    element={<OverviewPage entityType="corporation" />}
                                />
                                <Route
                                    path="alliance_admin/"
                                    element={<OverviewPage entityType="alliance" />}
                                />
                                <Route
                                    path="v2/corporation_admin/"
                                    element={<OverviewPage entityType="corporation" />}
                                />
                                <Route
                                    path="v2/alliance_admin/"
                                    element={<OverviewPage entityType="alliance" />}
                                />
                                <Route
                                    path=":entityType/:entityId/"
                                    element={<KillboardPage />}
                                />
                                <Route path="*" element={<KillboardPage />} />
                            </Route>
                            <Route
                                path="*"
                                element={<Navigate to={`/${ProjectName}/`} replace />}
                            />
                        </Routes>
                    </NuqsAdapter>
                </BrowserRouter>
            </QueryClientProvider>
        </React.StrictMode>
    );
}

export default App;

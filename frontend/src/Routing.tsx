// React
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

// Third Party
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AaReactProvider, AuthBase } from "aa-geuthur-react";
import { NuqsAdapter } from "nuqs/adapters/react-router/v8";

import { AppName, ProjectName } from "@/constants";
import { KillboardPage } from "@/Pages/Killboard";
import { OverviewPage } from "@/Pages/Overview";

const queryClient = new QueryClient();

function Routing() {
    return (
        <AaReactProvider projectName={ProjectName} appName={AppName}>
            <QueryClientProvider client={queryClient}>
                <BrowserRouter>
                    <NuqsAdapter>
                        <Routes>
                            <Route path={`/${ProjectName}/`} element={<AuthBase fluidOnSmallScreens />}>
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
        </AaReactProvider>
    );
}

export default Routing;

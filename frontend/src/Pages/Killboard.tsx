// React
import { useLocation, useParams } from "react-router-dom";

// Third Party
import { FetchingLoader, useUserData } from "aa-geuthur-react";
import { useTranslation } from "react-i18next";

import KillboardSection from "@/Components/Sections/KillboardSection";
// AA Killstats
import { AppName } from "@/constants";

export function KillboardPage() {
    const { t } = useTranslation();
    const params = useParams();
    const location = useLocation();
    const rootEl =
        typeof document !== "undefined"
            ? document.getElementById(`${AppName}-root`)
            : null;

    const { data: userData, isLoading: isLoadingUser } = useUserData();

    let entityType: "corporation" | "alliance" | "character" = "corporation";
    if (
        location.pathname.includes("/alliance/") ||
        params.entityType === "alliance"
    ) {
        entityType = "alliance";
    } else if (
        location.pathname.includes("/corporation/") ||
        params.entityType === "corporation"
    ) {
        entityType = "corporation";
    } else if (
        location.pathname.includes("/character/") ||
        params.entityType === "character"

    ) {
        entityType = "character";
    } else {
        const rootType = rootEl?.getAttribute("data-entity-type");
        if (
            rootType === "alliance" ||
            rootType === "corporation" ||
            rootType === "character"
        ) {
            entityType = rootType;
        }
    }

    let entityId = 0;
    if (params.entityId) {
        const id = parseInt(params.entityId, 10);
        if (!isNaN(id) && id > 0) {
            entityId = id;
        }
    }

    if (!entityId && userData?.user) {
        if (entityType === "alliance" && userData.user.alliance_id) {
            entityId = userData.user.alliance_id;
        } else if (userData.user.corporation_id) {
            entityId = userData.user.corporation_id;
        }
    }

    if (!entityId) {
        entityId = parseInt(rootEl?.getAttribute("data-entity-id") || "0", 10);
    }

    if (!entityId && isLoadingUser) {
        return (
            <div
                className="w-100 rounded-4 border-killstats p-5 d-flex align-items-center justify-content-center"
                style={{ minHeight: 300 }}
            >
                <FetchingLoader message={t("Loading user data...")} />
            </div>
        );
    }

    return (
        <KillboardSection
            key={`${entityType}-${entityId}`}
            entityType={entityType}
            entityId={entityId}
        />
    );
}

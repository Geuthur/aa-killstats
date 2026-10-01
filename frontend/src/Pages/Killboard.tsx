// React
import { useLocation, useParams } from "react-router-dom";

// Third Party
import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";

// AA Killstats
import { loadUserData } from "@/Api/ApiCalls";
import { queryKeys } from "@/Api/query";
import { AppName } from "@/App";
import { FetchingLoader } from "@/Components/Loader";
import KillboardSection from "@/Components/Sections/KillboardSection";

export function KillboardPage() {
    const { t } = useTranslation();
    const params = useParams();
    const location = useLocation();
    const rootEl =
        typeof document !== "undefined"
            ? document.getElementById(`${AppName}-root`)
            : null;

    const { data: userData, isLoading: isLoadingUser } = useQuery({
        queryKey: queryKeys.User,
        queryFn: () => loadUserData(),
        staleTime: 5 * 60 * 1000,
    });

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
            <div className="w-full bg-gray-800/80 rounded-xl border-killstats p-12 flex items-center justify-center min-h-[300px]">
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

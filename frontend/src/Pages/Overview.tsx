import { OverViewSection } from "@/Components/Sections/OverViewSection";
import type { OverviewPageProps } from "@/Components/Sections/OverViewSection";

export function OverviewPage({ entityType }: OverviewPageProps) {
    return (
        <OverViewSection entityType={entityType} />
    );
}

export default OverviewPage;
